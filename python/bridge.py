from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Iterable


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

    def _run(self, *args: str) -> dict:
        if not self.binary.exists():
            raise FileNotFoundError(
                f"C++ binary not found: {self.binary}. Please build the project first."
            )

        completed = subprocess.run(
            [str(self.binary), *args],
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(completed.stdout)

    def scan(self, categories: Iterable[str] | None = None) -> dict:
        categories = list(categories or [])
        return self._run("scan", *categories)

    def scan_app_caches(self, categories: Iterable[str] | None = None) -> dict:
        categories = list(categories or [])
        return self._run("scan-app-caches", *categories)

    def clean(self, categories: Iterable[str], dry_run: bool = True) -> dict:
        args = ["clean", *list(categories)]
        if dry_run:
            args.append("--dry-run")
        else:
            args.append("--execute")
        return self._run(*args)

    def clean_app_caches(self, categories: Iterable[str], dry_run: bool = True) -> dict:
        args = ["clean-app-caches", *list(categories)]
        if dry_run:
            args.append("--dry-run")
        else:
            args.append("--execute")
        return self._run(*args)

    def clean_files(self, file_paths: Iterable[str], dry_run: bool = True) -> dict:
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
            return self._run(*args)
        finally:
            try:
                os.unlink(manifest_path)
            except OSError:
                pass
