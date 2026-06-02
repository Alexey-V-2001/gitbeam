"""
gitbeam — CLI GitHub profile inspector (v0.2.0)

Usage:
    python gitbeam.py <username> [--no-cache]
    python gitbeam.py auth status

Features:
    - GitHub token via GITHUB_TOKEN environment variable
    - JSON cache in ~/.cache/gitbeam/cache.json (TTL 5 min)
    - Rate limit awareness and full error handling
    - Rich-powered terminal output
"""

import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import requests
from rich.console import Console
from rich.table import Table

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
API_BASE = "https://api.github.com"
USER_AGENT = "gitbeam/0.2.0"
REQUEST_TIMEOUT = 10  # seconds

CACHE_DIR = Path.home() / ".cache" / "gitbeam"
CACHE_FILE = CACHE_DIR / "cache.json"
CACHE_TTL = 300  # 5 minutes

# ---------------------------------------------------------------------------
# Logger (stderr, non-Rich, to keep it simple)
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=os.getenv("GITBEAM_LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stderr,
)
logger = logging.getLogger("gitbeam")

# ---------------------------------------------------------------------------
# Rich console for user-facing output (stdout)
# ---------------------------------------------------------------------------
console = Console()


# ---------------------------------------------------------------------------
# Token management
# ---------------------------------------------------------------------------
def get_token() -> Optional[str]:
    """Read GitHub token from environment variable."""
    token = os.getenv("GITHUB_TOKEN")
    if token:
        logger.info("🔑 Token found in GITHUB_TOKEN (first 4 chars: %s...)", token[:4])
    else:
        logger.info("🔓 No token set — operating anonymously (60 req/hour).")
    return token


def validate_token(token: str) -> bool:
    """Check token validity by requesting /rate_limit."""
    url = f"{API_BASE}/rate_limit"
    headers = {
        "User-Agent": USER_AGENT,
        "Authorization": f"token {token}",
    }
    try:
        resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
    except requests.exceptions.RequestException as e:
        logger.error("❌ Network error while validating token: %s", e)
        return False

    if resp.status_code == 200:
        core = resp.json().get("resources", {}).get("core", {})
        remaining = core.get("remaining", "?")
        limit = core.get("limit", "?")
        logger.info("✅ Token valid. Rate limit: %s/%s remaining.", remaining, limit)
        return True
    elif resp.status_code == 401:
        logger.error("❌ Token invalid (401). Check GITHUB_TOKEN.")
        return False
    else:
        logger.warning("⚠️ Unexpected status while checking token: %s", resp.status_code)
        return False


# ---------------------------------------------------------------------------
# Cache layer
# ---------------------------------------------------------------------------
def _ensure_cache_dir() -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _read_cache() -> dict:
    if not CACHE_FILE.exists():
        return {}
    try:
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, IOError) as e:
        logger.warning("⚠️ Cache corrupted, ignoring: %s", e)
        return {}


