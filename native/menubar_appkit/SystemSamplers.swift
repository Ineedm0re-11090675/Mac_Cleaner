import Foundation
import IOKit.ps

struct DiskSample {
    let volumeName: String
    let totalBytes: Double
    let usedBytes: Double
    let freeBytes: Double
}

struct MemorySample {
    let totalBytes: Double
    let usedBytes: Double
    let availableBytes: Double
    let appBytes: Double
    let wiredBytes: Double
    let compressedBytes: Double
    let usagePercent: Double
}

struct BatterySample {
    let isAvailable: Bool
    let levelPercent: Int
    let stateText: String
    let detailText: String
}

struct NetworkSample {
    let interfaceName: String
    let downloadBytesPerSecond: Double
    let uploadBytesPerSecond: Double
}

struct SpeedTestSample {
    let interfaceName: String
    let downloadBytesPerSecond: Double
    let uploadBytesPerSecond: Double
    let baseRTTMilliseconds: Double?
}

enum SpeedTestError: LocalizedError {
    case unavailable
    case failed(String)
    case invalidResult

    var errorDescription: String? {
        switch self {
        case .unavailable:
            return "当前系统不可用 networkQuality。"
        case let .failed(message):
            return message
        case .invalidResult:
            return "测速结果无法解析。"
        }
    }
}

final class CPUSampler {
    private var previousTicks: (user: UInt64, system: UInt64, idle: UInt64, nice: UInt64)?
    private(set) var lastUsagePercent: Double = 0

    func sample() -> Double {
        var cpuInfo: processor_info_array_t?
        var cpuInfoCount: mach_msg_type_number_t = 0
        var cpuCount: natural_t = 0
        let result = host_processor_info(
            mach_host_self(),
            PROCESSOR_CPU_LOAD_INFO,
            &cpuCount,
            &cpuInfo,
            &cpuInfoCount
        )
        guard result == KERN_SUCCESS, let cpuInfo else {
            return lastUsagePercent
        }

        defer {
            let byteCount = vm_size_t(cpuInfoCount) * vm_size_t(MemoryLayout<integer_t>.stride)
            vm_deallocate(mach_task_self_, vm_address_t(bitPattern: cpuInfo), byteCount)
        }

        let stride = Int(CPU_STATE_MAX)
        var currentUser: UInt64 = 0
        var currentSystem: UInt64 = 0
        var currentIdle: UInt64 = 0
        var currentNice: UInt64 = 0

        for cpuIndex in 0..<Int(cpuCount) {
            let base = cpuIndex * stride
            currentUser += UInt64(cpuInfo[base + Int(CPU_STATE_USER)])
            currentSystem += UInt64(cpuInfo[base + Int(CPU_STATE_SYSTEM)])
            currentIdle += UInt64(cpuInfo[base + Int(CPU_STATE_IDLE)])
            currentNice += UInt64(cpuInfo[base + Int(CPU_STATE_NICE)])
        }

        let current = (user: currentUser, system: currentSystem, idle: currentIdle, nice: currentNice)
        defer { previousTicks = current }

        guard let previousTicks else {
            return lastUsagePercent
        }

        let userDelta = max(0, current.user - previousTicks.user)
        let systemDelta = max(0, current.system - previousTicks.system)
        let idleDelta = max(0, current.idle - previousTicks.idle)
        let niceDelta = max(0, current.nice - previousTicks.nice)
        let totalDelta = userDelta + systemDelta + idleDelta + niceDelta
        guard totalDelta > 0 else {
            return lastUsagePercent
        }

        lastUsagePercent = min(100.0, Double(userDelta + systemDelta + niceDelta) / Double(totalDelta) * 100.0)
        return lastUsagePercent
    }
}

final class MemorySampler {
    func sample() -> MemorySample? {
        var pageSize: vm_size_t = 0
        guard host_page_size(mach_host_self(), &pageSize) == KERN_SUCCESS else {
            return nil
        }

        var stats = vm_statistics64()
        var count = mach_msg_type_number_t(MemoryLayout<vm_statistics64>.stride / MemoryLayout<integer_t>.stride)
        let result = withUnsafeMutablePointer(to: &stats) { pointer in
            pointer.withMemoryRebound(to: integer_t.self, capacity: Int(count)) { reboundPointer in
                host_statistics64(mach_host_self(), HOST_VM_INFO64, reboundPointer, &count)
            }
        }
        guard result == KERN_SUCCESS else {
            return nil
        }

        let totalMemory = Double(readSysctlUInt64("hw.memsize"))
        guard totalMemory > 0 else {
            return nil
        }

        let freeBytes = Double(stats.free_count + stats.speculative_count) * Double(pageSize)
        let purgeableBytes = Double(stats.purgeable_count) * Double(pageSize)
        let appBytes = Double(stats.internal_page_count) * Double(pageSize)
        let wiredBytes = Double(stats.wire_count) * Double(pageSize)
        let compressedBytes = Double(stats.compressor_page_count) * Double(pageSize)
        let availableBytes = max(0, freeBytes + purgeableBytes)
        let usedBytes = min(totalMemory, max(0, appBytes + wiredBytes + compressedBytes))
        let usagePercent = min(100.0, usedBytes / totalMemory * 100.0)

        return MemorySample(
            totalBytes: totalMemory,
            usedBytes: usedBytes,
            availableBytes: availableBytes,
            appBytes: appBytes,
            wiredBytes: wiredBytes,
            compressedBytes: compressedBytes,
            usagePercent: usagePercent
        )
    }
}

