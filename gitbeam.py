"""
gitbeam — CLI GitHub profile inspector.

Usage:
    python gitbeam.py <username> [--no-cache]
    python gitbeam.py auth status
"""

import logging
import os
import sys
from typing import Optional

from rich.traceback import install as install_rich_traceback

from gitbeam.commands import cmd_auth_status, cmd_events, cmd_followers, cmd_repos, cmd_user
from gitbeam.security import TokenFilter, scrub_token
from gitbeam.validation import validate_username

# ---------------------------------------------------------------------------
# Safety: prevent token leakage in logs and tracebacks
# ---------------------------------------------------------------------------

logging.getLogger().addFilter(TokenFilter())

install_rich_traceback(show_locals=False, width=100)

_original_excepthook = sys.excepthook


def _scrubbed_excepthook(exc_type, exc_value, exc_tb) -> None:
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


def main(argv: Optional[list[str]] = None) -> int:
    """Entry point. Parse args, dispatch to command handlers, return exit code."""
    try:
        args = argv if argv is not None else sys.argv[1:]

        if len(args) < 1:
            print_usage()
            return 1

        if args[0] == "auth" and len(args) > 1 and args[1] == "status":
            cmd_auth_status()
            return 0

        username = args[0]
        validate_username(username)
        no_cache = "--no-cache" in args

        if len(args) > 1 and args[1] == "repos":
            cmd_repos(username, no_cache)
            return 0

        if len(args) > 1 and args[1] == "events":
            cmd_events(username, no_cache)
            return 0

        if len(args) > 1 and args[1] == "followers":
            cmd_followers(username, no_cache)
            return 0

        cmd_user(username, no_cache)
        return 0

    except KeyboardInterrupt:
        print("", file=sys.stderr)
        return 130
    except BrokenPipeError:
        return 0


if __name__ == "__main__":
    sys.exit(main())
