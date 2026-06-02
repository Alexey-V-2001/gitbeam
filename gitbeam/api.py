"""GitHub API requests for gitbeam."""

import logging
from typing import Optional

import requests

API_BASE = "https://api.github.com"
USER_AGENT = "gitbeam/0.2.0"
REQUEST_TIMEOUT = 10

logger = logging.getLogger("gitbeam")


def get_user_info(username: str, token: Optional[str] = None) -> Optional[dict]:
    """Fetch user profile from GitHub API."""
    url = f"{API_BASE}/users/{username}"
    headers = _build_headers(token)
    try:
        resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
    except requests.exceptions.RequestException as e:
        logger.error("Network error: %s", e)
        return None
    return _handle_response(resp, context=f"user '{username}'")


def validate_token(token: str) -> bool:
    """Check token validity by calling /rate_limit."""
    url = f"{API_BASE}/rate_limit"
    headers = _build_headers(token)
    try:
        resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
    except requests.exceptions.RequestException as e:
        logger.error("Network error while validating token: %s", e)
        return False

    if resp.status_code == 200:
        core = resp.json().get("resources", {}).get("core", {})
        remaining = core.get("remaining", "?")
        limit = core.get("limit", "?")
        logger.info("Token valid. Rate limit: %s/%s remaining.", remaining, limit)
        return True
    elif resp.status_code == 401:
        logger.error("Token invalid (401).")
        return False
    else:
        logger.warning("Unexpected status while checking token: %s", resp.status_code)
        return False


def get_repos(username: str, token: Optional[str] = None) -> Optional[list]:
    """Fetch repositories for a user, sorted by stars descending."""
    url = f"{API_BASE}/users/{username}/repos?sort=stars&direction=desc&per_page=100"
    headers = _build_headers(token)
    try:
        resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
    except requests.exceptions.RequestException as e:
        logger.error("Network error: %s", e)
        return None
    return _handle_response(resp, context=f"repos for '{username}'")


def get_events(username: str, token: Optional[str] = None) -> Optional[list]:
    """Fetch recent public events for a user."""
    url = f"{API_BASE}/users/{username}/events?per_page=10"
    headers = _build_headers(token)
    try:
        resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
    except requests.exceptions.RequestException as e:
        logger.error("Network error: %s", e)
        return None
    return _handle_response(resp, context=f"events for '{username}'")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _build_headers(token: Optional[str]) -> dict:
    headers = {"User-Agent": USER_AGENT}
    if token:
        headers["Authorization"] = f"token {token}"
    return headers


def _handle_response(resp: requests.Response, context: str = "") -> Optional[dict]:
    """Interpret API response, log errors, return data or None."""
    remaining = resp.headers.get("X-RateLimit-Remaining")
    if remaining is not None and int(remaining) < 10:
        logger.warning("Only %s requests left! Limit resets in ~1 hour.", remaining)

    if resp.status_code == 200:
        return resp.json()
    elif resp.status_code == 404:
        logger.error("%s not found.", context.capitalize() or "Resource")
        return None
    elif resp.status_code == 401:
        logger.error("Authentication failed (401). Token missing or invalid.")
        return None
    elif resp.status_code == 403:
        logger.error("Forbidden (403). Rate limit likely exceeded or access restricted.")
        return None
    elif resp.status_code == 429:
        logger.error("Too many requests (429). Please wait.")
        return None
    elif 500 <= resp.status_code < 600:
        logger.error("GitHub server error (5xx). Try again later.")
        return None
    else:
        logger.error("Unexpected status: %s %s", resp.status_code, resp.reason)
        return None
    