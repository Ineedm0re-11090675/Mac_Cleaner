import AppKit
import SwiftUI

struct MenuBarSnapshot {
    var updatedAt: Date?
    var healthScore: Int
    var healthLabel: String
    var healthSummary: String

    var diskValue: String
    var diskDetail: String
    var diskFootnote: String

    var memoryValue: String
    var memoryDetail: String
    var memoryFootnote: String

    var batteryValue: String
    var batteryDetail: String
    var batteryFootnote: String

    var cpuValue: String
    var cpuDetail: String
    var cpuFootnote: String

    var networkValue: String
    var networkDetail: String
    var networkFootnote: String

    static let placeholder = MenuBarSnapshot(
        updatedAt: nil,
        healthScore: 85,
        healthLabel: "良好",
        healthSummary: "正在准备菜单栏监控面板。",
        diskValue: "--",
        diskDetail: "磁盘信息加载中",
        diskFootnote: "",
        memoryValue: "--",
        memoryDetail: "内存信息加载中",
        memoryFootnote: "",
        batteryValue: "--",
        batteryDetail: "电池信息加载中",
        batteryFootnote: "",
        cpuValue: "--",
        cpuDetail: "CPU 采样准备中",
        cpuFootnote: "",
        networkValue: "↓ --\n↑ --",
        networkDetail: "网络采样准备中",
        networkFootnote: ""
    )
}

enum SpeedTestDisplayState {
    case idle
    case running
    case finished(primary: String, detail: String, footnote: String)
    case failed(message: String)
}

@MainActor
final class MenuBarViewModel: ObservableObject {
    @Published var snapshot = MenuBarSnapshot.placeholder
    @Published var speedTestState: SpeedTestDisplayState = .idle

    private let cpuSampler = CPUSampler()
    private let memorySampler = MemorySampler()
    private let diskSampler = DiskSampler()
    private let batterySampler = BatterySampler()
    private let networkSampler = NetworkSampler()
    private let speedTestRunner = SpeedTestRunner()

    private let actionHandler: (HelperAction) -> Void
    private let closeHandler: () -> Void
    private var refreshTimer: Timer?
    private var refreshTick = 0

    private var cachedDisk: DiskSample?
    private var cachedMemory: MemorySample?
    private var cachedBattery = BatterySample(isAvailable: false, levelPercent: 0, stateText: "等待采样", detailText: "")
    private var cachedNetwork = NetworkSample(interfaceName: "等待采样", downloadBytesPerSecond: 0, uploadBytesPerSecond: 0)
    private var lastCPUPercent: Double = 0

    init(actionHandler: @escaping (HelperAction) -> Void, closeHandler: @escaping () -> Void) {
        self.actionHandler = actionHandler
        self.closeHandler = closeHandler
    }

    func panelDidOpen() {
        refreshNow(forceStatic: true)
        guard refreshTimer == nil else {
            return
        }
        refreshTimer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { [weak self] _ in
            Task { @MainActor [weak self] in
                self?.refreshNow()
            }
        }
    }

    func panelDidClose() {
        refreshTimer?.invalidate()
        refreshTimer = nil
    }

    func perform(_ action: HelperAction) {
        actionHandler(action)
        closeHandler()
    }

    func startSpeedTest() {
        guard !speedTestRunner.isRunning else {
            return
        }
        speedTestState = .running
        speedTestRunner.run { [weak self] result in
            safeMainActor {
                guard let self else { return }
                switch result {
                case let .success(sample):
                    let primary = "↓ \(formatRate(sample.downloadBytesPerSecond))\n↑ \(formatRate(sample.uploadBytesPerSecond))"
                    let detail: String
                    if let rtt = sample.baseRTTMilliseconds {
                        detail = "\(sample.interfaceName) · RTT \(String(format: "%.0f ms", rtt))"
                    } else {
                        detail = sample.interfaceName
                    }
                    self.speedTestState = .finished(
                        primary: primary,
                        detail: detail,
                        footnote: "结果来自 system networkQuality"
                    )
                case let .failure(error):
                    self.speedTestState = .failed(message: error.localizedDescription)
                }
            }
        }
    }

    private func refreshNow(forceStatic: Bool = false) {
        refreshTick += 1

        let cpuPercent = cpuSampler.sample()
        let memory = memorySampler.sample() ?? cachedMemory
        let disk = (forceStatic || refreshTick == 1 || refreshTick % 10 == 0) ? diskSampler.sample() ?? cachedDisk : cachedDisk
        let battery = (forceStatic || refreshTick == 1 || refreshTick % 30 == 0) ? batterySampler.sample() : cachedBattery
        let network = networkSampler.sample()

        if let memory {
            cachedMemory = memory
        }
        if let disk {
            cachedDisk = disk
        }
        cachedBattery = battery
        cachedNetwork = network
        lastCPUPercent = cpuPercent

        snapshot = buildSnapshot(cpuPercent: cpuPercent, memory: memory, disk: disk, battery: battery, network: network)
    }

