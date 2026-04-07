from __future__ import annotations

from typing import Callable


class TaskCancelledError(Exception):
    """Raised when a user-cancellable task is asked to stop."""


def raise_if_cancelled(cancel_check: Callable[[], bool] | None) -> None:
    if cancel_check and cancel_check():
        raise TaskCancelledError("用户已取消当前操作。")
