import AppKit
import Darwin
import Foundation

private let appName = "macOS Cleaner"
private let runtimeDir = FileManager.default.homeDirectoryForCurrentUser
    .appendingPathComponent("Library/Application Support/\(appName)/runtime", isDirectory: true)
private let commandsDir = runtimeDir.appendingPathComponent("commands", isDirectory: true)
private let helperLogPath = URL(fileURLWithPath: "/tmp/macos_cleaner_tray_helper.log")
private let helperLockPath = runtimeDir.appendingPathComponent("tray-helper.lock")

private enum HelperAction: String {
    case openMain = "open_main"
    case openDashboard = "open_dashboard"
    case quickCache = "quick_cache"
    case quickMemory = "quick_memory"
    case hideMain = "hide_main"
    case quitMain = "quit_main"
}

private func appendHelperLog(_ message: String) {
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

private func ensureRuntimeDirs() {
    try? FileManager.default.createDirectory(at: commandsDir, withIntermediateDirectories: true)
}

private func writeCommand(action: HelperAction) {
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

private func parentIsAlive(_ pid: pid_t) -> Bool {
    if pid <= 0 {
        return true
    }
    if kill(pid, 0) == 0 {
        return true
    }
    return errno == EPERM
}

private func acquireSingletonLock() -> Int32? {
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

private func makeStatusIcon() -> NSImage {
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

final class AppDelegate: NSObject, NSApplicationDelegate {
    private var statusItem: NSStatusItem?
    private var lockFileDescriptor: Int32 = -1
    private var parentTimer: Timer?
    private var parentPID: pid_t = 0
    private var mainAppPath: String = ""

    func configure(parentPID: pid_t, mainAppPath: String) {
        self.parentPID = parentPID
        self.mainAppPath = mainAppPath
    }

    func applicationDidFinishLaunching(_ notification: Notification) {
        guard let fd = acquireSingletonLock() else {
            NSApp.terminate(nil)
            return
        }
        lockFileDescriptor = fd
        installStatusItem()
        parentTimer = Timer.scheduledTimer(withTimeInterval: 2.0, repeats: true) { [weak self] _ in
            guard let self else { return }
            if !parentIsAlive(self.parentPID) {
                appendHelperLog("parent pid is gone; exiting native helper")
                NSApp.terminate(nil)
            }
        }
        appendHelperLog("native menu helper started successfully")
    }

    func applicationWillTerminate(_ notification: Notification) {
        parentTimer?.invalidate()
        if lockFileDescriptor >= 0 {
            close(lockFileDescriptor)
            lockFileDescriptor = -1
        }
    }

    private func installStatusItem() {
        statusItem = NSStatusBar.system.statusItem(withLength: NSStatusItem.squareLength)
        guard let statusItem else {
            appendHelperLog("failed to create status item")
            return
        }
        if let button = statusItem.button {
            button.title = ""
            button.toolTip = appName
            button.image = makeStatusIcon()
            button.imagePosition = .imageOnly
        }

        let menu = NSMenu(title: appName)
        menu.addItem(makeMenuItem(title: "打开主窗口", action: #selector(openMain)))
        menu.addItem(makeMenuItem(title: "打开仪表盘", action: #selector(openDashboard)))
        menu.addItem(.separator())
        menu.addItem(makeMenuItem(title: "一键清理缓存", action: #selector(quickCache)))
        menu.addItem(makeMenuItem(title: "一键释放可回收内存", action: #selector(quickMemory)))
        menu.addItem(.separator())
        menu.addItem(makeMenuItem(title: "隐藏窗口", action: #selector(hideMain)))
        menu.addItem(.separator())
        menu.addItem(makeMenuItem(title: "退出", action: #selector(quitMain)))
        statusItem.menu = menu
        appendHelperLog("native AppKit status item installed successfully")
    }

    private func makeMenuItem(title: String, action: Selector) -> NSMenuItem {
        let item = NSMenuItem(title: title, action: action, keyEquivalent: "")
        item.target = self
        return item
    }

    private func send(_ action: HelperAction) {
        writeCommand(action: action)
    }

    @objc private func openMain() {
        send(.openMain)
    }

    @objc private func openDashboard() {
        send(.openDashboard)
    }

    @objc private func quickCache() {
        send(.quickCache)
    }

    @objc private func quickMemory() {
        send(.quickMemory)
    }

    @objc private func hideMain() {
        send(.hideMain)
    }

    @objc private func quitMain() {
        send(.quitMain)
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.15) {
            NSApp.terminate(nil)
        }
    }
}

private func parseArgument(named name: String) -> String? {
    let args = CommandLine.arguments
    guard let index = args.firstIndex(of: name), args.indices.contains(index + 1) else {
        return nil
    }
    return args[index + 1]
}

let delegate = AppDelegate()
delegate.configure(
    parentPID: pid_t(parseArgument(named: "--main-pid").flatMap(Int32.init) ?? 0),
    mainAppPath: parseArgument(named: "--main-app") ?? ""
)

let app = NSApplication.shared
app.setActivationPolicy(.accessory)
app.delegate = delegate
app.run()
