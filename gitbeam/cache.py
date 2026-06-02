"""JSON cache layer for gitbeam."""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger("gitbeam")

CACHE_DIR = Path.home() / ".cache" / "gitbeam"
CACHE_FILE = CACHE_DIR / "cache.json"
CACHE_TTL = 300  # 5 minutes


def _ensure_cache_dir() -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _read_cache() -> dict:
    if not CACHE_FILE.exists():
        return {}
    try:
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, IOError) as e:
        logger.warning("Cache corrupted, ignoring: %s", e)
        return {}


def _write_cache(cache: dict) -> None:
    _ensure_cache_dir()
    CACHE_FILE.write_text(
        json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def get_cached(key: str) -> Optional[dict]:
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
    return entry["data"]


def set_cached(key: str, data: dict) -> None:
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
