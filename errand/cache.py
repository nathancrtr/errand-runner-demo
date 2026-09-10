"""Every download lands in data/cache and is reused for three days, so a run
with a warm cache needs no network at all."""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

import requests

CACHE = Path("data/cache")
MAX_AGE_HOURS = 72
UA = "errand (personal council watcher; contact via github.com/nthncrtr)"


def fetch(url: str, *, method: str = "GET", body: dict | None = None,
          headers: dict | None = None, timeout: int = 60) -> tuple[bytes, str]:
    """Bytes and content type for a URL, from the cache when it is fresh."""
    key = hashlib.sha1(f"{method} {url} {json.dumps(body, sort_keys=True)}".encode()).hexdigest()
    path, meta = CACHE / key, CACHE / f"{key}.meta"
    if path.exists() and time.time() - path.stat().st_mtime < MAX_AGE_HOURS * 3600:
        return path.read_bytes(), meta.read_text() if meta.exists() else ""
    resp = requests.request(method, url, json=body, headers={"User-Agent": UA, **(headers or {})},
                            timeout=timeout)
    resp.raise_for_status()
    CACHE.mkdir(parents=True, exist_ok=True)
    path.write_bytes(resp.content)
    meta.write_text(resp.headers.get("content-type", ""))
    return resp.content, meta.read_text()