    private func buildSnapshot(
        cpuPercent: Double,
        memory: MemorySample?,
        disk: DiskSample?,
        battery: BatterySample,
        network: NetworkSample
    ) -> MenuBarSnapshot {
        let memoryUsage = memory?.usagePercent ?? 0
        let diskFreePercent = disk.map { $0.totalBytes > 0 ? $0.freeBytes / $0.totalBytes * 100.0 : 100.0 } ?? 100.0
        let batteryPenalty = battery.isAvailable && battery.levelPercent < 20 ? 10 : 0
        let diskPenalty = diskFreePercent < 10 ? 25 : (diskFreePercent < 20 ? 12 : 0)
        let memoryPenalty = memoryUsage > 85 ? 22 : (memoryUsage > 70 ? 12 : 0)
        let cpuPenalty = cpuPercent > 85 ? 15 : (cpuPercent > 65 ? 8 : 0)
        let networkBusyPenalty = (network.downloadBytesPerSecond + network.uploadBytesPerSecond) > 100 * 1024 * 1024 ? 5 : 0
        let score = max(0, min(100, 100 - batteryPenalty - diskPenalty - memoryPenalty - cpuPenalty - networkBusyPenalty))

        let healthLabel: String
        switch score {
        case 80...:
            healthLabel = "良好"
        case 60...:
            healthLabel = "注意"
        default:
            healthLabel = "需要处理"
        }

        let healthSummary = buildHealthSummary(cpuPercent: cpuPercent, memoryUsage: memoryUsage, diskFreePercent: diskFreePercent, battery: battery)

        let diskValue = disk.map { formatBytes($0.freeBytes) } ?? "--"
        let diskDetail = disk.map { "\($0.volumeName) 可用" } ?? "磁盘信息暂不可用"
        let diskFootnote = disk.map { "已用 \(formatBytes($0.usedBytes)) / 总共 \(formatBytes($0.totalBytes))" } ?? ""

        let memoryValue = memory.map { formatPercent($0.usagePercent) } ?? "--"
        let memoryDetail = memory.map { "\(formatBytes($0.usedBytes)) / \(formatBytes($0.totalBytes))" } ?? "内存信息暂不可用"
        let memoryFootnote = memory.map {
            "App \(formatBytes($0.appBytes)) · Wired \(formatBytes($0.wiredBytes)) · 压缩 \(formatBytes($0.compressedBytes))"
        } ?? ""

        let batteryValue = battery.isAvailable ? "\(battery.levelPercent)%" : "--"
        let batteryDetail = battery.stateText
        let batteryFootnote = battery.detailText

        let cpuValue = formatPercent(cpuPercent)
        let cpuDetail = "当前总占用"
        let cpuFootnote = cpuPercent > 0 ? "近 1 秒总处理器占用" : "正在等待稳定采样"

        let networkValue = "↓ \(formatRate(network.downloadBytesPerSecond))\n↑ \(formatRate(network.uploadBytesPerSecond))"
        let networkDetail = network.interfaceName
        let networkFootnote = "实时接口吞吐"

        return MenuBarSnapshot(
            updatedAt: Date(),
            healthScore: score,
            healthLabel: healthLabel,
            healthSummary: healthSummary,
            diskValue: diskValue,
            diskDetail: diskDetail,
            diskFootnote: diskFootnote,
            memoryValue: memoryValue,
            memoryDetail: memoryDetail,
            memoryFootnote: memoryFootnote,
            batteryValue: batteryValue,
            batteryDetail: batteryDetail,
            batteryFootnote: batteryFootnote,
            cpuValue: cpuValue,
            cpuDetail: cpuDetail,
            cpuFootnote: cpuFootnote,
            networkValue: networkValue,
            networkDetail: networkDetail,
            networkFootnote: networkFootnote
        )
    }

    private func buildHealthSummary(cpuPercent: Double, memoryUsage: Double, diskFreePercent: Double, battery: BatterySample) -> String {
        var parts: [String] = []
        parts.append(cpuPercent > 70 ? "CPU 当前偏高" : "CPU 平稳")
        parts.append(memoryUsage > 75 ? "内存占用偏高" : "内存占用正常")
        parts.append(diskFreePercent < 15 ? "磁盘空间偏紧" : "磁盘可用空间正常")
        if battery.isAvailable {
            parts.append(battery.levelPercent < 20 ? "电池偏低" : "电池状态正常")
        }
        return parts.joined(separator: "，")
    }
}

