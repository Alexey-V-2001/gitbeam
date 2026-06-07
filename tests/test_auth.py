"""Tests for gitbeam.auth — GitHub token retrieval."""

import logging

import pytest

from gitbeam.auth import get_token

FAKE_TOKEN = "ghp_fake1234567890abcdef1234567890abcdef"


class TestAuth:
    """Token retrieval from GITHUB_TOKEN environment variable."""

    def test_no_token_returns_none(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """When GITHUB_TOKEN is unset, get_token returns None."""
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        assert get_token() is None

    def test_token_returned_verbatim(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """When GITHUB_TOKEN is set, get_token returns its value unchanged."""
        monkeypatch.setenv("GITHUB_TOKEN", FAKE_TOKEN)
        assert get_token() == FAKE_TOKEN

    def test_no_token_logs_info(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        """When unset, get_token logs the anonymous-mode message."""
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        caplog.set_level(logging.INFO)
        get_token()
        assert "No token set" in caplog.text

    def test_token_logs_first_four_chars(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        """When set, get_token logs the first 4 characters of the token."""
        monkeypatch.setenv("GITHUB_TOKEN", FAKE_TOKEN)
        caplog.set_level(logging.INFO)
        get_token()
        assert f"first 4 chars: {FAKE_TOKEN[:4]}" in caplog.text

    def test_token_never_fully_logged(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        """The full token value must never appear in log output."""
        monkeypatch.setenv("GITHUB_TOKEN", FAKE_TOKEN)
        caplog.set_level(logging.INFO)
        get_token()
        assert FAKE_TOKEN not in caplog.text
