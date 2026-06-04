"""JSON cache layer for gitbeam."""

import json
import logging
import os
import tempfile
from contextlib import suppress
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast

from platformdirs import user_cache_dir

logger = logging.getLogger("gitbeam")

CACHE_DIR = Path(user_cache_dir("gitbeam"))
CACHE_FILE = CACHE_DIR / "cache.json"
CACHE_TTL = 300  # 5 minutes


def _ensure_cache_dir() -> None:
    """Create the cache directory with 0o700 permissions."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with suppress(OSError):
        os.chmod(CACHE_DIR, 0o700)


def _read_cache() -> Any:
    """Read and parse the cache file. Empty dict on any failure."""
    if not CACHE_FILE.exists():
        return {}
    try:
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        logger.warning("Cache corrupted, ignoring: %s", e)
        return {}


def _write_cache(cache: dict) -> None:
    """Atomically write the cache file with 0o600 permissions."""
    _ensure_cache_dir()
    fd, tmp_path = tempfile.mkstemp(dir=str(CACHE_DIR), suffix=".json")
    try:
        os.chmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
        os.replace(tmp_path, str(CACHE_FILE))
    except Exception:
        with suppress(OSError):
            os.unlink(tmp_path)
        raise


def get_cached(key: str) -> Any:
    """Return cached data if fresh, otherwise None."""
    entry = _read_cache().get(key)
    if not entry:
        return None

    cached_at = datetime.fromisoformat(entry["cached_at"])
    age = (datetime.now(timezone.utc) - cached_at).total_seconds()
    if age > CACHE_TTL:
        logger.info("Cache for '%s' expired (%.0f s ago).", key, age)
        return None

    logger.info("Using cache for '%s' (age: %.0f s).", key, age)
    return cast(dict, entry["data"])


def set_cached(key: str, data: Any) -> None:
    """Store data in cache under the given key."""
    cache = _read_cache()
    cache[key] = {
        "data": data,
        "cached_at": datetime.now(timezone.utc).isoformat(),
    }
    _write_cache(cache)


def clear_cache_for(key: str) -> None:
    """Remove a single cache entry."""
    cache = _read_cache()
    if key in cache:
        del cache[key]
        _write_cache(cache)
        logger.info("Cache cleared for '%s'.", key)
