from __future__ import annotations

import heapq
import os
from pathlib import Path

from task_support import raise_if_cancelled


HOME = Path.home()
DISK_ROOTS = [
    {"key": "desktop", "name": "桌面", "path": HOME / "Desktop"},
    {"key": "downloads", "name": "下载", "path": HOME / "Downloads"},
    {"key": "documents", "name": "文稿", "path": HOME / "Documents"},
    {"key": "library", "name": "Library", "path": HOME / "Library"},
]
TOP_CHILD_LIMIT = 12
TOP_FILE_LIMIT = 36


def _safe_stat(path: Path) -> os.stat_result | None:
    try:
        return path.stat()
    except OSError:
        return None


def _walk_size(
    path: Path,
    top_files_heap: list[tuple[int, str, dict]],
    source_root: dict,
    *,
    cancel_check=None,
) -> tuple[int, int]:
    raise_if_cancelled(cancel_check)
    if path.is_symlink():
        return 0, 0

    if path.is_file():
        stat_result = _safe_stat(path)
        if not stat_result:
            return 0, 0
        size = int(stat_result.st_size)
        entry = {
            "path": str(path),
            "name": path.name,
            "size_bytes": size,
            "source_root": source_root["name"],
            "source_key": source_root["key"],
            "is_directory": False,
        }
        if len(top_files_heap) < TOP_FILE_LIMIT:
            heapq.heappush(top_files_heap, (size, str(path), entry))
        elif size > top_files_heap[0][0]:
            heapq.heapreplace(top_files_heap, (size, str(path), entry))
        return size, 1

    total_size = 0
    total_files = 0
    try:
        with os.scandir(path) as iterator:
            for entry in iterator:
                entry_path = Path(entry.path)
                size, file_count = _walk_size(
                    entry_path,
                    top_files_heap,
                    source_root,
                    cancel_check=cancel_check,
                )
                total_size += size
                total_files += file_count
    except OSError:
        return total_size, total_files
    return total_size, total_files


def scan_disk_usage(selected_roots: list[str] | None = None, *, log_callback=None, cancel_check=None) -> dict:
    selected_keys = set(selected_roots or [])
    root_configs = [config for config in DISK_ROOTS if not selected_keys or config["key"] in selected_keys]

    root_reports: list[dict] = []
    top_files_heap: list[tuple[int, str, dict]] = []
    grand_total_bytes = 0
    grand_total_files = 0

    for config in root_configs:
        raise_if_cancelled(cancel_check)
        root = Path(config["path"])
        if log_callback:
            log_callback(f"正在统计目录：{config['name']}")
        root_report = {
            "key": config["key"],
            "name": config["name"],
            "path": str(root),
            "exists": root.exists(),
            "accessible": False,
            "error": "",
            "total_bytes": 0,
            "file_count": 0,
            "children": [],
        }
        if not root.exists():
            root_reports.append(root_report)
            continue

        child_reports: list[dict] = []
        try:
            children = sorted(root.iterdir(), key=lambda item: item.name.lower())
            root_report["accessible"] = True
        except OSError:
            root_report["error"] = "没有访问权限或目录读取失败"
            root_reports.append(root_report)
            continue

        for child in children:
            raise_if_cancelled(cancel_check)
            if child.name.startswith("."):
                continue
            size_bytes, file_count = _walk_size(child, top_files_heap, config, cancel_check=cancel_check)
            if size_bytes <= 0:
                continue
            child_reports.append(
                {
                    "path": str(child),
                    "name": child.name,
                    "size_bytes": size_bytes,
                    "file_count": file_count,
                    "is_directory": child.is_dir(),
                    "kind": "目录" if child.is_dir() else "文件",
                    "source_root": config["name"],
                }
            )
            root_report["total_bytes"] += size_bytes
            root_report["file_count"] += file_count

        child_reports.sort(key=lambda item: (-item["size_bytes"], item["name"].lower()))
        root_report["children"] = child_reports[:TOP_CHILD_LIMIT]
        root_reports.append(root_report)
        grand_total_bytes += int(root_report["total_bytes"])
        grand_total_files += int(root_report["file_count"])

    large_files = [entry for _, _, entry in sorted(top_files_heap, key=lambda item: (-item[0], item[1]))]

    return {
        "roots": root_reports,
        "large_files": large_files,
        "total_bytes": grand_total_bytes,
        "total_file_count": grand_total_files,
        "root_count": len(root_reports),
        "inaccessible_roots": [item for item in root_reports if item["exists"] and not item["accessible"]],
        "missing_roots": [item for item in root_reports if not item["exists"]],
    }
