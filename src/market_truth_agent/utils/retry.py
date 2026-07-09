from __future__ import annotations

import os
import time
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")

_DEFAULT_RETRIES = 5
_DEFAULT_BASE_DELAY = 2.0
_DEFAULT_MAX_DELAY = 120.0


def retry_config() -> tuple[int, float, float]:
    retries = int(os.environ.get("MTA_RETRY_MAX", str(_DEFAULT_RETRIES)))
    base = float(os.environ.get("MTA_RETRY_BASE_DELAY", str(_DEFAULT_BASE_DELAY)))
    max_delay = float(os.environ.get("MTA_RETRY_MAX_DELAY", str(_DEFAULT_MAX_DELAY)))
    return max(1, retries), base, max_delay


def is_transient_error(exc: BaseException) -> bool:
    name = type(exc).__name__.lower()
    msg = str(exc).lower()
    transient_names = (
        "connectionerror",
        "timeouterror",
        "apiconnectionerror",
        "ratelimiterror",
        "internalservererror",
        "serviceunavailable",
    )
    if any(n in name for n in transient_names):
        return True
    transient_msgs = (
        "connection refused",
        "connection error",
        "timeout",
        "temporarily unavailable",
        "rate limit",
        "502",
        "503",
        "504",
    )
    return any(m in msg for m in transient_msgs)


def retry_call(
    fn: Callable[[], T],
    *,
    label: str = "operation",
    on_retry: Callable[[int, BaseException, float], None] | None = None,
) -> T:
    """Retry *fn* on transient network/API failures with exponential backoff."""
    max_retries, base_delay, max_delay = retry_config()
    last_exc: BaseException | None = None
    for attempt in range(1, max_retries + 1):
        try:
            return fn()
        except BaseException as exc:
            last_exc = exc
            if attempt >= max_retries or not is_transient_error(exc):
                raise
            delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
            if on_retry:
                on_retry(attempt, exc, delay)
            time.sleep(delay)
    assert last_exc is not None
    raise last_exc
