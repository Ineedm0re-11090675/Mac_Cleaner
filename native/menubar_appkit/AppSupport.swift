import AppKit
import Darwin
import Foundation

let appName = "macOS Cleaner"
let runtimeDir = FileManager.default.homeDirectoryForCurrentUser
    .appendingPathComponent("Library/Application Support/\(appName)/runtime", isDirectory: true)
let commandsDir = runtimeDir.appendingPathComponent("commands", isDirectory: true)
let helperLogPath = URL(fileURLWithPath: "/tmp/macos_cleaner_tray_helper.log")
let helperLockPath = runtimeDir.appendingPathComponent("tray-helper.lock")

enum HelperAction: String {
    case openMain = "open_main"
    case openDashboard = "open_dashboard"
    case quickCache = "quick_cache"
    case quickMemory = "quick_memory"
    case hideMain = "hide_main"
    case quitMain = "quit_main"
}

func appendHelperLog(_ message: String) {
    let timestamp = ISO8601DateFormatter().string(from: Date())
    let line = "[\(timestamp)] \(message)\n"
    let data = Data(line.utf8)
    let manager = FileManager.default
    if !manager.fileExists(atPath: helperLogPath.path) {
        try? data.write(to: helperLogPath)
        return
    }
    guard let handle = try? FileHandle(forWritingTo: helperLogPath) else {
        return
    }
    defer { try? handle.close() }
    _ = try? handle.seekToEnd()
    try? handle.write(contentsOf: data)
}

func ensureRuntimeDirs() {
    try? FileManager.default.createDirectory(at: commandsDir, withIntermediateDirectories: true)
}

func writeCommand(action: HelperAction) {
    ensureRuntimeDirs()
    let formatter = ISO8601DateFormatter()
    formatter.formatOptions = [.withInternetDateTime]
    let createdAt = formatter.string(from: Date())
    let id = UUID().uuidString.replacingOccurrences(of: "-", with: "").lowercased()
    let payload: [String: Any] = [
        "id": id,
        "action": action.rawValue,
        "payload": [:],
        "created_at": createdAt,
        "pid": Int(getpid()),
    ]
    guard let data = try? JSONSerialization.data(withJSONObject: payload, options: []) else {
        appendHelperLog("failed to serialize command \(action.rawValue)")
        return
    }
    let filenameBase = "\(createdAt.replacingOccurrences(of: ":", with: "-"))-\(id)"
    let tempURL = commandsDir.appendingPathComponent("\(filenameBase).tmp")
    let finalURL = commandsDir.appendingPathComponent("\(filenameBase).json")
    do {
        try data.write(to: tempURL, options: .atomic)
        try FileManager.default.moveItem(at: tempURL, to: finalURL)
        appendHelperLog("queued command \(action.rawValue): \(finalURL.lastPathComponent)")
    } catch {
        try? FileManager.default.removeItem(at: tempURL)
        appendHelperLog("failed to write command \(action.rawValue): \(error.localizedDescription)")
    }
}

func parentIsAlive(_ pid: pid_t) -> Bool {
    if pid <= 0 {
        return true
    }
    if kill(pid, 0) == 0 {
        return true
    }
    return errno == EPERM
}

func acquireSingletonLock() -> Int32? {
    ensureRuntimeDirs()
    let fd = open(helperLockPath.path, O_CREAT | O_RDWR, S_IRUSR | S_IWUSR)
    if fd < 0 {
        appendHelperLog("failed to open lock file")
        return nil
    }
    if flock(fd, LOCK_EX | LOCK_NB) != 0 {
        appendHelperLog("another native helper instance is already running; exiting")
        close(fd)
        return nil
    }
    let pidText = "\(getpid())\n"
    _ = ftruncate(fd, 0)
    pidText.withCString { ptr in
        _ = write(fd, ptr, strlen(ptr))
    }
    return fd
}

func parseArgument(named name: String) -> String? {
    let args = CommandLine.arguments
    guard let index = args.firstIndex(of: name), args.indices.contains(index + 1) else {
        return nil
    }
    return args[index + 1]
}

func makeStatusIcon() -> NSImage {
    let canvas = NSSize(width: 18, height: 18)
    let image = NSImage(size: canvas)
    image.lockFocus()

    NSColor.clear.setFill()
    NSRect(origin: .zero, size: canvas).fill()

    let roundedRect = NSBezierPath(roundedRect: NSRect(x: 1, y: 1, width: 16, height: 16), xRadius: 5, yRadius: 5)
    NSColor(calibratedWhite: 1.0, alpha: 0.98).setFill()
    roundedRect.fill()
    NSColor(calibratedWhite: 0.05, alpha: 0.18).setStroke()
    roundedRect.lineWidth = 1.0
    roundedRect.stroke()

    let paragraph = NSMutableParagraphStyle()
    paragraph.alignment = .center
    let attributes: [NSAttributedString.Key: Any] = [
        .font: NSFont.boldSystemFont(ofSize: 8.5),
        .foregroundColor: NSColor(calibratedWhite: 0.06, alpha: 1.0),
        .paragraphStyle: paragraph,
    ]
    let label = NSString(string: "MC")
    label.draw(
        in: NSRect(x: 0, y: 4.3, width: canvas.width, height: 9),
        withAttributes: attributes
    )

    image.unlockFocus()
    return image
}

func formatBytes(_ value: Double) -> String {
    let units = ["B", "KB", "MB", "GB", "TB"]
    var size = max(0, value)
    var index = 0
    while size >= 1024.0 && index < units.count - 1 {
        size /= 1024.0
        index += 1
    }
    return String(format: size >= 10 || index == 0 ? "%.0f %@" : "%.2f %@", size, units[index])
}

func formatRate(_ value: Double) -> String {
    "\(formatBytes(value))/s"
}

func formatPercent(_ value: Double, digits: Int = 0) -> String {
    String(format: "%.\(digits)f%%", max(0, value))
}

func formatClock(_ date: Date?) -> String {
    guard let date else {
        return "等待首次采样"
    }
    let formatter = DateFormatter()
    formatter.dateFormat = "HH:mm:ss"
    return formatter.string(from: date)
}

func safeMainActor(_ work: @escaping () -> Void) {
    DispatchQueue.main.async(execute: work)
}