struct MenuBarContentView: View {
    @ObservedObject var viewModel: MenuBarViewModel

    private let columns = [
        GridItem(.flexible(), spacing: 12),
        GridItem(.flexible(), spacing: 12),
    ]

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            headerSection

            LazyVGrid(columns: columns, spacing: 12) {
                MetricCardView(
                    title: "磁盘",
                    primary: viewModel.snapshot.diskValue,
                    detail: viewModel.snapshot.diskDetail,
                    footnote: viewModel.snapshot.diskFootnote,
                    accent: Color.blue,
                    actionTitle: "释放"
                ) {
                    viewModel.perform(.quickCache)
                }

                MetricCardView(
                    title: "内存",
                    primary: viewModel.snapshot.memoryValue,
                    detail: viewModel.snapshot.memoryDetail,
                    footnote: viewModel.snapshot.memoryFootnote,
                    accent: Color.mint,
                    actionTitle: "优化"
                ) {
                    viewModel.perform(.quickMemory)
                }

                MetricCardView(
                    title: "电池",
                    primary: viewModel.snapshot.batteryValue,
                    detail: viewModel.snapshot.batteryDetail,
                    footnote: viewModel.snapshot.batteryFootnote,
                    accent: Color.green,
                    actionTitle: nil,
                    action: nil
                )

                MetricCardView(
                    title: "CPU",
                    primary: viewModel.snapshot.cpuValue,
                    detail: viewModel.snapshot.cpuDetail,
                    footnote: viewModel.snapshot.cpuFootnote,
                    accent: Color.orange,
                    actionTitle: nil,
                    action: nil
                )

                MetricCardView(
                    title: "网络",
                    primary: viewModel.snapshot.networkValue,
                    detail: viewModel.snapshot.networkDetail,
                    footnote: viewModel.snapshot.networkFootnote,
                    accent: Color.cyan,
                    actionTitle: nil,
                    action: nil
                )

                SpeedTestCardView(viewModel: viewModel)
            }

            quickActionSection
        }
        .padding(14)
        .frame(width: 408)
        .background(
            LinearGradient(
                colors: [
                    Color(nsColor: NSColor(calibratedRed: 0.16, green: 0.08, blue: 0.37, alpha: 1.0)),
                    Color(nsColor: NSColor(calibratedRed: 0.22, green: 0.09, blue: 0.40, alpha: 1.0)),
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        )
    }

    private var headerSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack(alignment: .center) {
                Text("Mac 健康度")
                    .font(.system(size: 16, weight: .semibold))
                    .foregroundStyle(.white.opacity(0.94))
                Text(viewModel.snapshot.healthLabel)
                    .font(.system(size: 18, weight: .bold))
                    .foregroundStyle(healthColor)
                Spacer(minLength: 8)
                Text("更新 \(formatClock(viewModel.snapshot.updatedAt))")
                    .font(.system(size: 11, weight: .medium))
                    .foregroundStyle(.white.opacity(0.68))
            }

            Text(viewModel.snapshot.healthSummary)
                .font(.system(size: 13, weight: .medium))
                .foregroundStyle(.white.opacity(0.84))
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding(14)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.white.opacity(0.08))
        .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
    }

    private var quickActionSection: some View {
        VStack(spacing: 10) {
            HStack(spacing: 10) {
                ActionButton(title: "打开主窗口", accent: .white.opacity(0.12)) {
                    viewModel.perform(.openMain)
                }
                ActionButton(title: "打开仪表盘", accent: .white.opacity(0.12)) {
                    viewModel.perform(.openDashboard)
                }
            }

            HStack(spacing: 10) {
                ActionButton(title: "隐藏", accent: .white.opacity(0.08)) {
                    viewModel.perform(.hideMain)
                }
                ActionButton(title: "退出", accent: Color.red.opacity(0.24)) {
                    viewModel.perform(.quitMain)
                }
            }
        }
    }

    private var healthColor: Color {
        switch viewModel.snapshot.healthScore {
        case 80...:
            return Color.green
        case 60...:
            return Color.yellow
        default:
            return Color.red
        }
    }
}

private struct MetricCardView: View {
    let title: String
    let primary: String
    let detail: String
    let footnote: String
    let accent: Color
    let actionTitle: String?
    let action: (() -> Void)?

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack {
                Text(title)
                    .font(.system(size: 13, weight: .semibold))
                    .foregroundStyle(.white.opacity(0.9))
                Spacer(minLength: 8)
                Circle()
                    .fill(accent)
                    .frame(width: 8, height: 8)
            }

