import AppKit
import SwiftUI

final class AppDelegate: NSObject, NSApplicationDelegate, NSPopoverDelegate {
    private var statusItem: NSStatusItem?
    private var popover: NSPopover?
    private var lockFileDescriptor: Int32 = -1
    private var parentTimer: Timer?
    private var parentPID: pid_t = 0
    private var viewModel: MenuBarViewModel?
    private var localEventMonitor: Any?
    private var globalEventMonitor: Any?

    func configure(parentPID: pid_t) {
        self.parentPID = parentPID
    }

    @MainActor
    func applicationDidFinishLaunching(_ notification: Notification) {
        guard let fd = acquireSingletonLock() else {
            NSApp.terminate(nil)
            return
        }
        lockFileDescriptor = fd
        installStatusItem()
        startParentMonitor()
        appendHelperLog("native menu helper started successfully")
    }

    @MainActor
    func applicationWillTerminate(_ notification: Notification) {
        parentTimer?.invalidate()
        viewModel?.panelDidClose()
        removeEventMonitors()
        if lockFileDescriptor >= 0 {
            close(lockFileDescriptor)
            lockFileDescriptor = -1
        }
    }

    @MainActor
    func popoverDidShow(_ notification: Notification) {
        viewModel?.panelDidOpen()
    }

    @MainActor
    func popoverDidClose(_ notification: Notification) {
        viewModel?.panelDidClose()
    }

    @MainActor
    @objc private func togglePopover(_ sender: Any?) {
        guard let button = statusItem?.button else {
            return
        }
        if popover?.isShown == true {
            closePopover()
        } else {
            showPopover(relativeTo: button)
        }
    }

    @MainActor
    private func installStatusItem() {
        let viewModel = MenuBarViewModel(
            actionHandler: { [weak self] action in
                self?.handle(action)
            },
            closeHandler: { [weak self] in
                self?.closePopover()
            }
        )
        self.viewModel = viewModel

        let hostingController = NSHostingController(rootView: MenuBarContentView(viewModel: viewModel))
        let popover = NSPopover()
        popover.animates = true
        popover.behavior = .applicationDefined
        popover.contentSize = NSSize(width: 408, height: 620)
        popover.contentViewController = hostingController
        popover.delegate = self
        self.popover = popover

        let statusItem = NSStatusBar.system.statusItem(withLength: NSStatusItem.squareLength)
        guard let button = statusItem.button else {
            appendHelperLog("failed to create status item button")
            return
        }
        button.title = ""
        button.toolTip = appName
        button.image = makeStatusIcon()
        button.imagePosition = .imageOnly
        button.target = self
        button.action = #selector(togglePopover(_:))
        button.sendAction(on: [.leftMouseUp])
        self.statusItem = statusItem
        appendHelperLog("native AppKit status item installed successfully")
    }

    private func startParentMonitor() {
        let parentPID = self.parentPID
        parentTimer = Timer.scheduledTimer(withTimeInterval: 2.0, repeats: true) { _ in
            if !parentIsAlive(parentPID) {
                appendHelperLog("parent pid is gone; exiting native helper")
                NSApp.terminate(nil)
            }
        }
    }

    @MainActor
    private func showPopover(relativeTo button: NSStatusBarButton) {
        guard let popover else {
            return
        }
        installEventMonitors()
        popover.show(relativeTo: button.bounds, of: button, preferredEdge: .minY)
        popover.contentViewController?.view.window?.becomeKey()
        popover.contentViewController?.view.window?.makeFirstResponder(nil)
    }

    @MainActor
    private func closePopover() {
        removeEventMonitors()
        popover?.performClose(nil)
    }

    @MainActor
    private func handle(_ action: HelperAction) {
        writeCommand(action: action)
        if action == .quitMain {
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.2) {
                NSApp.terminate(nil)
            }
        }
    }

    @MainActor
    private func installEventMonitors() {
        guard localEventMonitor == nil, globalEventMonitor == nil else {
            return
        }

        localEventMonitor = NSEvent.addLocalMonitorForEvents(matching: [.leftMouseDown, .rightMouseDown, .otherMouseDown]) { [weak self] event in
            guard let self else { return event }
            if self.popover?.isShown == true, !self.containsInteractionPoint(event.locationInWindow, from: event.window) {
                self.closePopover()
            }
            return event
        }

        globalEventMonitor = NSEvent.addGlobalMonitorForEvents(matching: [.leftMouseDown, .rightMouseDown, .otherMouseDown]) { [weak self] _ in
            guard let self else { return }
            safeMainActor {
                guard self.popover?.isShown == true else {
                    return
                }
                let screenPoint = NSEvent.mouseLocation
                if !self.containsScreenPoint(screenPoint) {
                    self.closePopover()
                }
            }
        }
    }

    @MainActor
    private func removeEventMonitors() {
        if let localEventMonitor {
            NSEvent.removeMonitor(localEventMonitor)
            self.localEventMonitor = nil
        }
        if let globalEventMonitor {
            NSEvent.removeMonitor(globalEventMonitor)
            self.globalEventMonitor = nil
        }
    }

    @MainActor
    private func containsInteractionPoint(_ point: NSPoint, from window: NSWindow?) -> Bool {
        guard let window else {
            return containsScreenPoint(NSEvent.mouseLocation)
        }
        let screenPoint = window.convertPoint(toScreen: point)
        return containsScreenPoint(screenPoint)
    }

    @MainActor
    private func containsScreenPoint(_ screenPoint: NSPoint) -> Bool {
        if let popoverWindow = popover?.contentViewController?.view.window,
           popoverWindow.frame.contains(screenPoint) {
            return true
        }

        if let button = statusItem?.button,
           let buttonWindow = button.window {
            let buttonFrame = buttonWindow.convertToScreen(button.convert(button.bounds, to: nil))
            if buttonFrame.contains(screenPoint) {
                return true
            }
        }

        return false
    }
}

let delegate = AppDelegate()
delegate.configure(
    parentPID: pid_t(parseArgument(named: "--main-pid").flatMap(Int32.init) ?? 0)
)

let app = NSApplication.shared
app.setActivationPolicy(.accessory)
app.delegate = delegate
app.run()
