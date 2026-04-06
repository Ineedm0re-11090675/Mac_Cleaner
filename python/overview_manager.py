from __future__ import annotations

from pathlib import Path

from bridge import CleanerBridge
from application_manager import clean_app_residuals, scan_app_residuals
from disk_manager import scan_disk_usage
from image_manager import scan_image_library
from memory_manager import scan_memory_processes, terminate_processes
from startup_manager import disable_startup_items, scan_startup_items


MB = 1024 * 1024
GB = 1024 * MB
OVERVIEW_ITEM_LIMIT = 5


def _format_bytes(value: int | float) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(value or 0)
    index = 0
    while size >= 1024 and index < len(units) - 1:
        size /= 1024
        index += 1
    return f"{size:.2f} {units[index]}"


def _format_age(age_days: int | None) -> str:
    if age_days is None or age_days < 0:
        return "最近使用时间未知"
    return f"{age_days} 天未修改"


def _item_id(prefix: str, raw_key: str) -> str:
    return f"{prefix}::{raw_key}"


def _file_action_item(module_key: str, source_label: str, path: str, size_bytes: int, note: str, age_days: int | None = None) -> dict:
    path_obj = Path(path)
    meta_parts = [source_label, _format_bytes(size_bytes)]
    if age_days is not None:
        meta_parts.append(_format_age(age_days))
    return {
        "id": _item_id(module_key, path),
        "module_key": module_key,
        "name": path_obj.name or path,
        "meta": " | ".join(meta_parts),
        "note": note or "建议手动确认后处理",
        "path": path,
        "reveal_path": path,
        "open_path": path,
        "estimated_bytes": int(size_bytes or 0),
        "action_type": "clean_file",
        "payload": {"path": path},
    }


def _category_action_item(module_key: str, category: dict) -> dict:
    samples = category.get("samples") or []
    first_sample = samples[0] if samples else {}
    reveal_path = str(first_sample.get("path") or "")
    category_name = str(category.get("name") or category.get("key") or "基础清理")
    return {
        "id": _item_id(module_key, f"category::{category.get('key') or category_name}"),
        "module_key": module_key,
        "name": f"{category_name}（整组清理）",
        "meta": f"{int(category.get('file_count', 0) or 0)} 个文件 | {_format_bytes(category.get('total_bytes', 0))}",
        "note": str(category.get("description") or "将按基础清理规则处理这一整组文件。"),
        "path": reveal_path,
        "reveal_path": reveal_path,
        "open_path": reveal_path,
        "estimated_bytes": int(category.get("total_bytes", 0) or 0),
        "action_type": "clean_category",
        "payload": {
            "category_key": category.get("key"),
            "category_name": category_name,
        },
    }


def _startup_action_item(item: dict) -> dict:
    display_path = item.get("action_path") or item.get("plist_path") or item.get("path") or ""
    return {
        "id": _item_id("startup", str(item.get("id") or item.get("name") or "")),
        "module_key": "startup",
        "name": str(item.get("name") or "未命名启动项"),
        "meta": f"{'登录项' if item.get('kind') == 'login_item' else '后台项目'} | 影响 {item.get('impact_level', '未知')}",
        "note": str(item.get("impact_reason") or "建议先确认用途再关闭"),
        "path": display_path,
        "reveal_path": display_path,
        "open_path": display_path,
        "estimated_bytes": 0,
        "action_type": "disable_startup",
        "payload": {
            "id": item.get("id"),
            "kind": item.get("kind"),
            "name": item.get("name"),
            "path": item.get("path"),
            "plist_path": item.get("plist_path"),
        },
    }


