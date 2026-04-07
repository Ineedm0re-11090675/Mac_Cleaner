from __future__ import annotations

import re
import shutil
import subprocess
import time
from pathlib import Path

from memory_manager import (
    CURRENT_USER,
    _app_family_name,
    _base_process_name,
    _display_name,
    _extract_app_path,
    _is_background,
    _parse_ps_line,
    _role_from_command,
    _run_ps,
)


HOME = Path.home()
MIN_TOP_PROCESS_MEMORY_BYTES = 5 * 1024 * 1024
MIN_TOP_PROCESS_CPU_PERCENT = 0.3


def _run_text(command: list[str]) -> str:
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    return completed.stdout


def _parse_size_to_bytes(raw: str) -> int:
    token = str(raw or "").strip().replace(",", "")
    match = re.match(r"(?i)^([0-9]+(?:\.[0-9]+)?)\s*([kmgtp]?)(?:i?b?)?$", token)
    if not match:
        return 0
    value = float(match.group(1))
    unit = match.group(2).upper()
    factors = {
        "": 1,
        "K": 1024,
        "M": 1024**2,
        "G": 1024**3,
        "T": 1024**4,
        "P": 1024**5,
    }
    return int(value * factors.get(unit, 1))


def _read_top_summary() -> dict:
    output = _run_text(["top", "-l", "1", "-n", "0"])
    cpu_percent = 0.0

    cpu_match = re.search(r"CPU usage:\s*([0-9.]+)% user,\s*([0-9.]+)% sys,\s*([0-9.]+)% idle", output)
    if cpu_match:
        cpu_percent = float(cpu_match.group(1)) + float(cpu_match.group(2))

    return {
        "cpu_percent": max(0.0, min(100.0, cpu_percent)),
    }


def _read_vm_memory_summary() -> dict:
    output = _run_text(["vm_stat"])
    page_size = 4096
    size_match = re.search(r"page size of (\d+) bytes", output)
    if size_match:
        page_size = int(size_match.group(1))

    values: dict[str, int] = {}
    for line in output.splitlines():
        if ":" not in line:
            continue
        key, raw_value = line.split(":", 1)
        key = key.strip().strip('"')
        values[key] = int(re.sub(r"[^0-9]", "", raw_value) or 0)

    total_bytes = int(_run_text(["sysctl", "-n", "hw.memsize"]).strip() or 0)
    anonymous_bytes = int(values.get("Anonymous pages", 0)) * page_size
    wired_bytes = int(values.get("Pages wired down", 0)) * page_size
    compressed_bytes = int(values.get("Pages occupied by compressor", 0)) * page_size
    available_bytes = (
        int(values.get("Pages free", 0))
        + int(values.get("Pages speculative", 0))
        + int(values.get("Pages purgeable", 0))
    ) * page_size
    used_bytes = anonymous_bytes + wired_bytes + compressed_bytes
    memory_percent = (used_bytes / total_bytes * 100.0) if total_bytes else 0.0

    return {
        "memory_used_bytes": used_bytes,
        "memory_total_bytes": total_bytes,
        "memory_percent": max(0.0, min(100.0, memory_percent)),
        "app_memory_bytes": anonymous_bytes,
        "wired_memory_bytes": wired_bytes,
        "compressed_memory_bytes": compressed_bytes,
        "available_memory_bytes": available_bytes,
    }


def _read_network_counters() -> dict:
    output = _run_text(["netstat", "-ibn"])
    ibytes = 0
    obytes = 0
    interfaces: list[str] = []

    for line in output.splitlines()[1:]:
        parts = line.split()
        if len(parts) < 10:
            continue
        name = parts[0].rstrip("*")
        network = parts[2]
        if not network.startswith("<Link#"):
            continue
        if name.startswith("lo"):
            continue
        try:
            recv_bytes = int(parts[6])
            sent_bytes = int(parts[9])
        except ValueError:
            continue
        ibytes += recv_bytes
        obytes += sent_bytes
        if name not in interfaces:
            interfaces.append(name)

    return {
        "ibytes": ibytes,
        "obytes": obytes,
        "interfaces": interfaces,
    }


def _read_directory_usage_bytes(path: Path) -> int:
    if not path.exists():
        return 0
    completed = subprocess.run(
        ["du", "-sk", str(path)],
        check=False,
        capture_output=True,
        text=True,
    )
    line = completed.stdout.strip().splitlines()
    if not line:
        return 0
    parts = line[0].split()
    if not parts:
        return 0
    return int(parts[0]) * 1024


def _read_disk_breakdown() -> list[dict]:
    ordered_roots = [
        {"key": "library", "name": "系统目录", "path": HOME / "Library"},
        {"key": "documents", "name": "文稿", "path": HOME / "Documents"},
        {"key": "desktop", "name": "桌面", "path": HOME / "Desktop"},
        {"key": "downloads", "name": "下载", "path": HOME / "Downloads"},
    ]
    breakdown: list[dict] = []
    for root in ordered_roots:
        try:
            size_bytes = _read_directory_usage_bytes(Path(root["path"]))
        except Exception:
            size_bytes = 0
        breakdown.append(
            {
                "key": root["key"],
                "name": root["name"],
                "path": str(root["path"]),
                "size_bytes": size_bytes,
            }
        )
    return breakdown


