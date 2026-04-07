from __future__ import annotations

import hashlib
import math
import os
import re
import struct
import subprocess
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from task_support import raise_if_cancelled


HOME = Path.home()
IMAGE_ROOTS = [
    {"key": "desktop", "name": "桌面", "path": HOME / "Desktop"},
    {"key": "downloads", "name": "下载", "path": HOME / "Downloads"},
    {"key": "pictures", "name": "图片", "path": HOME / "Pictures"},
    {"key": "photos_library", "name": "照片图库", "path": HOME / "Pictures" / "Photos Library.photoslibrary"},
]
IMAGE_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".bmp",
    ".tif",
    ".tiff",
    ".heic",
    ".heif",
}
PREVIEW_CACHE_DIR = HOME / "Library" / "Caches" / "codex_demo" / "image_previews"
MAX_SCAN_IMAGES = 9000
LIST_LIMIT = 80
GROUP_LIMIT = 24
LARGE_IMAGE_BYTES = 5 * 1024 * 1024
OLD_IMAGE_DAYS = 90
SCREENSHOT_PATTERNS = (
    "截屏",
    "截图",
    "屏幕快照",
    "screen shot",
    "screenshot",
)


def _age_days(stat_result: os.stat_result) -> int:
    modified = datetime.fromtimestamp(stat_result.st_mtime)
    return max((datetime.now() - modified).days, 0)


def _is_screenshot_name(name: str) -> bool:
    lower = name.lower()
    return any(pattern in lower for pattern in SCREENSHOT_PATTERNS)


def _normalize_stem(name: str) -> str:
    stem = Path(name).stem.lower()
    stem = re.sub(r"\(\d+\)$", "", stem)
    stem = re.sub(r"[-_\s]+copy$", "", stem)
    stem = re.sub(r"[^0-9a-z\u4e00-\u9fff]+", "", stem)
    return stem


def _safe_iterdir(path: Path) -> list[Path]:
    try:
        return sorted(path.iterdir(), key=lambda item: item.name.lower())
    except OSError:
        return []


def _png_dimensions(path: Path) -> tuple[int | None, int | None]:
    with path.open("rb") as handle:
        data = handle.read(24)
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        return None, None
    width, height = struct.unpack(">II", data[16:24])
    return int(width), int(height)


def _gif_dimensions(path: Path) -> tuple[int | None, int | None]:
    with path.open("rb") as handle:
        data = handle.read(10)
    if len(data) < 10 or not data.startswith((b"GIF87a", b"GIF89a")):
        return None, None
    width, height = struct.unpack("<HH", data[6:10])
    return int(width), int(height)


def _bmp_dimensions(path: Path) -> tuple[int | None, int | None]:
    with path.open("rb") as handle:
        data = handle.read(26)
    if len(data) < 26 or data[:2] != b"BM":
        return None, None
    width, height = struct.unpack("<ii", data[18:26])
    return abs(int(width)), abs(int(height))


def _jpeg_dimensions(path: Path) -> tuple[int | None, int | None]:
    with path.open("rb") as handle:
        data = handle.read(2)
        if data != b"\xff\xd8":
            return None, None
        while True:
            marker_prefix = handle.read(1)
            if not marker_prefix:
                return None, None
            if marker_prefix != b"\xff":
                continue
            marker = handle.read(1)
            while marker == b"\xff":
                marker = handle.read(1)
            if not marker or marker in {b"\xd8", b"\xd9"}:
                continue
            length_bytes = handle.read(2)
            if len(length_bytes) != 2:
                return None, None
            length = struct.unpack(">H", length_bytes)[0]
            if length < 2:
                return None, None
            if marker in {
                b"\xc0", b"\xc1", b"\xc2", b"\xc3",
                b"\xc5", b"\xc6", b"\xc7",
                b"\xc9", b"\xca", b"\xcb",
                b"\xcd", b"\xce", b"\xcf",
            }:
                block = handle.read(5)
                if len(block) != 5:
                    return None, None
                height, width = struct.unpack(">HH", block[1:5])
                return int(width), int(height)
            handle.seek(length - 2, os.SEEK_CUR)


