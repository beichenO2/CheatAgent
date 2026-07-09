from __future__ import annotations

import os
import sys
import time

_started_at = time.time()


def progress(msg: str) -> None:
    """Stream progress to stderr (flush immediately). Disable via MTA_PROGRESS=0."""
    if os.environ.get("MTA_PROGRESS", "1") == "0":
        return
    elapsed = time.time() - _started_at
    print(f"[{elapsed:7.1f}s] {msg}", file=sys.stderr, flush=True)