def _memory_action_item(item: dict) -> dict:
    display_path = item.get("app_path") or item.get("command") or ""
    role_label = "后台进程" if item.get("is_background") else "前台进程"
    return {
        "id": _item_id("memory", str(item.get("id") or item.get("pid") or "")),
        "module_key": "memory",
        "name": str(item.get("name") or "未知进程"),
        "meta": f"{_format_bytes(item.get('memory_bytes', 0))} | CPU {float(item.get('cpu_percent', 0)):.1f}% | {role_label}",
        "note": str(item.get("recommendation") or "建议先确认后再结束"),
        "path": display_path,
        "reveal_path": item.get("app_path") or "",
        "open_path": item.get("app_path") or "",
        "estimated_bytes": int(item.get("memory_bytes", 0) or 0),
        "action_type": "terminate_process",
        "payload": {
            "id": item.get("id"),
            "pid": item.get("pid"),
            "name": item.get("name"),
            "memory_bytes": item.get("memory_bytes"),
        },
    }


def _application_action_item(item: dict) -> dict:
    return {
        "id": _item_id("applications", str(item.get("path") or item.get("id") or "")),
        "module_key": "applications",
        "name": str(item.get("name") or "未命名残留"),
        "meta": f"{item.get('location_type', '残留目录')} | {_format_bytes(item.get('size_bytes', 0))} | 风险 {item.get('risk_level', '未知')}",
        "note": str(item.get("reason") or item.get("location_description") or "建议先确认后再删除"),
        "path": str(item.get("path") or ""),
        "reveal_path": str(item.get("path") or ""),
        "open_path": str(item.get("path") or ""),
        "estimated_bytes": int(item.get("size_bytes", 0) or 0),
        "risk_level": str(item.get("risk_level") or ""),
        "action_type": "clean_app_residual",
        "payload": {
            "path": item.get("path"),
            "name": item.get("name"),
            "risk_level": item.get("risk_level"),
        },
    }


def _build_card(key: str, title: str, route: str, lines: list[str], alert: bool, items: list[dict] | None = None) -> dict:
    return {
        "key": key,
        "title": title,
        "route": route,
        "status": "建议处理" if alert else "状态良好",
        "ok": not alert,
        "body": "\n".join(lines),
        "items": items or [],
        "actionable_count": len(items or []),
    }


def _collect_file_items(result: dict) -> list[dict]:
    pinned_items: list[dict] = []
    ranked_items: list[dict] = []
    categories = {item.get("key"): item for item in result.get("categories", [])}
    for key in ["user_logs", "trash", "user_cache"]:
        category = categories.get(key)
        if not category:
            continue
        total_bytes = int(category.get("total_bytes", 0) or 0)
        file_count = int(category.get("file_count", 0) or 0)
        if total_bytes <= 0 or file_count <= 0:
            continue
        category_item = _category_action_item("files", category)
        if key == "user_logs":
            pinned_items.append(category_item)
        else:
            ranked_items.append(category_item)

    for finding in result.get("findings", []):
        source_name = {
            "installer_files": "安装文件",
            "download_files": "下载文件",
        }.get(finding.get("key"), "候选文件")
        for file in finding.get("files", []):
            ranked_items.append(
                _file_action_item(
                    "files",
                    source_name,
                    str(file.get("path") or ""),
                    int(file.get("size", 0) or 0),
                    str(file.get("note") or finding.get("name") or "建议手动确认"),
                    file.get("age_days"),
                )
            )

    for file in result.get("large_files", {}).get("files", []):
        ranked_items.append(
            _file_action_item(
                "files",
                "大型文件",
                str(file.get("path") or ""),
                int(file.get("size", 0) or 0),
                str(file.get("note") or "大型文件 Top 10"),
                file.get("age_days"),
            )
        )

    ranked_items.sort(key=lambda item: (-item["estimated_bytes"], item["path"]))
    combined = pinned_items + [item for item in ranked_items if item["id"] not in {p["id"] for p in pinned_items}]
    return combined[:OVERVIEW_ITEM_LIMIT]


