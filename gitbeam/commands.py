"""Command handlers for gitbeam CLI."""

import logging
import sys

from gitbeam import auth, cache, display
from gitbeam.api import GitHubClient

logger = logging.getLogger("gitbeam")


def cmd_auth_status() -> None:
    """Handle 'auth status' — validate the GitHub token."""
    token = auth.get_token()
    if not token:
        display.print_error("No token configured.")
        display.print_error("Create one at https://github.com/settings/tokens")
        display.print_error("Then set: export GITHUB_TOKEN=ghp_...")
        sys.exit(1)

    client = GitHubClient(token=token)
    if client.validate_token():
        display.print_success("Token is valid.")
        sys.exit(0)
    else:
        display.print_error("Token is invalid.")
        sys.exit(1)


def cmd_user(username: str, no_cache: bool = False) -> None:
    """Fetch and display a GitHub user profile."""
    token = auth.get_token()
    client = GitHubClient(token=token)

    if no_cache:
        cache.clear_cache_for(f"user:{username}")

    cached = cache.get_cached(f"user:{username}")
    if cached:
        display.display_user(cached)
        return

    logger.info("Fetching data for '%s'...", username)
    data = client.get_user_info(username)
    if data is None:
        sys.exit(1)

    cache.set_cached(f"user:{username}", data)
    display.display_user(data)


def cmd_repos(username: str, no_cache: bool = False) -> None:
    """Fetch and display top repositories."""
    token = auth.get_token()
    client = GitHubClient(token=token)

    if no_cache:
        cache.clear_cache_for(f"repos:{username}")

    cached = cache.get_cached(f"repos:{username}")
    if cached:
        display.display_repos(cached)
        return

    logger.info("Fetching repos for '%s'...", username)
    data = client.get_repos(username)
    if data is None:
        sys.exit(1)

    cache.set_cached(f"repos:{username}", data)
    display.display_repos(data)


def cmd_events(username: str, no_cache: bool = False) -> None:
    """Fetch and display recent public events."""
    token = auth.get_token()
    client = GitHubClient(token=token)

    if no_cache:
        cache.clear_cache_for(f"events:{username}")

    cached = cache.get_cached(f"events:{username}")
    if cached:
        display.display_events(cached)
        return

    logger.info("Fetching events for '%s'...", username)
    data = client.get_events(username)
    if data is None:
        sys.exit(1)

    cache.set_cached(f"events:{username}", data)
    display.display_events(data)


def cmd_followers(username: str, no_cache: bool = False) -> None:
    """Fetch and display followers."""
    token = auth.get_token()
    client = GitHubClient(token=token)

    if no_cache:
        cache.clear_cache_for(f"followers:{username}")

    cached = cache.get_cached(f"followers:{username}")
    if cached:
        display.display_followers(cached)
        return

    logger.info("Fetching followers for '%s'...", username)
    data = client.get_followers(username)
    if data is None:
        sys.exit(1)

    cache.set_cached(f"followers:{username}", data)
    display.display_followers(data)
