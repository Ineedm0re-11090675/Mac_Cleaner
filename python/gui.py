from __future__ import annotations

import json
import subprocess
import threading
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from application_manager import clean_app_residuals, scan_app_residuals
from bridge import CleanerBridge
from disk_manager import scan_disk_usage
from image_manager import create_image_preview, scan_image_library
from memory_manager import scan_memory_processes, terminate_processes
from overview_manager import execute_overview_actions, scan_overview
from startup_manager import disable_startup_items, scan_startup_items

GUI_VERSION = "build-2026-04-05-1648-web"
ROOT = Path(__file__).resolve().parent
STATIC_DIR = ROOT / "webui"
HOST = "127.0.0.1"


class CleanerWebHandler(BaseHTTPRequestHandler):
    bridge = CleanerBridge()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        try:
            if parsed.path == "/" or parsed.path == "/index.html":
                self._serve_file(STATIC_DIR / "index.html", "text/html; charset=utf-8")
                return
            if parsed.path == "/app.js":
                self._serve_file(STATIC_DIR / "app.js", "application/javascript; charset=utf-8")
                return
            if parsed.path == "/style.css":
                self._serve_file(STATIC_DIR / "style.css", "text/css; charset=utf-8")
                return
            if parsed.path == "/api/image-preview":
                params = parse_qs(parsed.query)
                path = (params.get("path") or [""])[0]
                preview = create_image_preview(path)
                self._serve_file(preview, "image/png")
                return
            if parsed.path == "/api/version":
                self._send_json({"version": GUI_VERSION})
                return
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")
        except Exception as exc:
            self._send_json({"error": str(exc)}, status=HTTPStatus.INTERNAL_SERVER_ERROR)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        try:
            payload = self._read_json()
            if parsed.path == "/api/scan":
                result = self.bridge.scan(payload.get("categories") or [])
                self._send_json(result)
                return
            if parsed.path == "/api/clean-categories":
                result = self.bridge.clean(payload.get("categories") or [], dry_run=payload.get("dry_run", True))
                self._send_json(result)
                return
            if parsed.path == "/api/scan-app-caches":
                result = self.bridge.scan_app_caches(payload.get("categories") or [])
                self._send_json(result)
                return
            if parsed.path == "/api/clean-app-caches":
                result = self.bridge.clean_app_caches(payload.get("categories") or [], dry_run=payload.get("dry_run", True))
                self._send_json(result)
                return
            if parsed.path == "/api/clean-files":
                result = self.bridge.clean_files(payload.get("paths") or [], dry_run=payload.get("dry_run", True))
                self._send_json(result)
                return
            if parsed.path == "/api/scan-startup-items":
                result = scan_startup_items(payload.get("groups") or [])
                self._send_json(result)
                return
            if parsed.path == "/api/disable-startup-items":
                result = disable_startup_items(payload.get("items") or [])
                self._send_json(result)
                return
            if parsed.path == "/api/scan-app-residuals":
                result = scan_app_residuals(payload.get("roots") or [])
                self._send_json(result)
                return
            if parsed.path == "/api/clean-app-residuals":
                result = clean_app_residuals(payload.get("items") or [])
                self._send_json(result)
                return
            if parsed.path == "/api/scan-memory-processes":
                result = scan_memory_processes(int(payload.get("limit") or 20))
                self._send_json(result)
                return
            if parsed.path == "/api/scan-overview":
                result = scan_overview(self.bridge)
                self._send_json(result)
                return
            if parsed.path == "/api/execute-overview-actions":
                result = execute_overview_actions(payload.get("items") or [], self.bridge)
                self._send_json(result)
                return
            if parsed.path == "/api/scan-images":
                result = scan_image_library(payload.get("roots") or [])
                self._send_json(result)
                return
            if parsed.path == "/api/scan-disk-usage":
                result = scan_disk_usage(payload.get("roots") or [])
                self._send_json(result)
                return
            if parsed.path == "/api/terminate-processes":
                result = terminate_processes(payload.get("items") or [])
                self._send_json(result)
                return
            if parsed.path == "/api/reveal-file":
                path = Path(payload.get("path") or "")
                if not path.is_absolute():
                    raise ValueError("Path must be absolute.")
                if not path.exists():
                    raise FileNotFoundError(f"Path not found: {path}")
                subprocess.run(["open", "-R", str(path)], check=True)
                self._send_json({"ok": True, "path": str(path)})
                return
            if parsed.path == "/api/open-file":
                path = Path(payload.get("path") or "")
                if not path.is_absolute():
                    raise ValueError("Path must be absolute.")
                if not path.exists():
                    raise FileNotFoundError(f"Path not found: {path}")
                subprocess.run(["open", str(path)], check=True)
                self._send_json({"ok": True, "path": str(path)})
                return
        except Exception as exc:
            self._send_json({"error": str(exc)}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Not found")

    def log_message(self, format: str, *args) -> None:
        return

    def _serve_file(self, path: Path, content_type: str) -> None:
        if not path.exists():
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return

        content = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _read_json(self) -> dict:
        content_length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(content_length) if content_length > 0 else b"{}"
        if not raw:
            return {}
        return json.loads(raw.decode("utf-8"))

    def _send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def run_server() -> None:
    server = ThreadingHTTPServer((HOST, 0), CleanerWebHandler)
    port = server.server_address[1]
    url = f"http://{HOST}:{port}/"

    print(f"Starting GUI from: {Path(__file__).resolve()}")
    print(f"GUI version: {GUI_VERSION}")
    print(f"Open in browser: {url}")

    threading.Timer(0.6, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    run_server()
