"""Tests for gitbeam.cache — JSON cache layer."""

import os
import stat
from pathlib import Path

import pytest
from freezegun import freeze_time

from gitbeam import cache


@pytest.fixture(autouse=True)
def cache_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Redirect cache to a temporary directory for every test."""
    monkeypatch.setattr(cache, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(cache, "CACHE_FILE", tmp_path / "cache.json")


class TestCache:
    """Cache read/write/expiry tests using temporary directories."""

    def test_get_cached_returns_none_when_empty(self) -> None:
        assert cache.get_cached("key") is None

    def test_set_and_get_roundtrip(self) -> None:
        data = {"login": "octocat", "name": "The Octocat"}
        cache.set_cached("user:test", data)
        result = cache.get_cached("user:test")
        assert result == data

    @freeze_time("2026-01-01 12:00:00")
    def test_get_cached_returns_none_after_expiry(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(cache, "CACHE_TTL", 1)

        cache.set_cached("key", {"data": 42})

        with freeze_time("2026-01-01 12:00:02"):
            assert cache.get_cached("key") is None

    @pytest.mark.parametrize(
        "prefix,username,data",
        [
            ("user", "octocat", {"login": "octocat"}),
            ("repos", "octocat", [{"name": "repo1"}]),
            ("events", "some-user", [{"type": "PushEvent"}]),
        ],
    )
    def test_different_cache_keys(
        self,
        prefix: str,
        username: str,
        data: dict,
    ) -> None:
        import hashlib

        digest = hashlib.sha256(username.encode()).hexdigest()[:16]
        key = f"{prefix}:{digest}"

        cache.set_cached(key, data)
        result = cache.get_cached(key)
        assert result == data

    def test_clear_cache_for_removes_only_target(self) -> None:
        cache.set_cached("keep", {"x": 1})
        cache.set_cached("drop", {"y": 2})
        cache.clear_cache_for("drop")

        assert cache.get_cached("keep") == {"x": 1}
        assert cache.get_cached("drop") is None

    def test_corrupt_cache_returns_none(self) -> None:
        import gitbeam.cache as cache_mod

        cache_dir = cache_mod.CACHE_DIR
        (cache_dir / "cache.json").write_text("not valid json {{{")

        result = cache.get_cached("anything")
        assert result is None

    @pytest.mark.skipif(os.name != "posix", reason="Permission test is Unix-only")
    def test_cache_file_permissions_0600(self) -> None:
        cache.set_cached("key", {"data": 42})

        import gitbeam.cache as cache_mod

        st = os.stat(cache_mod.CACHE_FILE)
        assert stat.S_IMODE(st.st_mode) == 0o600

    @pytest.mark.skipif(os.name != "posix", reason="Permission test is Unix-only")
    def test_cache_dir_permissions_0700(self) -> None:
        cache.set_cached("key", {"data": 42})

        import gitbeam.cache as cache_mod

        st = os.stat(cache_mod.CACHE_DIR)
        assert stat.S_IMODE(st.st_mode) == 0o700

    def test_atomic_write_does_not_leave_temp_files(self) -> None:
        cache.set_cached("key", {"data": 42})

        import gitbeam.cache as cache_mod

        items = list(cache_mod.CACHE_DIR.iterdir())
        assert len(items) == 1
        assert items[0].name == "cache.json"
