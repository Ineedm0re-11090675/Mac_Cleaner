from __future__ import annotations

import ctypes
import os
import subprocess
import sys
import traceback
from datetime import datetime
from pathlib import Path


if not getattr(sys, "frozen", False):
    PROJECT_PYTHON_DIR = Path(__file__).resolve().parents[1]
    if str(PROJECT_PYTHON_DIR) not in sys.path:
        sys.path.insert(0, str(PROJECT_PYTHON_DIR))


def resolve_app_icon_path() -> Path | None:
    if getattr(sys, "frozen", False):
        resources_dir = Path(sys.executable).resolve().parent.parent / "Resources"
        icon_path = resources_dir / "AppIcon.icns"
        if icon_path.exists():
            return icon_path
    else:
        icon_path = Path(__file__).resolve().parents[2] / "assets" / "AppIcon.icns"
        if icon_path.exists():
            return icon_path
    return None


def resolve_helper_path(filename: str) -> Path | None:
    if getattr(sys, "frozen", False):
        executable_dir = Path(sys.executable).resolve().parent
        contents_dir = executable_dir.parent
        candidates = [
            executable_dir / filename,
            contents_dir / "Frameworks" / filename,
            contents_dir / "Resources" / filename,
        ]
    else:
        candidates = [Path(__file__).resolve().parents[2] / "build" / filename]
    for helper_path in candidates:
        if helper_path.exists():
            return helper_path
    return None


def append_runtime_diag(message: str) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    paths = [Path("/tmp/macos_cleaner_tray.log")]
    try:
        app_support_dir = Path.home() / "Library" / "Application Support" / "macOS Cleaner" / "runtime"
        app_support_dir.mkdir(parents=True, exist_ok=True)
        paths.append(app_support_dir / "main-app.log")
    except OSError:
        pass
    for log_path in paths:
        try:
            with log_path.open("a", encoding="utf-8") as handle:
                handle.write(f"[{timestamp}] {message}\n")
        except OSError:
            continue


