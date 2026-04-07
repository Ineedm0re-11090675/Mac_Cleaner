from __future__ import annotations

import queue
import threading
import time
import traceback
from typing import Any, Callable

from PySide6.QtCore import QTimer

from task_support import TaskCancelledError


class TaskContext:
    def __init__(self, event_queue: "queue.Queue[tuple[str, Any]]") -> None:
        self._event_queue = event_queue
        self._cancel_event = threading.Event()
        self._cancel_handlers: list[Callable[[], None]] = []

    def log(self, message: str) -> None:
        timestamp = time.strftime("%H:%M:%S")
        self._event_queue.put(("log", f"[{timestamp}] {message}"))

    def update_progress(self, value: int, message: str, *, log: bool = False) -> None:
        if log:
            self.log(message)
        self._event_queue.put(("progress", (max(0, min(100, int(value))), message)))

    def stage(self, value: int, message: str) -> None:
        self.update_progress(value, message, log=True)

    def add_cancel_handler(self, handler: Callable[[], None]) -> None:
        self._cancel_handlers.append(handler)

    def cancel(self) -> None:
        if self._cancel_event.is_set():
            return
        self._cancel_event.set()
        self.log("已收到取消请求，正在尝试停止当前任务。")
        for handler in list(self._cancel_handlers):
            try:
                handler()
            except Exception as exc:  # pragma: no cover - defensive cleanup path
                self.log(f"取消处理器执行失败：{exc}")

    def is_cancelled(self) -> bool:
        return self._cancel_event.is_set()

    def raise_if_cancelled(self) -> None:
        if self._cancel_event.is_set():
            raise TaskCancelledError("用户已取消当前操作。")


class BackgroundTaskRunner:
    def __init__(
        self,
        *,
        owner,
        dialog,
        task_fn: Callable[[TaskContext], Any],
        on_success: Callable[[Any, str], None],
        on_error: Callable[[str, str], None],
        on_cancel: Callable[[str], None],
        on_finished: Callable[[], None] | None = None,
    ) -> None:
        self.owner = owner
        self.dialog = dialog
        self.task_fn = task_fn
        self.on_success = on_success
        self.on_error = on_error
        self.on_cancel = on_cancel
        self.on_finished = on_finished
        self.event_queue: "queue.Queue[tuple[str, Any]]" = queue.Queue()
        self.context = TaskContext(self.event_queue)
        self.thread = threading.Thread(target=self._worker_main, daemon=True)
        self.timer = QTimer(owner)
        self.timer.setInterval(50)
        self.timer.timeout.connect(self._poll_events)
        self._done = False

    def start(self) -> None:
        self.thread.start()
        self.timer.start()

    def request_cancel(self) -> None:
        self.dialog.mark_cancel_requested()
        self.context.cancel()

    def _worker_main(self) -> None:
        try:
            result = self.task_fn(self.context)
            if self.context.is_cancelled():
                self.event_queue.put(("cancelled", "用户已取消当前操作。"))
            else:
                self.event_queue.put(("result", result))
        except TaskCancelledError as exc:
            self.event_queue.put(("cancelled", str(exc)))
        except Exception as exc:  # pragma: no cover - runtime thread path
            self.event_queue.put(("error", (str(exc), traceback.format_exc())))

    def _finish(self) -> None:
        if self._done:
            return
        self._done = True
        self.timer.stop()
        self.dialog.close()
        if self.on_finished:
            self.on_finished()

    def _poll_events(self) -> None:
        while True:
            try:
                event_type, payload = self.event_queue.get_nowait()
            except queue.Empty:
                break
            if event_type == "log":
                self.dialog.append_log(str(payload))
                continue
            if event_type == "progress":
                value, message = payload
                self.dialog.update_progress(int(value), str(message))
                continue
            if event_type == "result":
                logs = self.dialog.logs_text()
                self._finish()
                self.on_success(payload, logs)
                return
            if event_type == "cancelled":
                logs = self.dialog.logs_text()
                self._finish()
                self.on_cancel(logs or str(payload))
                return
            if event_type == "error":
                message, details = payload
                logs = self.dialog.logs_text()
                self._finish()
                self.on_error(message, f"{logs}\n\n{details}".strip())
                return
