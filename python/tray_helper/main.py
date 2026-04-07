from __future__ import annotations

import argparse
import ctypes
import fcntl
import os
import signal
import subprocess
import sys
from pathlib import Path


PROJECT_PYTHON_DIR = Path(__file__).resolve().parents[1]
if str(PROJECT_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_PYTHON_DIR))

from tray_ipc import HELPER_LOCK_PATH, append_helper_log, ensure_runtime_dirs, write_command


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


def resolve_status_helper_path() -> Path | None:
    if getattr(sys, "frozen", False):
        executable_dir = Path(sys.executable).resolve().parent
        contents_dir = executable_dir.parent
        candidates = [
            executable_dir / "libmacos_status_item.dylib",
            contents_dir / "Frameworks" / "libmacos_status_item.dylib",
            contents_dir / "Resources" / "libmacos_status_item.dylib",
        ]
    else:
        candidates = [Path(__file__).resolve().parents[2] / "build" / "libmacos_status_item.dylib"]
    for path in candidates:
        if path.exists():
            return path
    return None


def acquire_singleton_lock():
    ensure_runtime_dirs()
    handle = HELPER_LOCK_PATH.open("w")
    try:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        handle.close()
        return None
    handle.write(str(os.getpid()))
    handle.flush()
    return handle


def parent_is_alive(parent_pid: int) -> bool:
    if parent_pid <= 0:
        return True
    try:
        os.kill(parent_pid, 0)
        return True
    except OSError:
        return False


def open_app_bundle(app_path: str | None) -> None:
    if not app_path:
        return
    subprocess.run(["open", app_path], check=False)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--main-pid", type=int, default=0)
    parser.add_argument("--main-app", default="")
    args = parser.parse_args()

    lock_handle = acquire_singleton_lock()
    if lock_handle is None:
        append_helper_log("another tray helper instance is already running; exiting")
        return 0

    try:
        from PySide6.QtCore import QTimer
        from PySide6.QtGui import QIcon
        from PySide6.QtWidgets import QApplication
    except Exception as exc:
        append_helper_log(f"PySide6 import failed: {exc}")
        return 1

    app = QApplication(sys.argv)
    app.setApplicationName("macOS Cleaner Menu")
    app.setQuitOnLastWindowClosed(False)
    icon_path = resolve_app_icon_path()
    if icon_path:
        icon = QIcon(str(icon_path))
        if not icon.isNull():
            app.setWindowIcon(icon)

    helper_path = resolve_status_helper_path()
    if helper_path is None:
        append_helper_log("status item helper dylib not found")
        return 1

    try:
        library = ctypes.CDLL(str(helper_path))
    except OSError as exc:
        append_helper_log(f"failed to load status item dylib: {exc}")
        return 1

    callback_type = ctypes.CFUNCTYPE(None)

    def send(action: str) -> None:
        open_app_bundle(args.main_app)
        path = write_command(action)
        append_helper_log(f"queued command {action}: {path}")

    @callback_type
    def on_open_main() -> None:
        send("open_main")

    @callback_type
    def on_open_dashboard() -> None:
        send("open_dashboard")

    @callback_type
    def on_quick_cache() -> None:
        send("quick_cache")

    @callback_type
    def on_quick_memory() -> None:
        send("quick_memory")

    @callback_type
    def on_hide() -> None:
        send("hide_main")

    @callback_type
    def on_quit() -> None:
        send("quit_main")
        QTimer.singleShot(150, app.quit)

    library.mcc_install_status_item.argtypes = [
        callback_type,
        callback_type,
        callback_type,
        callback_type,
        callback_type,
        callback_type,
    ]
    library.mcc_install_status_item.restype = ctypes.c_bool

    app._macos_cleaner_status_library = library  # type: ignore[attr-defined]
    app._macos_cleaner_lock_handle = lock_handle  # type: ignore[attr-defined]
    app._macos_cleaner_callbacks = (  # type: ignore[attr-defined]
        on_open_main,
        on_open_dashboard,
        on_quick_cache,
        on_quick_memory,
        on_hide,
        on_quit,
    )

    def install_status_item() -> None:
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
            append_helper_log("native helper failed to install status item")
            app.quit()
            return
        append_helper_log(f"tray helper started successfully with parent pid {args.main_pid}")

    QTimer.singleShot(0, install_status_item)

    parent_timer = QTimer()
    parent_timer.setInterval(2000)

    def check_parent() -> None:
        if not parent_is_alive(args.main_pid):
            append_helper_log("parent pid is gone; exiting tray helper")
            app.quit()

    parent_timer.timeout.connect(check_parent)
    parent_timer.start()

    def shutdown(*_args) -> None:
        app.quit()

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