def _webp_dimensions(path: Path) -> tuple[int | None, int | None]:
    with path.open("rb") as handle:
        data = handle.read(64)
    if len(data) < 30 or data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        return None, None
    chunk = data[12:16]
    if chunk == b"VP8X" and len(data) >= 30:
        width = 1 + int.from_bytes(data[24:27], "little")
        height = 1 + int.from_bytes(data[27:30], "little")
        return width, height
    if chunk == b"VP8 " and len(data) >= 30:
        width = struct.unpack("<H", data[26:28])[0] & 0x3FFF
        height = struct.unpack("<H", data[28:30])[0] & 0x3FFF
        return int(width), int(height)
    if chunk == b"VP8L" and len(data) >= 25:
        bits = int.from_bytes(data[21:25], "little")
        width = (bits & 0x3FFF) + 1
        height = ((bits >> 14) & 0x3FFF) + 1
        return int(width), int(height)
    return None, None


def _sips_dimensions(path: Path) -> tuple[int | None, int | None]:
    try:
        completed = subprocess.run(
            ["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(path)],
            check=True,
            capture_output=True,
            text=True,
        )
    except Exception:
        return None, None

    width = None
    height = None
    for line in completed.stdout.splitlines():
        if "pixelWidth:" in line:
            try:
                width = int(line.split(":", 1)[1].strip())
            except ValueError:
                width = None
        if "pixelHeight:" in line:
            try:
                height = int(line.split(":", 1)[1].strip())
            except ValueError:
                height = None
    return width, height


def image_dimensions(path: Path) -> tuple[int | None, int | None]:
    suffix = path.suffix.lower()
    try:
        if suffix == ".png":
            return _png_dimensions(path)
        if suffix in {".jpg", ".jpeg"}:
            return _jpeg_dimensions(path)
        if suffix == ".gif":
            return _gif_dimensions(path)
        if suffix == ".bmp":
            return _bmp_dimensions(path)
        if suffix == ".webp":
            return _webp_dimensions(path)
    except Exception:
        return None, None
    return _sips_dimensions(path)


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except Exception:
        return False


def _iter_image_files(
    selected_roots: list[dict],
    *,
    log_callback=None,
    cancel_check=None,
) -> tuple[list[dict], list[dict], bool]:
    items: list[dict] = []
    root_summaries: list[dict] = []
    truncated = False
    visited_count = 0

    for config in selected_roots:
        raise_if_cancelled(cancel_check)
        root = Path(config["path"])
        if log_callback:
            log_callback(f"正在读取图片来源：{config['name']}")
        root_summary = {
            "key": config["key"],
            "name": config["name"],
            "path": str(root),
            "image_count": 0,
            "total_bytes": 0,
            "exists": root.exists(),
            "accessible": False,
            "error": "",
        }
        if not root.exists():
            root_summaries.append(root_summary)
            continue

        try:
            with os.scandir(root):
                pass
            root_summary["accessible"] = True
        except OSError as exc:
            root_summary["error"] = str(exc)
            root_summaries.append(root_summary)
            continue

        for current_root, dirnames, filenames in os.walk(root):
            raise_if_cancelled(cancel_check)
            dirnames[:] = [name for name in dirnames if not name.startswith(".")]
            for filename in filenames:
                visited_count += 1
                if visited_count % 64 == 0:
                    raise_if_cancelled(cancel_check)
                if filename.startswith("."):
                    continue
                path = Path(current_root) / filename
                if path.suffix.lower() not in IMAGE_EXTENSIONS:
                    continue
                try:
                    stat_result = path.stat()
                except OSError:
                    continue

                width, height = image_dimensions(path)
                item = {
                    "id": str(path),
                    "path": str(path),
                    "name": path.name,
                    "size_bytes": int(stat_result.st_size),
                    "age_days": _age_days(stat_result),
                    "modified_ts": float(stat_result.st_mtime),
                    "root_key": config["key"],
                    "root_name": config["name"],
                    "width": width,
                    "height": height,
                    "dimensions": f"{width} × {height}" if width and height else "未知",
                    "is_screenshot": _is_screenshot_name(path.name),
                    "stem_normalized": _normalize_stem(path.name),
                    "suffix": path.suffix.lower().lstrip("."),
                }
                items.append(item)
                root_summary["image_count"] += 1
                root_summary["total_bytes"] += int(stat_result.st_size)
                if len(items) >= MAX_SCAN_IMAGES:
                    truncated = True
                    break
            if truncated:
                break
        root_summaries.append(root_summary)
        if truncated:
            break

    return items, root_summaries, truncated


def _group_duplicates(items: list[dict], *, cancel_check=None, log_callback=None) -> list[dict]:
    by_size: dict[int, list[dict]] = defaultdict(list)
    groups: list[dict] = []
    for item in items:
        by_size[int(item["size_bytes"])].append(item)

    if log_callback:
        log_callback("正在分析完全重复图片...")
    for same_size_items in by_size.values():
        raise_if_cancelled(cancel_check)
        if len(same_size_items) < 2:
            continue
        by_hash: dict[str, list[dict]] = defaultdict(list)
        for item in same_size_items:
            raise_if_cancelled(cancel_check)
            try:
                by_hash[_hash_file(Path(item["path"]))].append(item)
            except Exception:
                continue
        for duplicate_items in by_hash.values():
            if len(duplicate_items) < 2:
                continue
            duplicate_items.sort(key=lambda entry: (entry["modified_ts"], entry["path"]), reverse=True)
            groups.append(
                {
                    "id": f"duplicate::{hashlib.md5(duplicate_items[0]['path'].encode('utf-8')).hexdigest()}",
                    "name": duplicate_items[0]["name"],
                    "count": len(duplicate_items),
                    "total_bytes": sum(int(entry["size_bytes"]) for entry in duplicate_items),
                    "items": duplicate_items,
                }
            )
    groups.sort(key=lambda group: (-group["total_bytes"], -group["count"], group["name"].lower()))
    return groups[:GROUP_LIMIT]


def _group_similar(items: list[dict], *, cancel_check=None, log_callback=None) -> list[dict]:
    groups: list[dict] = []
    used_paths: set[str] = set()

    if log_callback:
        log_callback("正在分析相似图片组...")
    screenshots = [
        item for item in items
        if item["is_screenshot"] and item["width"] and item["height"]
    ]
    screenshots.sort(key=lambda item: (item["width"], item["height"], item["modified_ts"]))
    current_cluster: list[dict] = []
    for item in screenshots:
        raise_if_cancelled(cancel_check)
        if not current_cluster:
            current_cluster = [item]
            continue
        anchor = current_cluster[-1]
        same_shape = item["width"] == anchor["width"] and item["height"] == anchor["height"]
        time_close = abs(float(item["modified_ts"]) - float(anchor["modified_ts"])) <= 240
        size_ratio = (
            max(int(item["size_bytes"]), int(anchor["size_bytes"])) /
            max(1, min(int(item["size_bytes"]), int(anchor["size_bytes"])))
        )
        if same_shape and time_close and size_ratio <= 1.4:
            current_cluster.append(item)
        else:
            if len(current_cluster) > 1:
                groups.append(current_cluster[:])
                used_paths.update(entry["path"] for entry in current_cluster)
            current_cluster = [item]
    if len(current_cluster) > 1:
        groups.append(current_cluster[:])
        used_paths.update(entry["path"] for entry in current_cluster)

    by_name: dict[str, list[dict]] = defaultdict(list)
    for item in items:
        if item["path"] in used_paths or item["root_key"] != "downloads":
            continue
        normalized = item["stem_normalized"]
        if len(normalized) < 4 or not item["width"] or not item["height"]:
            continue
        by_name[f"{normalized}|{item['width']}x{item['height']}"].append(item)

    for key, similar_items in by_name.items():
        if len(similar_items) < 2:
            continue
        sizes = [int(entry["size_bytes"]) for entry in similar_items]
        if max(sizes) / max(1, min(sizes)) > 1.8:
            continue
        similar_items.sort(key=lambda entry: (entry["modified_ts"], entry["path"]), reverse=True)
        groups.append(similar_items)

    normalized_groups: list[dict] = []
    seen_keys: set[tuple[str, ...]] = set()
    for index, group_items in enumerate(groups, start=1):
        raise_if_cancelled(cancel_check)
        key = tuple(sorted(entry["path"] for entry in group_items))
        if key in seen_keys:
            continue
        seen_keys.add(key)
        normalized_groups.append(
            {
                "id": f"similar::{index}",
                "name": group_items[0]["name"],
                "count": len(group_items),
                "total_bytes": sum(int(entry["size_bytes"]) for entry in group_items),
                "items": group_items,
                "reason": "第一版按截图时间、尺寸和大小，或下载图片名称与尺寸聚类。",
            }
        )
    normalized_groups.sort(key=lambda group: (-group["total_bytes"], -group["count"], group["name"].lower()))
    return normalized_groups[:GROUP_LIMIT]


def _flatten_group_items(groups: list[dict], category: str, note_builder) -> list[dict]:
    flattened: list[dict] = []
    for index, group in enumerate(groups, start=1):
        for item in group["items"]:
            flattened.append(
                {
                    **item,
                    "category": category,
                    "group_id": group["id"],
                    "group_label": f"第 {index} 组，共 {group['count']} 张",
                    "reason": note_builder(group, item, index),
                }
            )
    return flattened


def _limit_items(items: list[dict], limit: int = LIST_LIMIT) -> tuple[list[dict], int]:
    if len(items) <= limit:
        return items, 0
    return items[:limit], len(items) - limit


def scan_image_library(
    selected_roots: list[str] | None = None,
    *,
    log_callback=None,
    cancel_check=None,
) -> dict:
    selected_keys = set(selected_roots or [])
    configs = [config for config in IMAGE_ROOTS if not selected_keys or config["key"] in selected_keys]
    if log_callback:
        log_callback(f"准备扫描 {len(configs)} 个图片来源目录。")
    items, root_summaries, truncated = _iter_image_files(configs, log_callback=log_callback, cancel_check=cancel_check)
    raise_if_cancelled(cancel_check)

    screenshots = sorted(
        [item for item in items if item["is_screenshot"]],
        key=lambda item: (item["modified_ts"], item["size_bytes"]),
        reverse=True,
    )
    downloads = sorted(
        [item for item in items if item["root_key"] == "downloads"],
        key=lambda item: (item["modified_ts"], item["size_bytes"]),
        reverse=True,
    )
    large_old = sorted(
        [
            {
                **item,
                "reason": (
                    "大图且长期未使用" if item["size_bytes"] >= LARGE_IMAGE_BYTES and item["age_days"] >= OLD_IMAGE_DAYS
                    else "大图" if item["size_bytes"] >= LARGE_IMAGE_BYTES
                    else "长期未使用图片"
                ),
            }
            for item in items
            if item["size_bytes"] >= LARGE_IMAGE_BYTES or item["age_days"] >= OLD_IMAGE_DAYS
        ],
        key=lambda item: (-int(item["size_bytes"]), -int(item["age_days"]), item["path"]),
    )

    duplicate_groups = _group_duplicates(items, cancel_check=cancel_check, log_callback=log_callback)
    raise_if_cancelled(cancel_check)
    similar_groups = _group_similar(items, cancel_check=cancel_check, log_callback=log_callback)
    raise_if_cancelled(cancel_check)

    screenshot_items, screenshot_truncated = _limit_items(
        [
            {**item, "category": "截图", "reason": "文件名符合截图命名模式。"}
            for item in screenshots
        ]
    )
    download_items, download_truncated = _limit_items(
        [
            {**item, "category": "下载图片", "reason": "图片位于 Downloads 目录。"}
            for item in downloads
        ]
    )
    duplicate_items_raw = _flatten_group_items(
        duplicate_groups,
        "完全重复图片",
        lambda group, item, index: f"与同组其他 {group['count'] - 1} 张图片内容完全一致，建议至少保留 1 张。",
    )
    duplicate_items, duplicate_truncated = _limit_items(duplicate_items_raw, LIST_LIMIT * 2)
    similar_items_raw = _flatten_group_items(
        similar_groups,
        "相似图片",
        lambda group, item, index: group["reason"],
    )
    similar_items, similar_truncated = _limit_items(similar_items_raw, LIST_LIMIT * 2)
    large_old_items, large_old_truncated = _limit_items(
        [{**item, "category": "大图/旧图"} for item in large_old],
        LIST_LIMIT,
    )

    inaccessible_roots = [root for root in root_summaries if root.get("exists") and not root.get("accessible")]
    missing_roots = [root for root in root_summaries if not root.get("exists")]

    return {
        "roots": root_summaries,
        "inaccessible_roots": inaccessible_roots,
        "missing_roots": missing_roots,
        "scan_truncated": truncated,
        "scanned_image_count": len(items),
        "total_bytes": sum(int(item["size_bytes"]) for item in items),
        "screenshots": {
            "items": screenshot_items,
            "total_count": len(screenshots),
            "total_bytes": sum(int(item["size_bytes"]) for item in screenshots),
            "truncated_count": screenshot_truncated,
        },
        "downloads": {
            "items": download_items,
            "total_count": len(downloads),
            "total_bytes": sum(int(item["size_bytes"]) for item in downloads),
            "truncated_count": download_truncated,
        },
        "duplicates": {
            "groups": duplicate_groups,
            "items": duplicate_items,
            "group_count": len(duplicate_groups),
            "total_count": len(duplicate_items_raw),
            "total_bytes": sum(int(item["size_bytes"]) for item in duplicate_items_raw),
            "truncated_count": duplicate_truncated,
        },
        "similar": {
            "groups": similar_groups,
            "items": similar_items,
            "group_count": len(similar_groups),
            "total_count": len(similar_items_raw),
            "total_bytes": sum(int(item["size_bytes"]) for item in similar_items_raw),
            "truncated_count": similar_truncated,
        },
        "large_old": {
            "items": large_old_items,
            "total_count": len(large_old),
            "total_bytes": sum(int(item["size_bytes"]) for item in large_old),
            "truncated_count": large_old_truncated,
        },
    }


def create_image_preview(source_path: str, max_edge: int = 480) -> Path:
    path = Path(source_path).expanduser()
    if not path.is_absolute():
        raise ValueError("图片路径必须是绝对路径。")
    if not path.exists():
        raise FileNotFoundError(f"图片不存在：{path}")
    if path.suffix.lower() not in IMAGE_EXTENSIONS:
        raise ValueError("当前路径不是支持的图片格式。")

    stat_result = path.stat()
    cache_key = hashlib.sha1(
        f"{path}|{int(stat_result.st_mtime)}|{stat_result.st_size}|{max_edge}".encode("utf-8")
    ).hexdigest()
    PREVIEW_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    output_path = PREVIEW_CACHE_DIR / f"{cache_key}.png"
    if output_path.exists():
        return output_path

    subprocess.run(
        [
            "sips",
            "--resampleHeightWidthMax",
            str(max_edge),
            "-s",
            "format",
            "png",
            str(path),
            "--out",
            str(output_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return output_path
