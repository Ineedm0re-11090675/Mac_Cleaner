from __future__ import annotations

import json
import os
import plistlib
import shutil
import subprocess
from pathlib import Path


HOME = Path.home()
LAUNCH_AGENTS_DIR = HOME / "Library" / "LaunchAgents"
DISABLED_LAUNCH_AGENTS_DIR = HOME / "Library" / "LaunchAgentsDisabled"


def _escape_applescript_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _run_osascript_jxa(script: str) -> str:
    completed = subprocess.run(
        ["osascript", "-l", "JavaScript"],
        input=script,
        text=True,
        capture_output=True,
        check=True,
    )
    return completed.stdout.strip()


def _friendly_osascript_failure(exc: subprocess.CalledProcessError) -> str:
    combined = "\n".join(part for part in [exc.stdout, exc.stderr] if part).strip()
    lowered = combined.lower()

    if (
        "not authorized to send apple events to system events" in lowered
        or "(-1743)" in lowered
        or "权限" in combined and "System Events" in combined
    ):
        return (
            "没有权限关闭这个“登录项”。\n"
            "请到“系统设置 -> 隐私与安全性 -> 自动化”，允许当前运行的 Python 或终端控制“System Events”，"
            "然后重新扫描再试一次。"
        )

    if "login item not found" in lowered:
        return "没有找到这个登录项。它可能已经被系统移除，或者名称发生了变化。请重新扫描后再试。"

    return combined or str(exc)


def _normalize_name(value: str) -> str:
    return "".join(ch.lower() for ch in value if ch.isalnum())


def _standard_app_locations() -> list[Path]:
    return [Path("/Applications"), HOME / "Applications"]


def _find_bundle_root(path: Path) -> Path | None:
    current = path.resolve()
    if current.suffix == ".app":
        return current
    for parent in current.parents:
        if parent.suffix == ".app":
            return parent
    return None


def _search_app_path_by_name(name: str) -> str:
    normalized = _normalize_name(name)
    if not normalized:
        return ""

    candidates: list[Path] = []
    for base in _standard_app_locations():
        if not base.exists():
            continue
        for app_path in base.glob("*.app"):
            candidates.append(app_path)
        for subdir in base.iterdir():
            if subdir.is_dir():
                for app_path in subdir.glob("*.app"):
                    candidates.append(app_path)

    exact = []
    fuzzy = []
    for path in candidates:
        app_name = path.stem
        normalized_app = _normalize_name(app_name)
        if normalized_app == normalized:
            exact.append(path)
        elif normalized in normalized_app or normalized_app in normalized:
            fuzzy.append(path)

    if exact:
        return str(sorted(exact)[0])
    if fuzzy:
        return str(sorted(fuzzy)[0])
    return ""


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


def _estimate_impact(item: dict) -> tuple[str, str, int]:
    score = 1
    reasons: list[str] = []
    name_lower = str(item.get("name", "")).lower()
    note_lower = str(item.get("note", "")).lower()
    action_path = str(item.get("action_path", ""))
    size_bytes = int(item.get("size_bytes") or 0)

    if item.get("kind") == "login_item":
        score += 1
        reasons.append("登录后会直接启动应用")
        if not item.get("hidden"):
            score += 1
            reasons.append("窗口不会隐藏")
    else:
        if item.get("run_at_load"):
            score += 1
            reasons.append("登录后会自动加载后台任务")
        if item.get("start_interval"):
            score += 1
            reasons.append(f"会按固定间隔唤醒（{item['start_interval']} 秒）")
        if item.get("watch_paths"):
            score += 1
            reasons.append("会持续监听文件变化")

    heavy_keywords = [
        "wechat", "微信", "qq", "dingtalk", "clash", "steam",
        "chrome", "edge", "firefox", "netease", "music", "aliyun",
        "adrive", "logi", "downloadmanager",
    ]
    updater_keywords = ["updater", "update", "keystone", "wake"]

    if any(keyword in name_lower for keyword in updater_keywords) or any(keyword in note_lower for keyword in updater_keywords):
        score -= 1
        reasons.append("更像后台更新器")

    if any(keyword in name_lower for keyword in heavy_keywords):
        score += 1
        reasons.append("应用本身较重或常驻")

    if action_path.endswith(".app"):
        if size_bytes >= 500 * 1024 * 1024:
            score += 1
            reasons.append("应用体积较大")
        elif size_bytes >= 150 * 1024 * 1024:
            reasons.append("应用体积中等")

    score = max(1, min(score, 3))
    level = {1: "低", 2: "中", 3: "高"}[score]
    if not reasons:
        reasons.append("估计影响较小")
    return level, "；".join(reasons), score