final class DiskSampler {
    func sample() -> DiskSample? {
        let homePath = NSHomeDirectory()
        guard let attributes = try? FileManager.default.attributesOfFileSystem(forPath: homePath),
              let total = attributes[.systemSize] as? NSNumber,
              let free = attributes[.systemFreeSize] as? NSNumber else {
            return nil
        }
        let totalBytes = total.doubleValue
        let freeBytes = free.doubleValue
        let usedBytes = max(0, totalBytes - freeBytes)
        let volumeURL = URL(fileURLWithPath: homePath)
        let volumeName = (try? volumeURL.resourceValues(forKeys: [.volumeLocalizedNameKey]).volumeLocalizedName)
            ?? "Macintosh HD"
        return DiskSample(volumeName: volumeName, totalBytes: totalBytes, usedBytes: usedBytes, freeBytes: freeBytes)
    }
}

final class BatterySampler {
    func sample() -> BatterySample {
        guard let info = IOPSCopyPowerSourcesInfo()?.takeRetainedValue(),
              let sources = IOPSCopyPowerSourcesList(info)?.takeRetainedValue() as? [CFTypeRef],
              !sources.isEmpty else {
            return BatterySample(
                isAvailable: false,
                levelPercent: 0,
                stateText: "当前设备无电池",
                detailText: "正在使用交流电"
            )
        }

        for source in sources {
            guard let description = IOPSGetPowerSourceDescription(info, source)?.takeUnretainedValue() as? [String: Any] else {
                continue
            }
            guard let current = description[kIOPSCurrentCapacityKey as String] as? Int,
                  let max = description[kIOPSMaxCapacityKey as String] as? Int,
                  max > 0 else {
                continue
            }

            let level = Int((Double(current) / Double(max) * 100.0).rounded())
            let isCharging = (description[kIOPSIsChargingKey as String] as? Bool) ?? false
            let isCharged = (description[kIOPSIsChargedKey as String] as? Bool) ?? false
            let powerState = description[kIOPSPowerSourceStateKey as String] as? String ?? ""
            let timeToEmpty = description[kIOPSTimeToEmptyKey as String] as? Int ?? -1
            let timeToFull = description[kIOPSTimeToFullChargeKey as String] as? Int ?? -1

            let stateText: String
            if isCharged {
                stateText = "已充满"
            } else if isCharging {
                stateText = timeToFull > 0 ? "充电中，约 \(timeToFull) 分钟充满" : "充电中"
            } else if powerState == kIOPSBatteryPowerValue {
                stateText = timeToEmpty > 0 ? "使用电池，约 \(timeToEmpty) 分钟剩余" : "使用电池"
            } else {
                stateText = "正在使用交流电"
            }

            let detailText: String
            if isCharged {
                detailText = "已连接电源"
            } else if isCharging {
                detailText = "电量恢复中"
            } else {
                detailText = "未连接充电器"
            }

            return BatterySample(isAvailable: true, levelPercent: level, stateText: stateText, detailText: detailText)
        }

        return BatterySample(
            isAvailable: false,
            levelPercent: 0,
            stateText: "暂未检测到电池",
            detailText: "请稍后重试"
        )
    }
}

final class NetworkSampler {
    private var previousCounters: [String: (incoming: UInt64, outgoing: UInt64)] = [:]
    private var previousDate: Date?
    private(set) var lastSample = NetworkSample(interfaceName: "等待采样", downloadBytesPerSecond: 0, uploadBytesPerSecond: 0)