def _file_card(bridge: CleanerBridge) -> dict:
    result = bridge.scan(["user_cache", "user_logs", "trash"])
    categories = {item.get("key"): item for item in result.get("categories", [])}
    candidate_bytes = int(result.get("grand_total_candidate_bytes", 0) or 0)
    candidate_count = sum(int(item.get("file_count", 0) or 0) for item in result.get("findings", []))
    largest = max((int(item.get("size", 0) or 0) for item in result.get("large_files", {}).get("files", [])), default=0)
    logs_bytes = int((categories.get("user_logs") or {}).get("total_bytes", 0) or 0)
    logs_count = int((categories.get("user_logs") or {}).get("file_count", 0) or 0)
    cache_bytes = int((categories.get("user_cache") or {}).get("total_bytes", 0) or 0)
    trash_bytes = int((categories.get("trash") or {}).get("total_bytes", 0) or 0)
    alert = (
        candidate_bytes >= 500 * MB
        or candidate_count >= 20
        or largest >= GB
        or logs_bytes >= 20 * MB
    )
    if alert:
        lines = [
            f"候选文件: {candidate_count} 个",
            f"手动确认空间: {_format_bytes(candidate_bytes)}",
            f"大型文件峰值: {_format_bytes(largest)}",
            f"用户缓存: {_format_bytes(cache_bytes)}",
            f"用户日志: {_format_bytes(logs_bytes)}（{logs_count} 个）",
            f"废纸篓: {_format_bytes(trash_bytes)}",
        ]
    else:
        lines = ["完美，暂无明显可改进项目。"]
    return _build_card("files", "文件清理", "files", lines, alert, _collect_file_items(result) if alert else [])


def _cache_card(bridge: CleanerBridge) -> dict:
    result = bridge.scan_app_caches([])
    total_bytes = int(result.get("total_bytes", 0) or 0)
    categories = sorted(result.get("categories", []), key=lambda item: int(item.get("total_bytes", 0) or 0), reverse=True)
    top = categories[:3]
    alert = total_bytes >= 300 * MB or any(int(item.get("total_bytes", 0) or 0) >= 200 * MB for item in top)
    if alert:
        lines = [f"缓存总空间: {_format_bytes(total_bytes)}"]
        for item in top:
            if int(item.get("total_bytes", 0) or 0) <= 0:
                continue
            lines.append(f"{item.get('name')}: {_format_bytes(item.get('total_bytes', 0))}")
    else:
        lines = ["完美，暂无明显可改进项目。"]

    files = sorted(result.get("files", []), key=lambda item: int(item.get("size", 0) or 0), reverse=True)
    items = [
        _file_action_item(
            "caches",
            str(item.get("group") or "软件缓存"),
            str(item.get("path") or ""),
            int(item.get("size", 0) or 0),
            str(item.get("note") or "缓存文件"),
            item.get("age_days"),
        )
        for item in files[:OVERVIEW_ITEM_LIMIT]
    ] if alert else []
    return _build_card("caches", "软件缓存", "caches", lines, alert, items)


def _startup_card() -> dict:
    try:
        result = scan_startup_items(["login_items", "launch_agents"])
    except Exception:
        return _build_card(
            "startup",
            "开机启动",
            "startup",
            ["需要自动化权限后才能读取登录项，请先到设置页打开自动化权限。"],
            True,
            [],
        )
    items = sorted(
        result.get("items", []),
        key=lambda item: (-int(item.get("impact_score", 0) or 0), str(item.get("name") or "")),
    )
    high_impact = int(result.get("high_impact_count", 0) or 0)
    total_count = int(result.get("total_count", 0) or 0)
    alert = high_impact >= 1 or total_count >= 6
    if alert:
        lines = [f"启动项: {total_count} 个", f"高影响项目: {high_impact} 个"]
        for item in items[:3]:
            lines.append(f"{item.get('name')}: 影响 {item.get('impact_level')}")
    else:
        lines = ["完美，暂无明显可改进项目。"]
    action_items = [_startup_action_item(item) for item in items[:OVERVIEW_ITEM_LIMIT]] if alert else []
    return _build_card("startup", "开机启动", "startup", lines, alert, action_items)


