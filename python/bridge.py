from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Iterable

from task_support import TaskCancelledError


def _candidate_roots() -> list[Path]:
    if getattr(sys, "frozen", False):
        roots = []
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            roots.append(Path(meipass))
        executable_dir = Path(sys.executable).resolve().parent
        roots.append(executable_dir)
        roots.append(executable_dir.parent / "Resources")
        return roots
    return [Path(__file__).resolve().parent.parent]


def _default_binary_path() -> Path:
    candidates: list[Path] = []
    for root in _candidate_roots():
        candidates.append(root / "build" / "mac_cleaner")
        candidates.append(root / "mac_cleaner")
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


BINARY = _default_binary_path()


class CleanerBridge:
    def __init__(self, binary: Path | None = None) -> None:
        self.binary = binary or BINARY

    def _run(self, *args: str, task_context=None) -> dict:
        if not self.binary.exists():
            raise FileNotFoundError(
                f"C++ binary not found: {self.binary}. Please build the project first."
            )

        command = [str(self.binary), *args]
        if task_context is None:
            completed = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
            )
            return json.loads(completed.stdout)

        proc = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        task_context.log(f"已启动 C++ 核心：{' '.join(args)}")
        task_context.add_cancel_handler(lambda: _terminate_process(proc))

        while proc.poll() is None:
            if task_context.is_cancelled():
                _terminate_process(proc)
                raise TaskCancelledError("已取消当前扫描任务。")
            time.sleep(0.1)

        stdout, stderr = proc.communicate()
        if task_context.is_cancelled():
            raise TaskCancelledError("已取消当前扫描任务。")
        if proc.returncode != 0:
            raise RuntimeError((stderr or stdout or "C++ 核心执行失败。").strip())
        task_context.log("C++ 核心执行结束。")
        return json.loads(stdout)

    def scan(self, categories: Iterable[str] | None = None, *, task_context=None) -> dict:
        categories = list(categories or [])
        return self._run("scan", *categories, task_context=task_context)

    def scan_app_caches(self, categories: Iterable[str] | None = None, *, task_context=None) -> dict:
        categories = list(categories or [])
        return self._run("scan-app-caches", *categories, task_context=task_context)

    def clean(self, categories: Iterable[str], dry_run: bool = True, *, task_context=None) -> dict:
        args = ["clean", *list(categories)]
        if dry_run:
            args.append("--dry-run")
        else:
            args.append("--execute")
        return self._run(*args, task_context=task_context)

    def clean_app_caches(self, categories: Iterable[str], dry_run: bool = True, *, task_context=None) -> dict:
        args = ["clean-app-caches", *list(categories)]
        if dry_run:
            args.append("--dry-run")
        else:
            args.append("--execute")
        return self._run(*args, task_context=task_context)

    def clean_files(self, file_paths: Iterable[str], dry_run: bool = True, *, task_context=None) -> dict:
        paths = [path for path in file_paths if path]
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as handle:
            handle.write("\n".join(paths))
            manifest_path = handle.name

        try:
            args = ["clean-files", manifest_path]
            if dry_run:
                args.append("--dry-run")
            else:
                args.append("--execute")
            if task_context:
                task_context.log(f"已写入待处理清单：{len(paths)} 个路径。")
            return self._run(*args, task_context=task_context)
        finally:
            try:
                os.unlink(manifest_path)
            except OSError:
                pass


def _terminate_process(proc: subprocess.Popen[str]) -> None:
    if proc.poll() is not None:
        return
    try:
        proc.terminate()
        proc.wait(timeout=1)
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass
