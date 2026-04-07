from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication


ROOT = Path(__file__).resolve().parents[1]
PYTHON_DIR = ROOT / "python"
DESKTOP_DIR = PYTHON_DIR / "desktop_app"

for candidate in (str(PYTHON_DIR), str(DESKTOP_DIR)):
    if candidate not in sys.path:
        sys.path.insert(0, candidate)

from desktop_app.window import CleanerDesktopWindow  # noqa: E402
from settings_manager import get_settings_manager  # noqa: E402


OUTPUT_DIR = ROOT / "artifacts" / "theme-smoke"
PAGES = ["overview", "files", "images", "space", "caches", "startup", "applications", "settings"]


def render_theme(theme_mode: str) -> None:
    settings = get_settings_manager()
    settings.set("theme_mode", theme_mode)

    app = QApplication.instance() or QApplication([])
    window = CleanerDesktopWindow()
    window.resize(1400, 900)
    window.show()
    app.processEvents()

    theme_dir = OUTPUT_DIR / theme_mode
    theme_dir.mkdir(parents=True, exist_ok=True)

    for page_key in PAGES:
        window.switch_page(page_key)
        app.processEvents()
        target = theme_dir / f"{page_key}.png"
        window.grab().save(str(target))
        print(f"saved {target}")

    window.close()
    app.processEvents()


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for theme in ("light", "dark"):
        render_theme(theme)
    print(f"theme smoke screenshots written to {OUTPUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
