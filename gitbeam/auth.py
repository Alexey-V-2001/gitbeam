"""Token management for gitbeam."""

import logging
import os

logger = logging.getLogger("gitbeam")


def get_token() -> str | None:
    """Read GitHub token from environment variable."""
    token = os.getenv("GITHUB_TOKEN")
    if token:
        logger.info("Token found in GITHUB_TOKEN (first 4 chars: %s...)", token[:4])
    else:
        logger.info("No token set — operating anonymously (60 req/hour).")
    return token