def _memory_card() -> dict:
    result = scan_memory_processes(20)
    items = result.get("items") or []
    recommended = [
        item for item in items
        if item.get("can_terminate") and item.get("risk_level") == "低" and int(item.get("memory_bytes", 0) or 0) >= 300 * MB
    ]
    recommended.sort(key=lambda item: (-int(item.get("memory_bytes", 0) or 0), -float(item.get("cpu_percent", 0) or 0)))
    alert = bool(recommended)
    if alert:
        lines = [f"低风险高占用进程: {len(recommended)} 个"]
        for item in recommended[:3]:
            lines.append(f"{item.get('name')}: {_format_bytes(item.get('memory_bytes', 0))}")
    else:
        lines = ["完美，暂无明显可改进项目。"]
    action_items = [_memory_action_item(item) for item in recommended[:OVERVIEW_ITEM_LIMIT]] if alert else []
    return _build_card("memory", "内存管理", "memory", lines, alert, action_items)


def _applications_card() -> dict:
    result = scan_app_residuals()
    items = sorted(
        result.get("items", []),
        key=lambda item: ({"低": 0, "中": 1, "高": 2}.get(str(item.get("risk_level") or ""), 3), -int(item.get("size_bytes", 0) or 0)),
    )
    total_count = int(result.get("total_count", 0) or 0)
    total_bytes = int(result.get("total_bytes", 0) or 0)
    alert = total_count >= 3 or total_bytes >= 300 * MB
    if alert:
        lines = [f"疑似残留: {total_count} 个", f"残留空间: {_format_bytes(total_bytes)}"]
        groups = result.get("groups") or []
        for item in groups[:3]:
            lines.append(f"{item.get('name')}: {_format_bytes(item.get('total_bytes', 0))}")
    else:
        lines = ["完美，暂无明显可改进项目。"]
    action_items = [_application_action_item(item) for item in items[:OVERVIEW_ITEM_LIMIT]] if alert else []
    return _build_card("applications", "应用程序", "applications", lines, alert, action_items)


def _images_card() -> dict:
    result = scan_image_library(["desktop", "downloads", "pictures"])
    screenshot_count = int(result.get("screenshots", {}).get("total_count", 0) or 0)
    similar_groups = int(result.get("similar", {}).get("group_count", 0) or 0)
    duplicate_groups = int(result.get("duplicates", {}).get("group_count", 0) or 0)
    large_old_bytes = int(result.get("large_old", {}).get("total_bytes", 0) or 0)
    alert = screenshot_count >= 80 or similar_groups >= 3 or duplicate_groups >= 1 or large_old_bytes >= GB
    if alert:
        lines = [
            f"截图: {screenshot_count} 张",
            f"相似图片: {similar_groups} 组",
            f"完全重复图片: {duplicate_groups} 组",
            f"大图 / 旧图空间: {_format_bytes(large_old_bytes)}",
        ]
    else:
        lines = ["完美，暂无明显可改进项目。"]

    ranked_candidates: list[tuple[int, dict]] = []
    for item in result.get("duplicates", {}).get("items", []):
        ranked_candidates.append((100, item))
    for item in result.get("screenshots", {}).get("items", []):
        ranked_candidates.append((95, item))
    for item in result.get("similar", {}).get("items", []):
        ranked_candidates.append((90, item))
    for item in result.get("large_old", {}).get("items", []):
        ranked_candidates.append((85, item))
    for item in result.get("downloads", {}).get("items", []):
        ranked_candidates.append((80, item))

    ranked_candidates.sort(
        key=lambda pair: (
            -pair[0],
            -int(pair[1].get("age_days", 0) or 0),
            -int(pair[1].get("size_bytes", 0) or 0),
            str(pair[1].get("path") or ""),
        )
    )
    items = [
        _file_action_item(
            "images",
            str(item.get("category") or "图片管理"),
            str(item.get("path") or ""),
            int(item.get("size_bytes", 0) or 0),
            str(item.get("reason") or "建议手动确认"),
            item.get("age_days"),
        )
        for _, item in ranked_candidates[:OVERVIEW_ITEM_LIMIT]
    ] if alert else []
    return _build_card("images", "图片管理", "images", lines, alert, items)


