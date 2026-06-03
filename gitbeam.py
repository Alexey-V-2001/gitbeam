"""
gitbeam — CLI GitHub profile inspector.

Usage:
    python gitbeam.py user <username> [--no-cache]
    python gitbeam.py repos <username> [--no-cache]
    python gitbeam.py events <username> [--no-cache]
    python gitbeam.py followers <username> [--no-cache]
    python gitbeam.py auth status
"""

import argparse
import logging
import os
import sys
from typing import Optional

from rich.traceback import install as install_rich_traceback

from gitbeam.commands import cmd_auth_status, cmd_events, cmd_followers, cmd_repos, cmd_user
from gitbeam.security import TokenFilter, scrub_token
from gitbeam.validation import validate_username

from gitbeam import __version__

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


def _build_parser() -> argparse.ArgumentParser:
    """Construct the argument parser with all subcommands."""
    parser = argparse.ArgumentParser(
        prog="gitbeam",
        description="CLI GitHub profile inspector",
    )
    parser.add_argument(
        "--version", action="version", version=f"gitbeam {__version__}"
    )
    sub = parser.add_subparsers(dest="command")

    # auth status
    auth_parser = sub.add_parser("auth", help="Manage authentication")
    auth_sub = auth_parser.add_subparsers(dest="auth_command")
    auth_sub.add_parser("status", help="Check token validity")

    # user
    user_parser = sub.add_parser("user", help="Show user profile")
    user_parser.add_argument("username")
    user_parser.add_argument("--no-cache", action="store_true")

    # repos
    repos_parser = sub.add_parser("repos", help="Show top repositories")
    repos_parser.add_argument("username")
    repos_parser.add_argument("--no-cache", action="store_true")

    # events
    events_parser = sub.add_parser("events", help="Show recent events")
    events_parser.add_argument("username")
    events_parser.add_argument("--no-cache", action="store_true")

    # followers
    followers_parser = sub.add_parser("followers", help="Show followers")
    followers_parser.add_argument("username")
    followers_parser.add_argument("--no-cache", action="store_true")

    return parser


def main(argv: Optional[list[str]] = None) -> int:
    """Entry point. Parse args, dispatch to command handlers, return exit code."""
    parser = _build_parser()

    try:
        args = parser.parse_args(argv)
    except SystemExit as e:
        # argparse calls sys.exit on --help or parse errors
        return e.code if isinstance(e.code, int) else 1

    try:
        if args.command == "auth":
            if args.auth_command == "status":
                cmd_auth_status()
                return 0
            parser.print_help()
            return 1
        else:
            username = args.username
            validate_username(username)
            no_cache = args.no_cache

            if args.command == "user":
                cmd_user(username, no_cache)
            elif args.command == "repos":
                cmd_repos(username, no_cache)
            elif args.command == "events":
                cmd_events(username, no_cache)
            elif args.command == "followers":
                cmd_followers(username, no_cache)
            else:
                parser.print_help()
                return 1

        return 0

    except KeyboardInterrupt:
        print("", file=sys.stderr)
        return 130
    except BrokenPipeError:
        return 0


if __name__ == "__main__":
    sys.exit(main())