def main() -> int:
    try:
        from PySide6.QtCore import QObject, QEvent, QTimer, Qt
        from PySide6.QtGui import QIcon
        from PySide6.QtWidgets import QApplication
    except ImportError as exc:
        print("PySide6 导入失败。")
        print(f"错误详情: {exc!r}")
        traceback.print_exc()
        if getattr(sys, "frozen", False):
            print("这是打包版应用中的运行时导入错误，不一定是本机没有安装 PySide6。")
        else:
            print("先运行：pip3 install PySide6")
            print("然后再启动：python3 python/desktop_app/main.py")
        return 1

    from desktop_app.window import CleanerDesktopWindow
    from tray_ipc import RUNTIME_DIR, drain_commands, ensure_runtime_dirs

    app = QApplication(sys.argv)
    app.setApplicationName("macOS Cleaner Desktop")
    app.setQuitOnLastWindowClosed(False)
    icon_path = resolve_app_icon_path()
    app_icon = QIcon(str(icon_path)) if icon_path else QIcon()
    if not app_icon.isNull():
        app.setWindowIcon(app_icon)
    window = CleanerDesktopWindow()
    if not app_icon.isNull():
        window.setWindowIcon(app_icon)
    window.show()

    def install_native_reopen_handler() -> tuple[object, object] | None:
        if sys.platform != "darwin":
            append_runtime_diag("native_reopen skipped: non-darwin platform")
            return None
        helper_path = resolve_helper_path("libmacos_reopen_hook.dylib")
        if helper_path is None:
            append_runtime_diag("native_reopen skipped: helper not found")
            return None
        try:
            library = ctypes.CDLL(str(helper_path))
        except OSError as exc:
            append_runtime_diag(f"native_reopen failed to load dylib: {exc}")
            return None
        callback_type = ctypes.CFUNCTYPE(None)

        @callback_type
        def on_reopen() -> None:
            QTimer.singleShot(0, window.show_main_window)

        library.mcc_install_reopen_handler.argtypes = [callback_type]
        library.mcc_install_reopen_handler.restype = None
        library.mcc_install_reopen_handler(on_reopen)
        append_runtime_diag(f"native_reopen installed successfully: helper={helper_path}")
        return library, on_reopen

    def install_native_status_item() -> tuple[object, object, object, object, object, object, object] | None:
        if sys.platform != "darwin":
            append_runtime_diag("native_status_item skipped: non-darwin platform")
            return None
        helper_path = resolve_helper_path("libmacos_status_item.dylib")
        if helper_path is None:
            append_runtime_diag("native_status_item skipped: helper not found")
            return None
        try:
            library = ctypes.CDLL(str(helper_path))
        except OSError as exc:
            append_runtime_diag(f"native_status_item failed to load dylib: {exc}")
            return None
        callback_type = ctypes.CFUNCTYPE(None)

        @callback_type
        def on_open_main() -> None:
            QTimer.singleShot(0, window.bring_main_window_to_front)

        @callback_type
        def on_open_dashboard() -> None:
            QTimer.singleShot(0, window.open_dashboard)

        @callback_type
        def on_quick_cache() -> None:
            QTimer.singleShot(0, window.run_tray_quick_cache_cleanup)

        @callback_type
        def on_quick_memory() -> None:
            QTimer.singleShot(0, window.run_tray_quick_memory_reclaim)

        @callback_type
        def on_hide() -> None:
            QTimer.singleShot(0, window.hide_to_background)

        @callback_type
        def on_quit() -> None:
            QTimer.singleShot(0, app.quit)

        library.mcc_install_status_item.argtypes = [
            callback_type,
            callback_type,
            callback_type,
            callback_type,
            callback_type,
            callback_type,
        ]
        library.mcc_install_status_item.restype = ctypes.c_bool
        installed = bool(
            library.mcc_install_status_item(
                on_open_main,
                on_open_dashboard,
                on_quick_cache,
                on_quick_memory,
                on_hide,
                on_quit,
            )
        )
        if not installed:
            append_runtime_diag(f"native_status_item install returned false: helper={helper_path}")
            return None
        window.set_tray_available(True)
        append_runtime_diag(f"native_status_item installed successfully: helper={helper_path}")
        return (
            library,
            on_open_main,
            on_open_dashboard,
            on_quick_cache,
            on_quick_memory,
            on_hide,
            on_quit,
        )

    native_reopen_hook = install_native_reopen_handler()

    class DockRestoreFilter(QObject):
        def __init__(self) -> None:
            super().__init__()
            self._last_state = app.applicationState()

        def eventFilter(self, watched, event):  # type: ignore[override]
            if watched is app and window.should_restore_on_activation():
                event_type = event.type()
                if event_type == QEvent.Type.ApplicationActivate:
                    QTimer.singleShot(0, window.show_main_window)
                elif event_type == QEvent.Type.ApplicationStateChange:
                    try:
                        new_state = event.applicationState()
                    except AttributeError:
                        new_state = app.applicationState()
                    if (
                        self._last_state == Qt.ApplicationState.ApplicationActive
                        and new_state == Qt.ApplicationState.ApplicationActive
                    ):
                        QTimer.singleShot(0, window.show_main_window)
                    self._last_state = new_state
            return False

    dock_restore_filter = DockRestoreFilter()
    app.installEventFilter(dock_restore_filter)

    def resolve_main_app_bundle() -> Path | None:
        if not getattr(sys, "frozen", False):
            return None
        executable = Path(sys.executable).resolve()
        try:
            return executable.parent.parent.parent
        except IndexError:
            return None

    def resolve_helper_app_path() -> Path | None:
        if getattr(sys, "frozen", False):
            main_bundle = resolve_main_app_bundle()
            if main_bundle is None:
                return None
            helper_path = main_bundle / "Contents" / "Helpers" / "macOS Cleaner Menu.app"
            return helper_path if helper_path.exists() else None
        helper_path = Path(__file__).resolve().parents[2] / "packaging" / "dev-helper-placeholder"
        return helper_path if helper_path.exists() else None

    def resolve_helper_executable_path() -> Path | None:
        helper_app = resolve_helper_app_path()
        if helper_app is None:
            return None
        executable = helper_app / "Contents" / "MacOS" / "macOS Cleaner Menu"
        return executable if executable.exists() else None

    def launch_menu_helper() -> bool:
        append_runtime_diag("launch_menu_helper invoked")
        ensure_runtime_dirs()
        drain_commands()
        if sys.platform != "darwin":
            append_runtime_diag("launch_menu_helper skipped: non-darwin platform")
            return False
        if getattr(sys, "frozen", False):
            helper_app = resolve_helper_app_path()
            helper_exec = resolve_helper_executable_path()
            main_bundle = resolve_main_app_bundle()
            if helper_app is None or helper_exec is None or main_bundle is None:
                append_runtime_diag("launch_menu_helper skipped: helper bundle or executable not found in bundle")
                return False
            try:
                subprocess.Popen(
                    [
                        "/usr/bin/open",
                        "-n",
                        str(helper_app),
                        "--args",
                        "--main-pid",
                        str(os.getpid()),
                        "--main-app",
                        str(main_bundle),
                    ],
                    cwd=str(helper_app.parent),
                )
                append_runtime_diag(f"launch_menu_helper started bundled helper app via open: {helper_app}")
                return True
            except OSError as exc:
                append_runtime_diag(f"launch_menu_helper failed to start bundled helper app via open: {exc}")
                return False
        helper_script = Path(__file__).resolve().parents[1] / "tray_helper" / "main.py"
        env = dict(os.environ)
        python_root = str(Path(__file__).resolve().parents[1])
        env["PYTHONPATH"] = python_root + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
        try:
            stdout_path = RUNTIME_DIR / "tray-helper.stdout.log"
            stderr_path = RUNTIME_DIR / "tray-helper.stderr.log"
            stdout_handle = stdout_path.open("a", encoding="utf-8")
            stderr_handle = stderr_path.open("a", encoding="utf-8")
            process = subprocess.Popen(
                [
                    sys.executable,
                    str(helper_script),
                    "--main-pid",
                    str(os.getpid()),
                    "--main-app",
                    "",
                ],
                env=env,
                stdout=stdout_handle,
                stderr=stderr_handle,
            )
            app._macos_cleaner_helper_process = process  # type: ignore[attr-defined]
            append_runtime_diag(f"launch_menu_helper started dev helper pid={process.pid}")
            return True
        except OSError as exc:
            append_runtime_diag(f"launch_menu_helper failed to start dev helper: {exc}")
            return False

    def dispatch_helper_command(command: dict) -> None:
        action = str(command.get("action") or "")
        append_runtime_diag(f"dispatch_helper_command received: {action}")
        if action == "open_main":
            window.bring_main_window_to_front()
        elif action == "open_dashboard":
            window.open_dashboard()
        elif action == "quick_cache":
            window.run_tray_quick_cache_cleanup()
        elif action == "quick_memory":
            window.run_tray_quick_memory_reclaim()
        elif action == "hide_main":
            window.hide_to_background()
        elif action == "quit_main":
            app.quit()

    helper_command_timer = QTimer()
    helper_command_timer.setInterval(350)

    def process_helper_commands() -> None:
        for command in drain_commands():
            dispatch_helper_command(command)

    helper_command_timer.timeout.connect(process_helper_commands)

    def on_application_state_changed(state) -> None:
        if state == Qt.ApplicationState.ApplicationActive and window.should_restore_on_activation():
            QTimer.singleShot(0, window.show_main_window)

    app.applicationStateChanged.connect(on_application_state_changed)
    append_runtime_diag("app startup complete, scheduling helper launch")
    helper_command_timer.start()

    def boot_helper() -> None:
        if os.environ.get("MACOS_CLEANER_TRAY_BOOTSTRAPPED") == "1":
            append_runtime_diag("launch_menu_helper skipped: wrapper already attempted helper bootstrap")
            launched_helper = True
        else:
            launched_helper = launch_menu_helper()
        window.set_tray_available(launched_helper)

    QTimer.singleShot(750, boot_helper)
    app._macos_cleaner_dock_restore_filter = dock_restore_filter  # type: ignore[attr-defined]
    app._macos_cleaner_native_reopen_hook = native_reopen_hook  # type: ignore[attr-defined]
    app._macos_cleaner_helper_command_timer = helper_command_timer  # type: ignore[attr-defined]
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
