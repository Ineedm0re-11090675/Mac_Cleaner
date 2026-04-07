from __future__ import annotations

import plistlib
import shutil
import subprocess
from pathlib import Path

from task_support import raise_if_cancelled


HOME = Path.home()
APPLICATION_DIRS = [Path("/Applications"), HOME / "Applications"]
RESIDUAL_ROOTS = [
    {
        "key": "caches",
        "name": "缓存目录",
        "path": HOME / "Library" / "Caches",
        "risk_level": "低",
        "description": "用户缓存目录，通常风险较低。",
    },
    {
        "key": "logs",
        "name": "日志目录",
        "path": HOME / "Library" / "Logs",
        "risk_level": "低",
        "description": "用户日志目录，通常风险较低。",
    },
    {
        "key": "preferences",
        "name": "偏好设置",
        "path": HOME / "Library" / "Preferences",
        "risk_level": "低",
        "description": "应用偏好设置 plist 文件。",
    },
    {
        "key": "application_support",
        "name": "应用支持目录",
        "path": HOME / "Library" / "Application Support",
        "risk_level": "中",
        "description": "应用支持目录，删除前建议先确认。",
    },
    {
        "key": "containers",
        "name": "容器目录",
        "path": HOME / "Library" / "Containers",
        "risk_level": "高",
        "description": "容器目录风险较高，建议先在访达里确认。",
    },
    {
        "key": "group_containers",
        "name": "共享容器目录",
        "path": HOME / "Library" / "Group Containers",
        "risk_level": "高",
        "description": "共享容器目录风险较高，可能被多个应用共用。",
    },
]


def _normalize_name(value: str) -> str:
    return "".join(ch.lower() for ch in value if ch.isalnum())


def _guess_display_name(identifier: str) -> str:
    lower = identifier.lower()
    known_names = [
        ("tencent.xinwechat", "微信"),
        ("tencent.weixin", "微信"),
        ("tencent.qq", "QQ"),
        ("tencent.mobileqq", "QQ"),
        ("dingtalk", "钉钉"),
        ("163music", "网易云音乐"),
        ("google.chrome", "Google Chrome"),
        ("microsoft.edgemac", "Microsoft Edge"),
        ("firefox", "Firefox"),
        ("safari", "Safari"),
        ("steam", "Steam"),
        ("discord", "Discord"),
        ("spotify", "Spotify"),
        ("logi", "Logi"),
    ]
    for keyword, label in known_names:
        if keyword in lower:
            return label

    tail = identifier.split(".")[-1]
    cleaned = tail.replace("-", " ").replace("_", " ").strip()
    return cleaned or identifier


def _du_size_bytes(path: Path) -> int:
    try:
        completed = subprocess.run(
            ["du", "-sk", str(path)],
            check=True,
            capture_output=True,
            text=True,
        )
        kb = int((completed.stdout.strip().split() or ["0"])[0])
        return kb * 1024
    except Exception:
        return 0


def _iter_application_bundles(base: Path) -> list[Path]:
    bundles: list[Path] = []
    if not base.exists():
        return bundles

    try:
        for child in base.iterdir():
            if child.suffix == ".app":
                bundles.append(child)
            elif child.is_dir():
                for nested in child.glob("*.app"):
                    bundles.append(nested)
    except OSError:
        return bundles
    return bundles


def _installed_app_index() -> tuple[set[str], dict[str, str], set[str]]:
    identifiers: set[str] = set()
    names_by_identifier: dict[str, str] = {}
    normalized_names: set[str] = set()

    for base in APPLICATION_DIRS:
        for bundle in _iter_application_bundles(base):
            info_plist = bundle / "Contents" / "Info.plist"
            bundle_name = bundle.stem
            normalized_names.add(_normalize_name(bundle_name))
            if not info_plist.exists():
                continue
            try:
                data = plistlib.loads(info_plist.read_bytes())
            except Exception:
                continue

            bundle_id = str(data.get("CFBundleIdentifier") or "").strip()
            display_name = (
                str(data.get("CFBundleDisplayName") or "").strip()
                or str(data.get("CFBundleName") or "").strip()
                or bundle_name
            )
            if bundle_id:
                identifiers.add(bundle_id)
                names_by_identifier[bundle_id] = display_name
                normalized_names.add(_normalize_name(display_name))

    return identifiers, names_by_identifier, normalized_names


def _looks_like_bundle_identifier(identifier: str) -> bool:
    parts = [part for part in identifier.split(".") if part]
    if len(parts) < 2:
        return False
    for part in parts:
        if not all(ch.isalnum() or ch in {"-", "_"} for ch in part):
            return False
    return True


def _strip_team_prefix(name: str) -> str:
    parts = name.split(".", 1)
    if len(parts) == 2 and len(parts[0]) >= 6 and parts[0].isalnum() and parts[0].upper() == parts[0]:
        return parts[1]
    return name


