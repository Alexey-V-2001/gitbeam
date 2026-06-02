"""
gitbeam — CLI GitHub profile inspector.

Usage:
    python gitbeam.py <username> [--no-cache]
    python gitbeam.py auth status
"""

import logging
import os
import sys

from gitbeam.commands import cmd_auth_status, cmd_user, cmd_repos, cmd_events

# Set up logging early (before any other module touches it).
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
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    # auth status command
    if sys.argv[1] == "auth" and len(sys.argv) > 2 and sys.argv[2] == "status":
        cmd_auth_status()
        return
    
    # repos command
    if len(sys.argv) > 2 and sys.argv[2] == "repos":
        username = sys.argv[1]
        no_cache = "--no-cache" in sys.argv
        cmd_repos(username, no_cache)
        return

    # events command
    if len(sys.argv) > 2 and sys.argv[2] == "events":
        username = sys.argv[1]
        no_cache = "--no-cache" in sys.argv
        cmd_events(username, no_cache)
        return

    # default: user lookup
    username = sys.argv[1]
    no_cache = "--no-cache" in sys.argv
    cmd_user(username, no_cache)


if __name__ == "__main__":
    main()