            Text(primary)
                .font(.system(size: primary.contains("\n") ? 18 : 26, weight: .bold))
                .foregroundStyle(.white)
                .fixedSize(horizontal: false, vertical: true)

            Text(detail)
                .font(.system(size: 13, weight: .medium))
                .foregroundStyle(.white.opacity(0.84))
                .fixedSize(horizontal: false, vertical: true)

            if !footnote.isEmpty {
                Text(footnote)
                    .font(.system(size: 11, weight: .regular))
                    .foregroundStyle(.white.opacity(0.62))
                    .fixedSize(horizontal: false, vertical: true)
            }

            Spacer(minLength: 0)

            if let actionTitle, let action {
                Button(actionTitle, action: action)
                    .buttonStyle(CardActionButtonStyle())
            }
        }
        .padding(14)
        .frame(maxWidth: .infinity, minHeight: 148, alignment: .topLeading)
        .background(Color.white.opacity(0.10))
        .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
    }
}

private struct SpeedTestCardView: View {
    @ObservedObject var viewModel: MenuBarViewModel

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack {
                Text("网速测试")
                    .font(.system(size: 13, weight: .semibold))
                    .foregroundStyle(.white.opacity(0.9))
                Spacer(minLength: 8)
                Circle()
                    .fill(Color.pink)
                    .frame(width: 8, height: 8)
            }

            switch viewModel.speedTestState {
            case .idle:
                Text("尚未测速")
                    .font(.system(size: 24, weight: .bold))
                    .foregroundStyle(.white)
                Text("点击下方按钮执行系统 networkQuality 测速。")
                    .font(.system(size: 13, weight: .medium))
                    .foregroundStyle(.white.opacity(0.84))
                Spacer(minLength: 0)
                Button("测试速度") {
                    viewModel.startSpeedTest()
                }
                .buttonStyle(CardActionButtonStyle())

            case .running:
                ProgressView()
                    .progressViewStyle(.circular)
                    .tint(.white)
                Text("测速中...")
                    .font(.system(size: 22, weight: .bold))
                    .foregroundStyle(.white)
                Text("这一步会调用系统测速命令，通常需要十几秒。")
                    .font(.system(size: 13, weight: .medium))
                    .foregroundStyle(.white.opacity(0.84))
                Spacer(minLength: 0)

            case let .finished(primary, detail, footnote):
                Text(primary)
                    .font(.system(size: 18, weight: .bold))
                    .foregroundStyle(.white)
                    .fixedSize(horizontal: false, vertical: true)
                Text(detail)
                    .font(.system(size: 13, weight: .medium))
                    .foregroundStyle(.white.opacity(0.84))
                Text(footnote)
                    .font(.system(size: 11, weight: .regular))
                    .foregroundStyle(.white.opacity(0.62))
                Spacer(minLength: 0)
                Button("重新测速") {
                    viewModel.startSpeedTest()
                }
                .buttonStyle(CardActionButtonStyle())

            case let .failed(message):
                Text("测速失败")
                    .font(.system(size: 22, weight: .bold))
                    .foregroundStyle(.white)
                Text(message)
                    .font(.system(size: 13, weight: .medium))
                    .foregroundStyle(.white.opacity(0.84))
                    .fixedSize(horizontal: false, vertical: true)
                Spacer(minLength: 0)
                Button("重试") {
                    viewModel.startSpeedTest()
                }
                .buttonStyle(CardActionButtonStyle())
            }
        }
        .padding(14)
        .frame(maxWidth: .infinity, minHeight: 148, alignment: .topLeading)
        .background(Color.white.opacity(0.10))
        .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
    }
}

private struct ActionButton: View {
    let title: String
    let accent: Color
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            Text(title)
                .font(.system(size: 13, weight: .semibold))
                .foregroundStyle(.white)
                .frame(maxWidth: .infinity)
                .padding(.vertical, 11)
                .background(accent)
                .clipShape(RoundedRectangle(cornerRadius: 12, style: .continuous))
        }
        .buttonStyle(.plain)
    }
}

private struct CardActionButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .font(.system(size: 12, weight: .semibold))
            .foregroundStyle(.white)
            .padding(.vertical, 8)
            .padding(.horizontal, 12)
            .background(Color.white.opacity(configuration.isPressed ? 0.24 : 0.16))
            .clipShape(RoundedRectangle(cornerRadius: 10, style: .continuous))
    }
}
