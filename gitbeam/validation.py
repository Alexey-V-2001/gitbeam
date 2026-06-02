"""Username validation for gitbeam."""

import re
import sys

# GitHub username rules: 1–39 chars, alphanumeric + single hyphens,
# no leading/trailing hyphens, no consecutive hyphens.
_USERNAME_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9]|-(?=[A-Za-z0-9])){0,38}$")


def validate_username(username: str) -> None:
    """Raise SystemExit(1) if *username* does not match GitHub's pattern."""
    if not _USERNAME_RE.match(username):
        print(f"error: invalid username: {username!r}", file=sys.stderr)
        sys.exit(1)