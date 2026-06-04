"""Rich-powered display functions for gitbeam."""

import re

from rich.console import Console
from rich.markup import escape as rich_escape
from rich.table import Table

console = Console()

# Control characters to strip (except \t, \n which are harmless in Rich tables)
_CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def _sanitize(text: str, max_len: int = 200) -> str:
    """Strip control chars, escape Rich markup, truncate to *max_len*."""
    if not text:
        return ""
    text = _CONTROL_RE.sub("", str(text))
    text = rich_escape(text)
    if len(text) > max_len:
        text = text[:max_len] + "..."
    return text


def display_user(data: dict) -> None:
    """Pretty-print a GitHub user profile."""
    table = Table(show_header=False, show_edge=False, padding=(0, 1))
    table.add_column(style="bold cyan", width=18)
    table.add_column()

    table.add_row("Bio:", _sanitize(data.get("bio") or "—", max_len=300))
    table.add_row("Company:", _sanitize(data.get("company") or "—"))
    table.add_row("Location:", _sanitize(data.get("location") or "—"))
    table.add_row("Public repos:", str(data.get("public_repos", 0)))
    table.add_row("Followers:", str(data.get("followers", 0)))
    table.add_row("Profile:", f"https://github.com/{data.get('login')}")

    console.print()
    console.rule(f"{data.get('name') or data.get('login')}  —  @{data.get('login')}")
    console.print(table)
    console.rule()
    console.print()


def display_repos(repos: list) -> None:
    """Display top repositories as a Rich table."""
    table = Table(title="Top Repositories", padding=(0, 1))
    table.add_column("#", style="dim", width=3, justify="right")
    table.add_column("Name", style="bold cyan")
    table.add_column("Stars", justify="right")
    table.add_column("Language")
    table.add_column("Description")

    for i, repo in enumerate(repos[:5], start=1):
        table.add_row(
            str(i),
            _sanitize(repo.get("name", ""), max_len=80),
            str(repo.get("stargazers_count", 0)),
            _sanitize(repo.get("language") or "—", max_len=30),
            _sanitize(repo.get("description") or "—", max_len=60),
        )

    console.print()
    console.print(table)
    console.print()


def display_events(events: list) -> None:
    """Display recent events as a Rich table."""
    if not events:
        console.print("No events found.", style="dim")
        return

    table = Table(title="Recent Events", padding=(0, 1))
    table.add_column("Type", style="bold yellow", width=18)
    table.add_column("Repo", style="cyan")
    table.add_column("Details")

    for event in events[:10]:
        etype = event.get("type", "").replace("Event", "")
        repo_name = _sanitize(event.get("repo", {}).get("name", "—"), max_len=60)
        detail = _sanitize(_event_detail(event), max_len=200)
        table.add_row(etype, repo_name, detail)

    console.print()
    console.print(table)
    console.print()


def display_followers(followers: list) -> None:
    """Display followers as a Rich table with borders."""
    if not followers:
        console.print("No followers found.", style="dim")
        return

    table = Table(
        title=f"Followers (showing {len(followers)})",
        show_edge=True,
        padding=(0, 1),
    )
    table.add_column("#", style="dim", width=4, justify="right")
    table.add_column("Login", style="bold cyan")
    table.add_column("Profile", style="dim")

    for i, follower in enumerate(followers, start=1):
        login = _sanitize(follower.get("login", ""), max_len=39)
        table.add_row(
            str(i),
            login,
            f"https://github.com/{login}",
        )

    console.print()
    console.print(table)
    console.print()


def print_error(message: str) -> None:
    """Print an error message to stderr via Rich (styled red)."""
    console.print(message, style="red")


def print_success(message: str) -> None:
    """Print a success message via Rich (styled green)."""
    console.print(message, style="green")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _event_detail(event: dict) -> str:
    """Extract a human-readable detail from an event payload."""
    payload = event.get("payload", {})
    etype = event.get("type", "")

    if etype == "PushEvent":
        commits = payload.get("commits", [])
        return f"{len(commits)} commit(s)"
    elif etype == "IssuesEvent":
        action = payload.get("action", "")
        title = payload.get("issue", {}).get("title", "")
        return f"{action}: {title[:50]}"
    elif etype == "PullRequestEvent":
        action = payload.get("action", "")
        title = payload.get("pull_request", {}).get("title", "")
        return f"{action}: {title[:50]}"
    elif etype == "ForkEvent":
        forkee = payload.get("forkee", {}).get("full_name", "")
        return f"forked to {forkee}"
    elif etype == "WatchEvent":
        return "starred"
    elif etype == "CreateEvent":
        ref_type = payload.get("ref_type", "")
        ref = payload.get("ref", "")
        return f"{ref_type}: {ref}" if ref else ref_type
    else:
        return "—"
