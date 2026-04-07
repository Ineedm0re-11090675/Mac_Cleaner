from __future__ import annotations

import getpass
import os
import signal
import subprocess
import time
from pathlib import Path

from task_support import raise_if_cancelled


CURRENT_USER = getpass.getuser()
SELF_PIDS = {os.getpid(), os.getppid()}
DISPLAY_LIMIT = 20
MIN_MEMORY_BYTES = 20 * 1024 * 1024
HIGH_MEMORY_BYTES = 300 * 1024 * 1024
QUICK_RECLAIM_MIN_MEMORY_BYTES = 80 * 1024 * 1024
QUICK_RECLAIM_MIN_CPU_PERCENT = 5.0
QUICK_RECLAIM_LIMIT = 8

PROTECTED_NAMES = {
    "windowserver",
    "kernel_task",
    "launchd",
    "loginwindow",
    "finder",
    "dock",
    "systemuiserver",
    "controlcenter",
    "notificationcenter",
}

HELPER_ROLE_LABELS = {
    "updater": "更新器",
    "daemon": "后台服务",
    "agent": "后台代理",
    "service": "服务进程",
    "renderer": "渲染子进程",
    "gpu": "图形子进程",
    "helper": "辅助进程",
    "utility": "工具子进程",
    "crashpad": "崩溃上报进程",
    "plugin": "插件进程",
    "broker": "中转进程",
}