def _build_login_items() -> list[dict]:
    script = r"""
var se = Application("System Events");
var items = se.loginItems();
var out = [];
for (var i = 0; i < items.length; i++) {
  var item = items[i];
  var name = "";
  var path = "";
  var hidden = false;
  try { name = item.name(); } catch (e) {}
  try { path = item.path(); } catch (e) {}
  try { hidden = item.hidden(); } catch (e) {}
  out.push({name: name, path: path || "", hidden: !!hidden});
}
JSON.stringify(out);
"""
    raw = _run_osascript_jxa(script)
    parsed = json.loads(raw or "[]")
    items: list[dict] = []
    for record in parsed:
        name = str(record.get("name") or "").strip()
        path = str(record.get("path") or "").strip()
        hidden = bool(record.get("hidden"))
        if not path:
            path = _search_app_path_by_name(name)

        action_path = path
        size_bytes = 0
        if action_path:
            bundle_root = _find_bundle_root(Path(action_path))
            target = bundle_root or Path(action_path)
            if target.exists():
                size_bytes = _du_size_bytes(target) if target.is_dir() else int(target.stat().st_size)
                action_path = str(target)

        item = {
            "id": f"login_item::{name}",
            "kind": "login_item",
            "group": "登录项",
            "name": name or "未命名登录项",
            "path": action_path,
            "hidden": hidden,
            "note": "系统登录项",
            "size_bytes": size_bytes,
            "action_path": action_path,
            "plist_path": "",
            "label": "",
            "run_at_load": False,
            "start_interval": 0,
            "watch_paths": [],
        }
        level, reason, score = _estimate_impact(item)
        item["impact_level"] = level
        item["impact_reason"] = reason
        item["impact_score"] = score
        items.append(item)
    return items


def _build_launch_agents() -> list[dict]:
    items: list[dict] = []
    if not LAUNCH_AGENTS_DIR.exists():
        return items

    for plist_path in sorted(LAUNCH_AGENTS_DIR.glob("*.plist")):
        try:
            data = plistlib.loads(plist_path.read_bytes())
        except Exception:
            continue

        label = str(data.get("Label") or plist_path.stem)
        args = data.get("ProgramArguments") or []
        program = str(data.get("Program") or "")
        resolved_path = program or (str(args[0]) if args else "")
        action_path = resolved_path if resolved_path and Path(resolved_path).exists() else str(plist_path)
        size_bytes = 0
        target = Path(action_path)
        bundle_root = _find_bundle_root(target) if action_path else None
        if bundle_root and bundle_root.exists():
            size_bytes = _du_size_bytes(bundle_root)
            action_path = str(bundle_root)
        elif target.exists() and target.is_file():
            size_bytes = int(target.stat().st_size)

        item = {
            "id": f"launch_agent::{plist_path}",
            "kind": "launch_agent",
            "group": "后台项目",
            "name": label,
            "path": action_path,
            "hidden": False,
            "note": "用户后台项目",
            "size_bytes": size_bytes,
            "action_path": action_path,
            "plist_path": str(plist_path),
            "label": label,
            "run_at_load": bool(data.get("RunAtLoad")),
            "start_interval": int(data.get("StartInterval") or 0),
            "watch_paths": list(data.get("WatchPaths") or []),
        }
        level, reason, score = _estimate_impact(item)
        item["impact_level"] = level
        item["impact_reason"] = reason
        item["impact_score"] = score
        items.append(item)
    return items


