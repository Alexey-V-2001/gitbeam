"""Tests for gitbeam.validation — username validation."""

import pytest

from gitbeam.validation import validate_username

# Valid usernames per GitHub rules:
#   - 1 to 39 characters
#   - Alphanumeric and single hyphens (no leading/trailing, no consecutive)
VALID = [
    "a",
    "1",
    "torvalds",
    "octocat",
    "hello-world",
    "user-123-test",
    "a" * 39,  # max length
]

# Invalid usernames
INVALID = [
    "",  # empty
    "-abc",  # leading hyphen
    "abc-",  # trailing hyphen
    "ab--cd",  # consecutive hyphens
    "user name",  # space
    "user@host",  # special char
    "user.name",  # dot
    "user/name",  # path traversal
    "a" * 40,  # too long (40 chars)
    "user\nname",  # newline
    "user\tname",  # tab
]


class TestValidateUsername:
    """Group username validation tests."""

    @pytest.mark.parametrize("username", VALID)
    def test_valid_username(self, username: str) -> None:
        """Valid usernames should not raise SystemExit."""
        validate_username(username)

    @pytest.mark.parametrize("username", INVALID)
    def test_invalid_username_exits(self, username: str) -> None:
        """Invalid usernames should call sys.exit(1)."""
        with pytest.raises(SystemExit) as exc_info:
            validate_username(username)
        assert exc_info.value.code == 1

    @pytest.mark.parametrize("username", INVALID)
    def test_invalid_username_prints_error(
        self, username: str, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Invalid usernames should print an error message to stderr."""
        with pytest.raises(SystemExit):
            validate_username(username)
        captured = capsys.readouterr()
        assert "invalid username" in captured.err.lower()