def _extract_identifier(entry: Path, root_key: str) -> str:
    candidate = entry.name
    if root_key == "preferences":
        if entry.suffix != ".plist":
            return ""
        candidate = entry.stem
    elif root_key == "group_containers":
        candidate = _strip_team_prefix(candidate)

    if not _looks_like_bundle_identifier(candidate):
        return ""
    if candidate.startswith("com.apple.") or candidate.startswith("group.com.apple."):
        return ""
    return candidate


def _identifier_is_installed(identifier: str, installed_ids: set[str]) -> bool:
    if identifier in installed_ids:
        return True
    for installed_id in installed_ids:
        if identifier.startswith(installed_id + ".") or installed_id.startswith(identifier + "."):
            return True
    return False


def _safe_relative_to(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def _build_reason(config: dict, identifier: str) -> str:
    return (
        f"路径名看起来像应用标识符“{identifier}”，但当前没有找到对应的已安装应用。"
        f" 来源目录：{config['name']}。"
    )


def scan_app_residuals(selected_roots: list[str] | None = None) -> dict:
    selected = set(selected_roots or [])
    include_all = not selected
    installed_ids, installed_names, installed_normalized_names = _installed_app_index()

    items: list[dict] = []
    groups: dict[str, dict] = {}

    for config in RESIDUAL_ROOTS:
        if not include_all and config["key"] not in selected:
            continue

        root = Path(config["path"])
        if not root.exists():
            continue

        try:
            entries = sorted(root.iterdir(), key=lambda entry: entry.name.lower())
        except OSError:
            continue

        for entry in entries:
            if entry.name.startswith(".") or entry.is_symlink():
                continue

            identifier = _extract_identifier(entry, config["key"])
            if not identifier:
                continue
            if _identifier_is_installed(identifier, installed_ids):
                continue

            display_name = installed_names.get(identifier) or _guess_display_name(identifier)
            if _normalize_name(display_name) in installed_normalized_names:
                continue

            size_bytes = _du_size_bytes(entry) if entry.is_dir() else int(entry.stat().st_size)
            item = {
                "id": str(entry),
                "group": display_name,
                "name": entry.name,
                "identifier": identifier,
                "path": str(entry),
                "size_bytes": size_bytes,
                "risk_level": config["risk_level"],
                "location_type": config["name"],
                "location_description": config["description"],
                "reason": _build_reason(config, identifier),
                "is_directory": entry.is_dir(),
                "action_path": str(entry),
            }
            items.append(item)

            group = groups.setdefault(
                display_name,
                {
                    "key": display_name,
                    "name": display_name,
                    "count": 0,
                    "total_bytes": 0,
                    "high_risk_count": 0,
                },
            )
            group["count"] += 1
            group["total_bytes"] += size_bytes
            if config["risk_level"] == "高":
                group["high_risk_count"] += 1

    items.sort(
        key=lambda item: (
            {"高": 0, "中": 1, "低": 2}.get(item["risk_level"], 3),
            -int(item["size_bytes"] or 0),
            item["group"].lower(),
            item["name"].lower(),
        )
    )
    group_list = sorted(groups.values(), key=lambda group: (-group["total_bytes"], group["name"].lower()))

    return {
        "groups": group_list,
        "items": items,
        "total_count": len(items),
        "total_bytes": sum(item["size_bytes"] for item in items),
        "high_risk_count": sum(1 for item in items if item["risk_level"] == "高"),
    }


def _is_safe_residual_path(path: Path) -> bool:
    if not path.is_absolute():
        return False
    if not _safe_relative_to(path, HOME):
        return False
    return any(_safe_relative_to(path, Path(config["path"])) for config in RESIDUAL_ROOTS)


def clean_app_residuals(
    selected_items: list[dict] | None = None,
    *,
    log_callback=None,
    cancel_check=None,
) -> dict:
    results = []

    for item in selected_items or []:
        raise_if_cancelled(cancel_check)
        raw_path = str(item.get("path") or "")
        path = Path(raw_path)
        name = str(item.get("name") or path.name or raw_path)
        if log_callback:
            log_callback(f"正在删除残留：{name}")
        try:
            if not path.exists():
                raise FileNotFoundError(f"路径不存在：{path}")
            if not _is_safe_residual_path(path):
                raise ValueError(f"不允许删除这个路径：{path}")

            reclaimed_bytes = _du_size_bytes(path) if path.is_dir() else int(path.stat().st_size)
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()

            results.append(
                {
                    "path": str(path),
                    "name": name,
                    "success": True,
                    "reclaimed_bytes": reclaimed_bytes,
                    "message": "已删除",
                }
            )
            if log_callback:
                log_callback(f"已删除残留：{name}")
        except Exception as exc:
            results.append(
                {
                    "path": raw_path,
                    "name": name,
                    "success": False,
                    "reclaimed_bytes": 0,
                    "message": str(exc),
                }
            )
            if log_callback:
                log_callback(f"删除失败：{name} | {exc}")

    return {
        "results": results,
        "deleted_count": sum(1 for item in results if item["success"]),
        "failed_count": sum(1 for item in results if not item["success"]),
        "reclaimed_bytes": sum(item["reclaimed_bytes"] for item in results if item["success"]),
    }
