from __future__ import annotations

import json
import platform
import subprocess
import sys
from pathlib import Path

from bridge import CleanerBridge


APP_NAME = "macOS Cleaner"
APP_VERSION = "desktop-2026-04-06-1005"
HOME = Path.home()
APP_SUPPORT_DIR = HOME / "Library" / "Application Support" / APP_NAME
SETTINGS_PATH = APP_SUPPORT_DIR / "settings.json"

PERMISSION_ROOTS = [
    {"key": "desktop", "name": "桌面", "path": HOME / "Desktop"},
    {"key": "downloads", "name": "下载", "path": HOME / "Downloads"},
    {"key": "documents", "name": "文稿", "path": HOME / "Documents"},
    {"key": "pictures", "name": "图片", "path": HOME / "Pictures"},
    {"key": "photos_library", "name": "照片图库", "path": HOME / "Pictures" / "Photos Library.photoslibrary"},
    {"key": "application_support", "name": "其他 App 数据（Application Support）", "path": HOME / "Library" / "Application Support"},
    {"key": "containers", "name": "其他 App 数据（Containers）", "path": HOME / "Library" / "Containers"},
    {"key": "group_containers", "name": "其他 App 数据（Group Containers）", "path": HOME / "Library" / "Group Containers"},
]

THEME_OPTIONS = {
    "follow_system": "跟随系统",
    "light": "浅色",
    "dark": "深色",
}

DEFAULT_SETTINGS = {
    "theme_mode": "follow_system",
    "confirm_before_delete": True,
    "confirm_high_risk_delete": True,
}

SYSTEM_SETTINGS_URLS = {
    "privacy_files": "x-apple.systempreferences:com.apple.preference.security?Privacy_FilesAndFolders",
    "privacy_automation": "x-apple.systempreferences:com.apple.preference.security?Privacy_Automation",
    "privacy": "x-apple.systempreferences:com.apple.preference.security",
    "general": "x-apple.systempreferences:com.apple.preferences",
}


def _status_label(accessible: bool, exists: bool, error: str) -> str:
    if not exists:
        return "目录不存在"
    if accessible:
        return "已授权"
    if error:
        return "未授权或读取失败"
    return "未检测"


class SettingsManager:
    def __init__(self) -> None:
        self._settings = self._load()

    def _load(self) -> dict:
        if not SETTINGS_PATH.exists():
            return dict(DEFAULT_SETTINGS)
        try:
            loaded = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
        except Exception:
            return dict(DEFAULT_SETTINGS)
        merged = dict(DEFAULT_SETTINGS)
        if isinstance(loaded, dict):
            merged.update(loaded)
        return merged

    def save(self) -> None:
        APP_SUPPORT_DIR.mkdir(parents=True, exist_ok=True)
        SETTINGS_PATH.write_text(
            json.dumps(self._settings, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def get(self, key: str, default=None):
        return self._settings.get(key, default)

    def set(self, key: str, value) -> None:
        self._settings[key] = value
        self.save()

    def as_dict(self) -> dict:
        return dict(self._settings)

    def runtime_info(self) -> dict:
        bridge = CleanerBridge()
        binary = bridge.binary
        return {
            "app_name": APP_NAME,
            "app_version": APP_VERSION,
            "packaged": bool(getattr(sys, "frozen", False)),
            "python_version": platform.python_version(),
            "system_version": platform.mac_ver()[0] or "未知系统版本",
            "architecture": platform.machine() or "未知架构",
            "core_binary": str(binary),
            "core_binary_exists": binary.exists(),
            "workspace_root": str(Path(__file__).resolve().parents[1]),
            "settings_path": str(SETTINGS_PATH),
        }

    def scan_folder_permissions(self) -> dict:
        statuses = []
        for root in PERMISSION_ROOTS:
            path = Path(root["path"])
            exists = path.exists()
            accessible = False
            error = ""
            if exists:
                try:
                    iterator = path.iterdir()
                    next(iterator, None)
                    accessible = True
                except PermissionError as exc:
                    error = str(exc)
                except OSError as exc:
                    error = str(exc)
            statuses.append(
                {
                    "key": root["key"],
                    "name": root["name"],
                    "path": str(path),
                    "exists": exists,
                    "accessible": accessible,
                    "error": error,
                    "status_label": _status_label(accessible, exists, error),
                }
            )
        return {
            "items": statuses,
            "granted_count": sum(1 for item in statuses if item["accessible"]),
            "missing_count": sum(1 for item in statuses if not item["exists"]),
            "denied_count": sum(
                1 for item in statuses if item["exists"] and not item["accessible"]
            ),
        }

    def open_system_settings(self, section: str = "privacy") -> None:
        target = SYSTEM_SETTINGS_URLS.get(section, SYSTEM_SETTINGS_URLS["privacy"])
        subprocess.run(["open", target], check=False)


_SETTINGS_MANAGER = SettingsManager()


def get_settings_manager() -> SettingsManager:
    return _SETTINGS_MANAGER


def open_system_settings(section: str = "privacy") -> None:
    _SETTINGS_MANAGER.open_system_settings(section)