def _build_top_processes(limit: int) -> dict:
    processes: list[dict] = []
    for line in _run_ps():
        parsed = _parse_ps_line(line)
        if not parsed or parsed["user"] != CURRENT_USER:
            continue

        memory_bytes = int(parsed["rss_kb"]) * 1024
        cpu_percent = float(parsed["cpu_percent"])
        if memory_bytes < MIN_TOP_PROCESS_MEMORY_BYTES and cpu_percent < MIN_TOP_PROCESS_CPU_PERCENT:
            continue

        command = parsed["command"]
        app_path = _extract_app_path(command)
        app_family = _app_family_name(app_path, command)
        role = _role_from_command(command)
        processes.append(
            {
                "pid": int(parsed["pid"]),
                "name": _display_name(app_family, role) if app_family else _base_process_name(command),
                "family": app_family or _base_process_name(command),
                "memory_bytes": memory_bytes,
                "cpu_percent": cpu_percent,
                "is_background": _is_background(role, command),
                "role": role,
            }
        )

    top_memory = sorted(
        processes,
        key=lambda item: (-int(item["memory_bytes"]), -float(item["cpu_percent"]), item["name"].lower()),
    )[:limit]
    top_cpu = sorted(
        processes,
        key=lambda item: (-float(item["cpu_percent"]), -int(item["memory_bytes"]), item["name"].lower()),
    )[:limit]

    return {
        "top_memory": top_memory,
        "top_cpu": top_cpu,
    }


def sample_dashboard(
    previous_sample: dict | None = None,
    *,
    process_limit: int = 5,
    include_processes: bool = True,
    include_disk: bool = True,
) -> dict:
    sampled_at = time.time()
    top_summary = _read_top_summary()
    memory_summary = _read_vm_memory_summary()
    network_counters = _read_network_counters()

    previous_sample = previous_sample or {}
    disk_used_bytes = int(previous_sample.get("disk_used_bytes", 0) or 0)
    disk_total_bytes = int(previous_sample.get("disk_total_bytes", 0) or 0)
    disk_percent = float(previous_sample.get("disk_percent", 0.0) or 0.0)
    if include_disk:
        disk_usage = shutil.disk_usage(str(HOME))
        disk_used_bytes = disk_usage.used
        disk_total_bytes = disk_usage.total
        disk_percent = (disk_usage.used / disk_usage.total * 100.0) if disk_usage.total else 0.0
        disk_breakdown = _read_disk_breakdown()
    else:
        disk_breakdown = list(previous_sample.get("disk_breakdown") or [])

    download_bps = 0.0
    upload_bps = 0.0
    if previous_sample:
        previous_time = float(previous_sample.get("sampled_at") or 0.0)
        elapsed = max(0.001, sampled_at - previous_time)
        previous_network = previous_sample.get("network_counters") or {}
        download_bps = max(
            0.0,
            (float(network_counters["ibytes"]) - float(previous_network.get("ibytes") or 0.0)) / elapsed,
        )
        upload_bps = max(
            0.0,
            (float(network_counters["obytes"]) - float(previous_network.get("obytes") or 0.0)) / elapsed,
        )

    top_memory_processes = list(previous_sample.get("top_memory_processes") or [])
    top_cpu_processes = list(previous_sample.get("top_cpu_processes") or [])
    if include_processes:
        processes = _build_top_processes(process_limit)
        top_memory_processes = processes["top_memory"]
        top_cpu_processes = processes["top_cpu"]

    return {
        "processes_refreshed": include_processes,
        "disk_refreshed": include_disk,
        "sampled_at": sampled_at,
        "cpu_percent": top_summary["cpu_percent"],
        "memory_percent": memory_summary["memory_percent"],
        "memory_used_bytes": memory_summary["memory_used_bytes"],
        "memory_total_bytes": memory_summary["memory_total_bytes"],
        "app_memory_bytes": memory_summary["app_memory_bytes"],
        "wired_memory_bytes": memory_summary["wired_memory_bytes"],
        "compressed_memory_bytes": memory_summary["compressed_memory_bytes"],
        "available_memory_bytes": memory_summary["available_memory_bytes"],
        "disk_percent": disk_percent,
        "disk_used_bytes": disk_used_bytes,
        "disk_total_bytes": disk_total_bytes,
        "disk_breakdown": disk_breakdown,
        "download_bps": download_bps,
        "upload_bps": upload_bps,
        "interfaces": network_counters["interfaces"],
        "network_counters": network_counters,
        "top_memory_processes": top_memory_processes,
        "top_cpu_processes": top_cpu_processes,
    }
