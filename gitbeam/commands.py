"""Command handlers for gitbeam CLI."""

import logging
import sys
from typing import Optional

from gitbeam import api, auth, cache, display

logger = logging.getLogger("gitbeam")


def cmd_auth_status() -> None:
    """Handle 'auth status' command."""
    token = auth.get_token()
    if not token:
        display.print_error("No token configured.")
        display.print_error("Create one at https://github.com/settings/tokens")
        display.print_error("Then set: export GITHUB_TOKEN=ghp_...")
        sys.exit(1)

    if api.validate_token(token):
        display.print_success("Token is valid.")
        sys.exit(0)
    else:
        display.print_error("Token is invalid.")
        sys.exit(1)


def cmd_user(username: str, no_cache: bool = False) -> None:
    """Handle the default command: fetch and display a user profile."""
    token = auth.get_token()

    if no_cache:
        cache.clear_cache_for(f"user:{username}")

    cached_data = cache.get_cached(f"user:{username}")
    if cached_data:
        display.display_user(cached_data)
        return

    logger.info("Fetching data for '%s'...", username)
    user_data = api.get_user_info(username, token)
    if user_data is None:
        sys.exit(1)

    cache.set_cached(f"user:{username}", user_data)
    display.display_user(user_data)


def cmd_repos(username: str, no_cache: bool = False) -> None:
    """Handle 'repos' subcommand."""
    token = auth.get_token()

    if no_cache:
        cache.clear_cache_for(f"repos:{username}")

    cached_data = cache.get_cached(f"repos:{username}")
    if cached_data:
        display.display_repos(cached_data)
        return

    logger.info("Fetching repos for '%s'...", username)
    repos = api.get_repos(username, token)
    if repos is None:
        sys.exit(1)

    cache.set_cached(f"repos:{username}", repos)
    display.display_repos(repos)
