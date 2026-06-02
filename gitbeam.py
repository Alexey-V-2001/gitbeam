"""
gitbeam — CLI GitHub profile inspector.

Usage:
    python gitbeam.py <username> [--no-cache]
    python gitbeam.py auth status
"""

import logging
import os
import sys

from rich.traceback import install as install_rich_traceback

from gitbeam.commands import cmd_auth_status, cmd_events, cmd_followers, cmd_repos, cmd_user
from gitbeam.security import TokenFilter, scrub_token
from gitbeam.validation import validate_username

# ---------------------------------------------------------------------------
# Safety: prevent token leakage in logs and tracebacks
# ---------------------------------------------------------------------------

# 1. Scrub tokens from all log messages
logging.getLogger().addFilter(TokenFilter())

# 2. Rich traceback without local variables (they may contain the token)
install_rich_traceback(show_locals=False, width=100)

# 3. Last-resort safety net: scrub the traceback before printing
_original_excepthook = sys.excepthook


def _scrubbed_excepthook(exc_type, exc_value, exc_tb) -> None:
    """Wrap excepthook to scrub any token that may have leaked."""
    if exc_value is not None:
        exc_value = exc_type(scrub_token(str(exc_value)))
    _original_excepthook(exc_type, exc_value, exc_tb)


sys.excepthook = _scrubbed_excepthook

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=os.getenv("GITBEAM_LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stderr,
)


def print_usage() -> None:
    print("Usage:")
    print("  python gitbeam.py <username> [--no-cache]")
    print("  python gitbeam.py auth status")
    print()
    print("Examples:")
    print("  python gitbeam.py torvalds")
    print("  python gitbeam.py octocat --no-cache")
    print("  python gitbeam.py auth status")


def main() -> None:
    try:
        if len(sys.argv) < 2:
            print_usage()
            sys.exit(1)

        # auth status command
        if sys.argv[1] == "auth" and len(sys.argv) > 2 and sys.argv[2] == "status":
            cmd_auth_status()
            return

        username = sys.argv[1]
        validate_username(username)
        no_cache = "--no-cache" in sys.argv

        if len(sys.argv) > 2 and sys.argv[2] == "repos":
            cmd_repos(username, no_cache)
            return

        # repos command
        if len(sys.argv) > 2 and sys.argv[2] == "repos":
            cmd_repos(username, no_cache)
            return

        # events command
        if len(sys.argv) > 2 and sys.argv[2] == "events":
            cmd_events(username, no_cache)
            return

        # followers command
        if len(sys.argv) > 2 and sys.argv[2] == "followers":
            cmd_followers(username, no_cache)
            return

        # default: user lookup
        cmd_user(username, no_cache)

    except KeyboardInterrupt:
        print("", file=sys.stderr)
        sys.exit(130)
    except BrokenPipeError:
        # Silently exit when piped to head/less
        pass


if __name__ == "__main__":
    main()
