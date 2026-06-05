"""TypedDict models for GitHub REST API responses.

These models describe only the fields that gitbeam actually uses.
They are intentionally partial: GitHub returns many more fields,
but we ignore them.  All models use total=False so missing keys
do not cause runtime errors (mypy still requires explicit None
checks for Optional fields).
"""

from __future__ import annotations

from typing import Any, TypedDict

from typing_extensions import NotRequired


class GitHubUser(TypedDict, total=False):
    """Profile returned by GET /users/{username}."""

    login: str
    name: str | None
    bio: str | None
    company: str | None
    location: str | None
    public_repos: int
    followers: int


class GitHubRepo(TypedDict, total=False):
    """Repository returned by GET /users/{username}/repos."""

    name: str
    stargazers_count: int
    language: str | None
    description: str | None


class GitHubRepoRef(TypedDict, total=False):
    """Minimal repo reference embedded in events."""

    name: str


class GitHubEventPayload(TypedDict, total=False):
    """Payload of a GitHub event (partial — only fields we render)."""

    commits: NotRequired[list[dict[str, Any]]]
    action: NotRequired[str]
    issue: NotRequired[dict[str, Any]]
    pull_request: NotRequired[dict[str, Any]]
    forkee: NotRequired[dict[str, Any]]
    ref_type: NotRequired[str]
    ref: NotRequired[str | None]


class GitHubEvent(TypedDict, total=False):
    """Event returned by GET /users/{username}/events."""

    type: str
    repo: GitHubRepoRef
    payload: GitHubEventPayload


class GitHubFollower(TypedDict, total=False):
    """Follower returned by GET /users/{username}/followers."""

    login: str


class GitHubRateLimit(TypedDict, total=False):
    """Rate-limit status from GET /rate_limit."""

    resources: NotRequired[dict[str, Any]]