def _space_card() -> dict:
    result = scan_disk_usage(["desktop", "downloads", "documents", "library"])
    roots = sorted(result.get("roots", []), key=lambda item: int(item.get("total_bytes", 0) or 0), reverse=True)
    top_root = roots[0] if roots else None
    top_file = (result.get("large_files") or [None])[0]
    top_root_bytes = int((top_root or {}).get("total_bytes", 0) or 0)
    top_file_bytes = int((top_file or {}).get("size_bytes", 0) or 0)
    alert = top_root_bytes >= 5 * GB or top_file_bytes >= GB
    if alert:
        lines = []
        if top_root:
            lines.append(f"最占空间目录: {top_root.get('name')} · {_format_bytes(top_root_bytes)}")
        if top_file:
            lines.append(f"最大文件: {top_file.get('name')} · {_format_bytes(top_file_bytes)}")
        lines.append(f"总扫描空间: {_format_bytes(result.get('total_bytes', 0))}")
    else:
        lines = ["完美，暂无明显可改进项目。"]

    items = [
        _file_action_item(
            "space",
            str(item.get("source_root") or "磁盘空间"),
            str(item.get("path") or ""),
            int(item.get("size_bytes", 0) or 0),
            "磁盘空间分析里最占空间的大文件",
        )
        for item in (result.get("large_files") or [])[:OVERVIEW_ITEM_LIMIT]
    ] if alert else []
    return _build_card("space", "磁盘空间", "space", lines, alert, items)


def scan_overview(bridge: CleanerBridge | None = None, progress_callback=None, skip_keys: set[str] | None = None) -> dict:
    bridge = bridge or CleanerBridge()
    skip_keys = set(skip_keys or set())
    steps = [
        ("files", "正在检查文件清理...", lambda: _file_card(bridge)),
        ("images", "正在检查图片管理...", _images_card),
        ("space", "正在检查磁盘空间...", _space_card),
        ("caches", "正在检查软件缓存...", lambda: _cache_card(bridge)),
        ("startup", "正在检查开机启动...", _startup_card),
        ("memory", "正在检查内存管理...", _memory_card),
        ("applications", "正在检查应用程序...", _applications_card),
    ]
    cards = []
    total = len(steps)
    for index, (key, label, builder) in enumerate(steps):
        if key in skip_keys:
            continue
        if progress_callback:
            progress_callback(index, total, label)
        cards.append(builder())
    if progress_callback:
        progress_callback(total, total, "正在汇总检查结果...")
    issue_count = sum(1 for card in cards if not card["ok"])
    actionable_count = sum(len(card["items"]) for card in cards)
    return {
        "cards": cards,
        "issue_count": issue_count,
        "actionable_count": actionable_count,
        "all_good": issue_count == 0,
    }


