from __future__ import annotations

import sys
import traceback
from pathlib import Path


if not getattr(sys, "frozen", False):
    PROJECT_PYTHON_DIR = Path(__file__).resolve().parents[1]
    if str(PROJECT_PYTHON_DIR) not in sys.path:
        sys.path.insert(0, str(PROJECT_PYTHON_DIR))


def main() -> int:
    try:
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

    app = QApplication(sys.argv)
    app.setApplicationName("macOS Cleaner Desktop")
    window = CleanerDesktopWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