def _write_cache(cache: dict) -> None:
    _ensure_cache_dir()
    CACHE_FILE.write_text(
        json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def get_cached(username: str) -> Optional[dict]:
    """Return cached user data if fresh, otherwise None."""
    entry = _read_cache().get(username)
    if not entry:
        return None

    cached_at = datetime.fromisoformat(entry["cached_at"])
    age = (datetime.now(timezone.utc) - cached_at).total_seconds()
    if age > CACHE_TTL:
        logger.info("📦 Cache for '%s' expired (%.0f s ago).", username, age)
        return None

    logger.info("📦 Using cache for '%s' (age: %.0f s).", username, age)
    return entry["data"]


def set_cached(username: str, data: dict) -> None:
    """Store user data in cache."""
    cache = _read_cache()
    cache[username] = {
        "data": data,
        "cached_at": datetime.now(timezone.utc).isoformat(),
    }
    _write_cache(cache)


def clear_cache_for(username: str) -> None:
    """Remove cached entry for a single user."""
    cache = _read_cache()
    if username in cache:
        del cache[username]
        _write_cache(cache)
        logger.info("🧹 Cache cleared for '%s'.", username)


# ---------------------------------------------------------------------------
# GitHub API
# ---------------------------------------------------------------------------
def get_user_info(username: str, token: Optional[str] = None) -> Optional[dict]:
    """Fetch user profile from GitHub API."""
    url = f"{API_BASE}/users/{username}"
    headers = {"User-Agent": USER_AGENT}
    if token:
        headers["Authorization"] = f"token {token}"

    try:
        resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
    except requests.exceptions.RequestException as e:
        logger.error("❌ Network error: %s", e)
        return None

    return _handle_response(resp, username)


def _handle_response(resp: requests.Response, username: str) -> Optional[dict]:
    """Interpret API response and return data or log error."""
    remaining = resp.headers.get("X-RateLimit-Remaining")
    if remaining is not None and int(remaining) < 10:
        logger.warning("⚠️ Only %s requests left! Limit resets in ~1 hour.", remaining)

    if resp.status_code == 200:
        return resp.json()
    elif resp.status_code == 404:
        logger.error("❌ User '%s' not found.", username)
        return None
    elif resp.status_code == 401:
        logger.error("❌ Authentication failed (401). Token missing or invalid.")
        return None
    elif resp.status_code == 403:
        logger.error("❌ Forbidden (403). Rate limit likely exceeded or access restricted.")
        return None
    elif resp.status_code == 429:
        logger.error("⏳ Too many requests (429). Please wait.")
        return None
    elif 500 <= resp.status_code < 600:
        logger.error("❌ GitHub server error (5xx). Try again later.")
        return None
    else:
        logger.error("❌ Unexpected status: %s %s", resp.status_code, resp.reason)
        return None


# ---------------------------------------------------------------------------
# Display (Rich-powered)
# ---------------------------------------------------------------------------
def display_user(data: dict) -> None:
    """Pretty-print user profile using Rich."""
    # Key-value table
    table = Table(show_header=False, show_edge=False, padding=(0, 1))
    table.add_column(style="bold cyan", width=18)
    table.add_column()

    table.add_row("📝 Bio:", data.get("bio") or "—")
    table.add_row("🏢 Company:", data.get("company") or "—")
    table.add_row("📍 Location:", data.get("location") or "—")
    table.add_row("📦 Public repos:", str(data.get("public_repos", 0)))
    table.add_row("👥 Followers:", str(data.get("followers", 0)))
    table.add_row("🔗 Profile:", f"https://github.com/{data.get('login')}")

    # Render
    console.print()
    console.rule(f"👤 {data.get('name') or data.get('login')}  —  @{data.get('login')}")
    console.print(table)
    console.rule()
    console.print()


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------
def cmd_auth_status() -> None:
    """auth status – check whether a valid token is configured."""
    token = get_token()
    if not token:
        console.print("❌ No token configured.", style="red")
        console.print("   Create one at [underline]https://github.com/settings/tokens[/]")
        console.print("   Then set: export GITHUB_TOKEN=ghp_...")
        sys.exit(1)

    if validate_token(token):
        console.print("✅ Token is valid.", style="green")
        sys.exit(0)
    else:
        console.print("❌ Token is invalid.", style="red")
        sys.exit(1)


def cmd_user(username: str, no_cache: bool = False) -> None:
    """Fetch and display a GitHub user profile."""
    token = get_token()

    if no_cache:
        clear_cache_for(username)

    cached_data = get_cached(username)
    if cached_data:
        display_user(cached_data)
        return

    logger.info("🔍 Fetching data for '%s'...", username)
    user_data = get_user_info(username, token)
    if user_data is None:
        sys.exit(1)

    set_cached(username, user_data)
    display_user(user_data)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def print_usage() -> None:
    console.print("Usage:", style="bold")
    console.print("  python gitbeam.py <username> [--no-cache]")
    console.print("  python gitbeam.py auth status")
    console.print()
    console.print("Examples:", style="bold")
    console.print("  python gitbeam.py torvalds")
    console.print("  python gitbeam.py octocat --no-cache")
    console.print("  python gitbeam.py auth status")


def main() -> None:
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    # auth status command
    if sys.argv[1] == "auth" and len(sys.argv) > 2 and sys.argv[2] == "status":
        cmd_auth_status()
        return

    # user lookup command
    username = sys.argv[1]
    no_cache = "--no-cache" in sys.argv
    cmd_user(username, no_cache)


if __name__ == "__main__":
    main()
