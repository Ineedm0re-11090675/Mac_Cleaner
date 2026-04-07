from __future__ import annotations

import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any


APP_NAME = "macOS Cleaner"
RUNTIME_DIR = Path.home() / "Library" / "Application Support" / APP_NAME / "runtime"
COMMANDS_DIR = RUNTIME_DIR / "commands"
HELPER_LOCK_PATH = RUNTIME_DIR / "tray-helper.lock"
HELPER_LOG_PATH = Path("/tmp/macos_cleaner_tray_helper.log")


def ensure_runtime_dirs() -> None:
    COMMANDS_DIR.mkdir(parents=True, exist_ok=True)


def append_helper_log(message: str) -> None:
    try:
        ensure_runtime_dirs()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with HELPER_LOG_PATH.open("a", encoding="utf-8") as handle:
            handle.write(f"[{timestamp}] {message}\n")
    except OSError:
        pass


def write_command(action: str, payload: dict[str, Any] | None = None) -> Path:
    ensure_runtime_dirs()
    command = {
        "id": uuid.uuid4().hex,
        "action": action,
        "payload": payload or {},
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "pid": os.getpid(),
    }
    temp_path = COMMANDS_DIR / f"{command['created_at'].replace(':', '-')}-{command['id']}.tmp"
    final_path = temp_path.with_suffix(".json")
    temp_path.write_text(json.dumps(command, ensure_ascii=False), encoding="utf-8")
    temp_path.replace(final_path)
    return final_path


def drain_commands() -> list[dict[str, Any]]:
    ensure_runtime_dirs()
    commands: list[dict[str, Any]] = []
    for path in sorted(COMMANDS_DIR.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                commands.append(data)
        except Exception as exc:  # pragma: no cover - diagnostic only
            append_helper_log(f"failed to parse command {path}: {exc}")
        finally:
            try:
                path.unlink()
            except OSError:
                pass
    return commands
