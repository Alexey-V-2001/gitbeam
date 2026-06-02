"""GitHub REST API client with retry, timeout, and rate-limit handling."""

import logging
from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

logger = logging.getLogger("gitbeam")

API_BASE = "https://api.github.com"
USER_AGENT = "gitbeam/0.3.1"
REQUEST_TIMEOUT = (3.05, 15)  # (connect, read)


class GitHubClient:
    """GitHub REST API client with retry, timeout, and Bearer auth.

    Every request:
        - timeout=(3.05, 15) so the CLI never hangs
        - 3 retries with backoff on 429/5xx (GET only)
        - Authorization: Bearer <token> (if token provided)
        - allow_redirects=False
        - Accept + X-GitHub-Api-Version headers pinned
    """

    def __init__(
        self,
        token: Optional[str] = None,
        base_url: str = API_BASE,
        session: Optional[requests.Session] = None,
    ) -> None:
        self._token = token
        self._base_url = base_url.rstrip("/")
        self._session = session or self._build_session()

    # -- public methods --------------------------------------------------

    def get_user_info(self, username: str) -> Optional[dict]:
        """GET /users/{username}"""
        return self._request("GET", f"/users/{username}")

    def get_repos(self, username: str) -> Optional[list]:
        """GET /users/{username}/repos?sort=stars&direction=desc&per_page=100"""
        path = f"/users/{username}/repos?sort=stars&direction=desc&per_page=100"
        return self._request("GET", path)

    def get_events(self, username: str) -> Optional[list]:
        """GET /users/{username}/events?per_page=10"""
        return self._request("GET", f"/users/{username}/events?per_page=10")

    def get_followers(self, username: str) -> Optional[list]:
        """GET /users/{username}/followers?per_page=100"""
        return self._request("GET", f"/users/{username}/followers?per_page=100")

    def validate_token(self) -> bool:
        """Validate the stored token via GET /rate_limit."""
        data = self._request("GET", "/rate_limit")
        if data is None:
            return False
        core = data.get("resources", {}).get("core", {})
        logger.info(
            "Token valid. Rate limit: %s/%s remaining.",
            core.get("remaining", "?"),
            core.get("limit", "?"),
        )
        return True

    # -- internal ---------------------------------------------------------

    def _build_session(self) -> requests.Session:
        """Session with retry adapter for https and http."""
        retry = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods={"GET"},
            respect_retry_after_header=True,
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session = requests.Session()
        session.mount("https://", adapter)
        session.mount("http://", adapter)  # for local testing
        return session

    def _build_headers(self) -> dict:
        """User-Agent, Accept, API version, optional Bearer token."""
        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        return headers

    def _request(self, method: str, path: str) -> Optional[dict]:
        """Execute request, return JSON or None."""
        url = f"{self._base_url}{path}"
        try:
            resp = self._session.request(
                method,
                url,
                headers=self._build_headers(),
                timeout=REQUEST_TIMEOUT,
                allow_redirects=False,
            )
        except requests.exceptions.RequestException as e:
            logger.error("Network error: %s", e)
            return None
        return self._handle_response(resp)

    def _handle_response(self, resp: requests.Response) -> Optional[dict]:
        """Map status code -> log message; return JSON or None."""
        self._log_rate_limit(resp)

        if resp.status_code == 200:
            return resp.json()
        if resp.status_code == 404:
            logger.error("Resource not found (404).")
        elif resp.status_code == 401:
            logger.error("Authentication failed (401). Token missing or invalid.")
        elif resp.status_code == 403:
            self._handle_403(resp)
        elif resp.status_code == 429:
            logger.error("Too many requests (429). Please wait.")
        elif 500 <= resp.status_code < 600:
            logger.error("GitHub server error (%s). Try again later.", resp.status_code)
        else:
            logger.error("Unexpected status: %s %s", resp.status_code, resp.reason)
        return None

    def _handle_403(self, resp: requests.Response) -> None:
        """Secondary rate limit (403 + 'secondary rate limit' in body)
        vs standard 403."""
        try:
            body = resp.json()
            if "secondary rate limit" in str(body.get("message", "")).lower():
                logger.error("Secondary rate limit hit (403). Wait a few minutes.")
                return
        except (ValueError, KeyError):
            pass
        logger.error("Forbidden (403). Rate limit exceeded or access restricted.")

    @staticmethod
    def _log_rate_limit(resp: requests.Response) -> None:
        """Log remaining rate limit; warn below 10."""
        remaining = resp.headers.get("X-RateLimit-Remaining")
        if remaining is None:
            return
        limit = resp.headers.get("X-RateLimit-Limit")
        remaining_int = int(remaining)
        if limit is not None:
            logger.info("Rate limit: %s/%s remaining.", remaining_int, limit)
        if remaining_int < 10:
            logger.warning("Only %s requests left!", remaining_int)