def execute_overview_actions(selected_items: list[dict] | None = None, bridge: CleanerBridge | None = None) -> dict:
    bridge = bridge or CleanerBridge()
    selected_items = selected_items or []

    clean_categories = [item.get("payload", {}).get("category_key") for item in selected_items if item.get("action_type") == "clean_category"]
    clean_file_paths = [item.get("payload", {}).get("path") for item in selected_items if item.get("action_type") == "clean_file"]
    startup_items = [item.get("payload", {}) for item in selected_items if item.get("action_type") == "disable_startup"]
    process_items = [item.get("payload", {}) for item in selected_items if item.get("action_type") == "terminate_process"]
    residual_items = [item.get("payload", {}) for item in selected_items if item.get("action_type") == "clean_app_residual"]

    modules: list[dict] = []
    total_success = 0
    total_failed = 0
    total_reclaimed_bytes = 0
    deleted_paths: list[str] = []
    disabled_ids: list[str] = []
    terminated_ids: list[str] = []
    residual_paths: list[str] = []
    cleaned_category_keys: list[str] = []

    if clean_categories:
        result = bridge.clean(clean_categories, dry_run=False)
        success = sum(int(item.get("deleted_files", 0) or 0) for item in result.get("results", []))
        failed = sum(
            len(item.get("skipped_paths", [])) + int(item.get("skipped_paths_truncated", 0) or 0)
            for item in result.get("results", [])
        )
        reclaimed = sum(int(item.get("reclaimed_bytes", 0) or 0) for item in result.get("results", []))
        total_success += success
        total_failed += failed
        total_reclaimed_bytes += reclaimed
        cleaned_category_keys.extend(item.get("key") for item in result.get("results", []) if int(item.get("deleted_files", 0) or 0) > 0)
        modules.append(
            {
                "title": "基础清理",
                "success_count": success,
                "failed_count": failed,
                "reclaimed_bytes": reclaimed,
            }
        )

    if clean_file_paths:
        result = bridge.clean_files(clean_file_paths, dry_run=False)
        item = (result.get("results") or [{}])[0]
        success = int(item.get("deleted_files", 0) or 0)
        failed = len(item.get("skipped_paths", [])) + int(item.get("skipped_paths_truncated", 0) or 0)
        reclaimed = int(item.get("reclaimed_bytes", 0) or 0)
        total_success += success
        total_failed += failed
        total_reclaimed_bytes += reclaimed
        deleted_paths.extend(item.get("deleted_paths", []))
        modules.append(
            {
                "title": "文件 / 图片 / 缓存 / 大文件",
                "success_count": success,
                "failed_count": failed,
                "reclaimed_bytes": reclaimed,
            }
        )

    if startup_items:
        result = disable_startup_items(startup_items)
        success = int(result.get("disabled_count", 0) or 0)
        failed = int(result.get("failed_count", 0) or 0)
        total_success += success
        total_failed += failed
        disabled_ids.extend(item.get("id") for item in result.get("results", []) if item.get("success"))
        modules.append(
            {
                "title": "开机启动",
                "success_count": success,
                "failed_count": failed,
                "reclaimed_bytes": 0,
            }
        )

    if process_items:
        result = terminate_processes(process_items)
        success = int(result.get("terminated_count", 0) or 0)
        failed = int(result.get("failed_count", 0) or 0)
        reclaimed = int(result.get("reclaimed_bytes_estimate", 0) or 0)
        total_success += success
        total_failed += failed
        total_reclaimed_bytes += reclaimed
        terminated_ids.extend(f"process::{item.get('pid')}" for item in result.get("results", []) if item.get("success"))
        modules.append(
            {
                "title": "内存管理",
                "success_count": success,
                "failed_count": failed,
                "reclaimed_bytes": reclaimed,
            }
        )

    if residual_items:
        result = clean_app_residuals(residual_items)
        success = int(result.get("deleted_count", 0) or 0)
        failed = int(result.get("failed_count", 0) or 0)
        reclaimed = int(result.get("reclaimed_bytes", 0) or 0)
        total_success += success
        total_failed += failed
        total_reclaimed_bytes += reclaimed
        residual_paths.extend(item.get("path") for item in result.get("results", []) if item.get("success"))
        modules.append(
            {
                "title": "应用程序",
                "success_count": success,
                "failed_count": failed,
                "reclaimed_bytes": reclaimed,
            }
        )

    return {
        "handled_count": len(selected_items),
        "success_count": total_success,
        "failed_count": total_failed,
        "reclaimed_bytes": total_reclaimed_bytes,
        "modules": modules,
        "deleted_paths": deleted_paths,
        "disabled_ids": disabled_ids,
        "terminated_ids": terminated_ids,
        "residual_paths": residual_paths,
        "cleaned_category_keys": cleaned_category_keys,
    }