    func sample() -> NetworkSample {
        var pointer: UnsafeMutablePointer<ifaddrs>?
        guard getifaddrs(&pointer) == 0, let first = pointer else {
            return lastSample
        }
        defer { freeifaddrs(pointer) }

        var counters: [String: (incoming: UInt64, outgoing: UInt64)] = [:]
        var current = first
        while true {
            let interface = current.pointee
            let flags = Int32(interface.ifa_flags)
            if let addr = interface.ifa_addr,
               addr.pointee.sa_family == UInt8(AF_LINK),
               (flags & IFF_UP) != 0,
               (flags & IFF_LOOPBACK) == 0,
               let dataPointer = interface.ifa_data?.assumingMemoryBound(to: if_data.self) {
                let name = String(cString: interface.ifa_name)
                counters[name] = (incoming: UInt64(dataPointer.pointee.ifi_ibytes), outgoing: UInt64(dataPointer.pointee.ifi_obytes))
            }

            guard let next = interface.ifa_next else {
                break
            }
            current = next
        }

        let now = Date()
        defer {
            previousCounters = counters
            previousDate = now
        }

        guard let previousDate else {
            return lastSample
        }
        let interval = max(0.5, now.timeIntervalSince(previousDate))

        var totalIncoming: UInt64 = 0
        var totalOutgoing: UInt64 = 0
        var primaryInterface = "网络空闲"
        var highestDelta: UInt64 = 0

        for (name, currentValues) in counters {
            let previous = previousCounters[name] ?? currentValues
            let incomingDelta = currentValues.incoming >= previous.incoming ? currentValues.incoming - previous.incoming : 0
            let outgoingDelta = currentValues.outgoing >= previous.outgoing ? currentValues.outgoing - previous.outgoing : 0
            let totalDelta = incomingDelta + outgoingDelta

            totalIncoming += incomingDelta
            totalOutgoing += outgoingDelta
            if totalDelta >= highestDelta {
                highestDelta = totalDelta
                primaryInterface = labelForInterface(name)
            }
        }

        lastSample = NetworkSample(
            interfaceName: primaryInterface,
            downloadBytesPerSecond: Double(totalIncoming) / interval,
            uploadBytesPerSecond: Double(totalOutgoing) / interval
        )
        return lastSample
    }

    private func labelForInterface(_ rawName: String) -> String {
        if rawName.hasPrefix("en") {
            return "接口 \(rawName)"
        }
        if rawName.hasPrefix("bridge") {
            return "桥接 \(rawName)"
        }
        if rawName.hasPrefix("utun") {
            return "VPN \(rawName)"
        }
        return rawName
    }
}

final class SpeedTestRunner {
    private var process: Process?

    var isRunning: Bool {
        process != nil
    }

    func run(completion: @escaping (Result<SpeedTestSample, Error>) -> Void) {
        guard process == nil else {
            completion(.failure(SpeedTestError.failed("测速已经在进行中。")))
            return
        }
        let executable = "/usr/bin/networkQuality"
        guard FileManager.default.isExecutableFile(atPath: executable) else {
            completion(.failure(SpeedTestError.unavailable))
            return
        }

        let process = Process()
        let output = Pipe()
        let error = Pipe()
        process.executableURL = URL(fileURLWithPath: executable)
        process.arguments = ["-c"]
        process.standardOutput = output
        process.standardError = error
        process.terminationHandler = { [weak self] finishedProcess in
            let stdout = output.fileHandleForReading.readDataToEndOfFile()
            let stderr = error.fileHandleForReading.readDataToEndOfFile()
            defer { self?.process = nil }

            if finishedProcess.terminationStatus != 0 {
                let message = String(data: stderr, encoding: .utf8)?.trimmingCharacters(in: .whitespacesAndNewlines)
                completion(.failure(SpeedTestError.failed(message?.isEmpty == false ? message! : "测速命令执行失败。")))
                return
            }

            guard let sample = Self.parseSample(from: stdout) else {
                completion(.failure(SpeedTestError.invalidResult))
                return
            }
            completion(.success(sample))
        }

        do {
            try process.run()
            self.process = process
        } catch {
            self.process = nil
            completion(.failure(error))
        }
    }

    private static func parseSample(from data: Data) -> SpeedTestSample? {
        guard let jsonObject = try? JSONSerialization.jsonObject(with: data) as? [String: Any] else {
            return nil
        }
        let download = (jsonObject["dl_throughput"] as? NSNumber)?.doubleValue ?? 0
        let upload = (jsonObject["ul_throughput"] as? NSNumber)?.doubleValue ?? 0
        let interfaceName = (jsonObject["interface_name"] as? String) ?? "默认接口"
        let baseRTT = (jsonObject["base_rtt"] as? NSNumber)?.doubleValue
        return SpeedTestSample(
            interfaceName: interfaceName,
            downloadBytesPerSecond: download,
            uploadBytesPerSecond: upload,
            baseRTTMilliseconds: baseRTT
        )
    }
}

private func readSysctlUInt64(_ name: String) -> UInt64 {
    var value: UInt64 = 0
    var size = MemoryLayout<UInt64>.size
    let result = name.withCString { cname in
        sysctlbyname(cname, &value, &size, nil, 0)
    }
    return result == 0 ? value : 0
}