def scan_startup_items(selected_groups: list[str] | None = None) -> dict:
    selected = set(selected_groups or [])
    include_all = not selected
    items: list[dict] = []

    if include_all or "login_items" in selected:
        items.extend(_build_login_items())
    if include_all or "launch_agents" in selected:
        items.extend(_build_launch_agents())

    groups = []
    for group_key, group_name in [("login_items", "登录项"), ("launch_agents", "后台项目")]:
        group_items = [item for item in items if item["group"] == group_name]
        high_count = sum(1 for item in group_items if item["impact_level"] == "高")
        groups.append({
            "key": group_key,
            "name": group_name,
            "count": len(group_items),
            "high_impact_count": high_count,
        })

    items.sort(
        key=lambda item: (
            {"高": 0, "中": 1, "低": 2}.get(item["impact_level"], 3),
            item["group"],
            item["name"].lower(),
        )
    )

    return {
        "groups": groups,
        "items": items,
        "total_count": len(items),
        "high_impact_count": sum(1 for item in items if item["impact_level"] == "高"),
    }


def _disable_login_item(name: str, path: str) -> None:
    name_literal = json.dumps(name)
    path_literal = json.dumps(path or "")
    script = f"""
var se = Application("System Events");
var targetName = {name_literal};
var targetPath = {path_literal};
var items = se.loginItems();
var matched = [];

for (var i = 0; i < items.length; i++) {{
  var item = items[i];
  var currentName = "";
  var currentPath = "";
  try {{ currentName = item.name(); }} catch (e) {{}}
  try {{ currentPath = item.path() || ""; }} catch (e) {{}}
  if (currentName === targetName) {{
    if (!targetPath || !currentPath || currentPath === targetPath) {{
      matched.push(item);
    }}
  }}
}}

if (!matched.length && targetPath) {{
  for (var j = 0; j < items.length; j++) {{
    var fallbackItem = items[j];
    var fallbackName = "";
    try {{ fallbackName = fallbackItem.name(); }} catch (e) {{}}
    if (fallbackName === targetName) {{
      matched.push(fallbackItem);
    }}
  }}
}}

if (!matched.length) {{
  throw new Error("Login item not found: " + targetName);
}}

matched[0].delete();
"ok";
"""
    try:
        _run_osascript_jxa(script)
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(_friendly_osascript_failure(exc)) from exc


def _disable_launch_agent(plist_path: Path) -> Path:
    DISABLED_LAUNCH_AGENTS_DIR.mkdir(parents=True, exist_ok=True)
    destination = DISABLED_LAUNCH_AGENTS_DIR / plist_path.name
    if destination.exists():
        destination = DISABLED_LAUNCH_AGENTS_DIR / f"{plist_path.stem}.{int(plist_path.stat().st_mtime)}.plist"

    subprocess.run(
        ["launchctl", "bootout", f"gui/{os.getuid()}", str(plist_path)],
        check=False,
        capture_output=True,
        text=True,
    )
    shutil.move(str(plist_path), str(destination))
    return destination


def disable_startup_items(selected_items: list[dict] | None = None) -> dict:
    results = []
    for item in selected_items or []:
        item_id = str(item.get("id") or "")
        kind = str(item.get("kind") or "")
        name = str(item.get("name") or "")
        try:
            if kind == "login_item":
                _disable_login_item(name, str(item.get("path") or ""))
                results.append({
                    "id": item_id,
                    "name": name,
                    "kind": kind,
                    "success": True,
                    "message": "已从登录项中移除",
                })
            elif kind == "launch_agent":
                plist_path = Path(str(item.get("plist_path") or ""))
                if not plist_path.exists():
                    raise FileNotFoundError(f"LaunchAgent 文件不存在：{plist_path}")
                destination = _disable_launch_agent(plist_path)
                results.append({
                    "id": item_id,
                    "name": name,
                    "kind": kind,
                    "success": True,
                    "message": f"已禁用并移动到 {destination}",
                })
            else:
                raise ValueError(f"不支持的启动项类型：{kind}")
        except Exception as exc:
            results.append({
                "id": item_id,
                "name": name or item_id,
                "kind": kind,
                "success": False,
                "message": str(exc),
            })

    return {
        "results": results,
        "disabled_count": sum(1 for item in results if item["success"]),
        "failed_count": sum(1 for item in results if not item["success"]),
    }