def _run_ps() -> list[str]:
    completed = subprocess.run(
        ["ps", "axww", "-o", "pid=,ppid=,user=,%cpu=,rss=,state=,tty=,command="],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.splitlines()


def _parse_ps_line(line: str) -> dict | None:
    parts = line.strip().split(None, 7)
    if len(parts) < 8:
        return None

    try:
        pid = int(parts[0])
        ppid = int(parts[1])
        user = parts[2]
        cpu_percent = float(parts[3])
        rss_kb = int(parts[4])
        state = parts[5]
        tty = parts[6]
        command = parts[7]
    except (TypeError, ValueError):
        return None

    return {
        "pid": pid,
        "ppid": ppid,
        "user": user,
        "cpu_percent": cpu_percent,
        "rss_kb": rss_kb,
        "state": state,
        "tty": tty,
        "command": command,
    }


def _extract_app_path(command: str) -> str:
    if not command.startswith("/"):
        return ""
    marker_index = command.find(".app")
    if marker_index == -1:
        return ""
    return command[: marker_index + 4]


def _base_process_name(command: str) -> str:
    command = command.strip()
    if not command:
        return "未知进程"
    first_segment = command.split(" --", 1)[0].strip()
    if first_segment.startswith("/"):
        return Path(first_segment).name or first_segment
    return first_segment.split()[0]


def _role_from_command(command: str) -> str:
    lowered = command.lower()
    if "windowserver" in lowered:
        return "protected"
    if "crashpad" in lowered:
        return "crashpad"
    if "updater" in lowered or "update" in lowered or "keystone" in lowered:
        return "updater"
    if "daemon" in lowered:
        return "daemon"
    if " agent" in lowered or ".agent" in lowered or "/agent" in lowered:
        return "agent"
    if "--type=renderer" in lowered or "(renderer)" in lowered or " renderer" in lowered:
        return "renderer"
    if "--type=gpu" in lowered or "(gpu)" in lowered or " gpu" in lowered:
        return "gpu"
    if "--type=utility" in lowered or "utility-sub-type" in lowered:
        return "utility"
    if "helper" in lowered:
        return "helper"
    if "plugin" in lowered:
        return "plugin"
    if "broker" in lowered:
        return "broker"
    if "service" in lowered:
        return "service"
    return "main"


def _app_family_name(app_path: str, command: str) -> str:
    if app_path:
        return Path(app_path).stem
    return _base_process_name(command)


def _display_name(app_family: str, role: str) -> str:
    if role == "main":
        return app_family
    label = HELPER_ROLE_LABELS.get(role)
    if label:
        return f"{app_family} {label}"
    return app_family


def _is_background(role: str, command: str) -> bool:
    if role in {"updater", "daemon", "agent", "service", "renderer", "gpu", "helper", "utility", "crashpad", "plugin", "broker"}:
        return True
    lowered = command.lower()
    return any(token in lowered for token in ["--type=", "--headless", "--launchd"])


def _is_protected_process(pid: int, command: str, app_family: str) -> tuple[bool, str]:
    lowered = command.lower()
    if pid in SELF_PIDS or "python/desktop_app/main.py" in lowered or "python/gui.py" in lowered or app_family.lower() == "codex":
        return True, "这是当前清理工具自己的进程，不能在这里结束。"
    if app_family.lower() in PROTECTED_NAMES:
        return True, "这是系统核心或桌面核心进程，不建议关闭。"
    if lowered.startswith("/system/") or lowered.startswith("/usr/libexec/") or lowered.startswith("/sbin/"):
        if any(name in lowered for name in PROTECTED_NAMES):
            return True, "这是系统关键进程，不建议关闭。"
    return False, ""


def _risk_for_process(app_family: str, role: str, command: str, cpu_percent: float, memory_bytes: int, protected: bool, protected_reason: str) -> tuple[str, str, bool]:
    if protected:
        return "高", protected_reason, False

    if role in {"updater", "daemon", "agent", "service", "crashpad"}:
        reason = "这是后台更新或常驻服务，关闭后通常只会影响自动更新、同步或后台常驻能力。"
        if memory_bytes >= HIGH_MEMORY_BYTES:
            reason += " 它当前内存占用较高，可以优先考虑关闭。"
        return "低", reason, True

    if role in {"renderer", "gpu", "helper", "utility", "plugin", "broker"}:
        reason = "这是应用的辅助/渲染子进程，关闭后通常只会让对应窗口、标签页或模块重新加载。"
        if cpu_percent >= 15:
            reason += " 它当前 CPU 占用偏高。"
        if memory_bytes >= HIGH_MEMORY_BYTES:
            reason += " 它当前内存占用也偏高。"
        return "低", reason, True

    if ".app" in command:
        reason = "这是应用主进程，关闭后通常会直接退出整个应用。"
        if memory_bytes >= HIGH_MEMORY_BYTES:
            reason += " 当前占用内存较高。"
        return "中", reason, True

    reason = "这是普通用户进程，结束后可能影响当前任务或终端会话。"
    if cpu_percent >= 15 or memory_bytes >= HIGH_MEMORY_BYTES:
        reason += " 当前资源占用较高。"
    return "中", reason, True


def _build_process_item(raw: dict) -> dict | None:
    if raw["user"] != CURRENT_USER:
        return None

    memory_bytes = raw["rss_kb"] * 1024
    if memory_bytes < MIN_MEMORY_BYTES:
        return None

    app_path = _extract_app_path(raw["command"])
    app_family = _app_family_name(app_path, raw["command"])
    role = _role_from_command(raw["command"])
    protected, protected_reason = _is_protected_process(raw["pid"], raw["command"], app_family)
    risk_level, recommendation, can_terminate = _risk_for_process(
        app_family,
        role,
        raw["command"],
        raw["cpu_percent"],
        memory_bytes,
        protected,
        protected_reason,
    )

    return {
        "id": f"process::{raw['pid']}",
        "pid": raw["pid"],
        "ppid": raw["ppid"],
        "user": raw["user"],
        "name": _display_name(app_family, role),
        "family": app_family,
        "role": role,
        "memory_bytes": memory_bytes,
        "cpu_percent": raw["cpu_percent"],
        "is_background": _is_background(role, raw["command"]),
        "risk_level": risk_level,
        "recommendation": recommendation,
        "can_terminate": can_terminate,
        "protected": protected,
        "state": raw["state"],
        "tty": raw["tty"],
        "command": raw["command"],
        "app_path": app_path,
        "reveal_path": app_path,
        "open_path": app_path,
    }


def scan_memory_processes(limit: int = DISPLAY_LIMIT) -> dict:
    processes: list[dict] = []
    total_memory_bytes = 0
    current_user_process_count = 0

    for line in _run_ps():
        parsed = _parse_ps_line(line)
        if not parsed:
            continue
        if parsed["user"] == CURRENT_USER:
            current_user_process_count += 1

        item = _build_process_item(parsed)
        if not item:
            continue
        processes.append(item)
        total_memory_bytes += item["memory_bytes"]

    processes.sort(key=lambda item: (-int(item["memory_bytes"]), -float(item["cpu_percent"]), item["name"].lower()))
    visible = processes[: max(1, limit)]

    low_risk_count = sum(1 for item in visible if item["risk_level"] == "低")
    background_count = sum(1 for item in visible if item["is_background"])
    high_memory_count = sum(1 for item in visible if item["memory_bytes"] >= HIGH_MEMORY_BYTES)

    return {
        "items": visible,
        "display_limit": limit,
        "visible_count": len(visible),
        "total_candidate_count": len(processes),
        "current_user_process_count": current_user_process_count,
        "visible_memory_bytes": sum(int(item["memory_bytes"]) for item in visible),
        "total_candidate_memory_bytes": total_memory_bytes,
        "low_risk_count": low_risk_count,
        "background_count": background_count,
        "high_memory_count": high_memory_count,
    }


def scan_reclaimable_memory_processes(limit: int = QUICK_RECLAIM_LIMIT) -> dict:
    payload = scan_memory_processes(max(DISPLAY_LIMIT * 3, 80))
    candidates = []
    for item in payload.get("items", []):
        if not item.get("can_terminate"):
            continue
        if str(item.get("risk_level") or "") != "低":
            continue
        if not bool(item.get("is_background")):
            continue
        memory_bytes = int(item.get("memory_bytes") or 0)
        cpu_percent = float(item.get("cpu_percent") or 0.0)
        if memory_bytes < QUICK_RECLAIM_MIN_MEMORY_BYTES and cpu_percent < QUICK_RECLAIM_MIN_CPU_PERCENT:
            continue
        candidates.append(item)

    candidates.sort(
        key=lambda item: (-int(item.get("memory_bytes") or 0), -float(item.get("cpu_percent") or 0.0), str(item.get("name") or "")),
    )
    visible = candidates[: max(1, limit)]
    total_memory_bytes = sum(int(item.get("memory_bytes") or 0) for item in visible)
    return {
        "items": visible,
        "candidate_count": len(candidates),
        "visible_count": len(visible),
        "estimated_reclaimable_bytes": total_memory_bytes,
    }


def _pid_exists(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def terminate_processes(
    selected_items: list[dict] | None = None,
    *,
    log_callback=None,
    cancel_check=None,
) -> dict:
    results: list[dict] = []

    for item in selected_items or []:
        raise_if_cancelled(cancel_check)
        pid = int(item.get("pid") or 0)
        name = str(item.get("name") or pid)
        can_terminate = bool(item.get("can_terminate"))
        protected = bool(item.get("protected"))
        memory_bytes = int(item.get("memory_bytes") or 0)
        if log_callback:
            log_callback(f"正在结束进程：{name}（PID {pid}）")

        if pid <= 0:
            results.append({
                "pid": pid,
                "name": name,
                "success": False,
                "message": "无效的进程 ID。",
                "reclaimed_bytes": 0,
            })
            if log_callback:
                log_callback(f"已跳过无效进程：{name}")
            continue

        if protected or not can_terminate:
            results.append({
                "pid": pid,
                "name": name,
                "success": False,
                "message": str(item.get("recommendation") or "这是受保护的进程，不能在这里结束。"),
                "reclaimed_bytes": 0,
            })
            if log_callback:
                log_callback(f"已跳过受保护进程：{name}")
            continue

        if not _pid_exists(pid):
            results.append({
                "pid": pid,
                "name": name,
                "success": False,
                "message": "进程已经不存在了。请重新扫描。",
                "reclaimed_bytes": 0,
            })
            if log_callback:
                log_callback(f"进程已不存在：{name}")
            continue

        try:
            os.kill(pid, signal.SIGTERM)
            deadline = time.time() + 1.5
            while time.time() < deadline:
                raise_if_cancelled(cancel_check)
                if not _pid_exists(pid):
                    break
                time.sleep(0.1)

            if _pid_exists(pid):
                raise TimeoutError("已经发送结束信号，但进程仍在运行。它可能拒绝退出。")

            results.append({
                "pid": pid,
                "name": name,
                "success": True,
                "message": "已结束进程。",
                "reclaimed_bytes": memory_bytes,
            })
            if log_callback:
                log_callback(f"已结束进程：{name}")
        except ProcessLookupError:
            results.append({
                "pid": pid,
                "name": name,
                "success": True,
                "message": "进程已退出。",
                "reclaimed_bytes": memory_bytes,
            })
            if log_callback:
                log_callback(f"进程已提前退出：{name}")
        except PermissionError:
            results.append({
                "pid": pid,
                "name": name,
                "success": False,
                "message": "没有权限结束这个进程。",
                "reclaimed_bytes": 0,
            })
            if log_callback:
                log_callback(f"结束失败：{name} | 没有权限")
        except TimeoutError as exc:
            results.append({
                "pid": pid,
                "name": name,
                "success": False,
                "message": str(exc),
                "reclaimed_bytes": 0,
            })
            if log_callback:
                log_callback(f"结束失败：{name} | {exc}")
        except Exception as exc:
            results.append({
                "pid": pid,
                "name": name,
                "success": False,
                "message": str(exc),
                "reclaimed_bytes": 0,
            })
            if log_callback:
                log_callback(f"结束失败：{name} | {exc}")

    return {
        "results": results,
        "terminated_count": sum(1 for item in results if item["success"]),
        "failed_count": sum(1 for item in results if not item["success"]),
        "reclaimed_bytes_estimate": sum(int(item.get("reclaimed_bytes") or 0) for item in results if item["success"]),
    }
