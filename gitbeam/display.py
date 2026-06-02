"""Rich-powered display functions for gitbeam."""

from rich.console import Console
from rich.table import Table

console = Console()


def display_user(data: dict) -> None:
    """Pretty-print a GitHub user profile."""
    table = Table(show_header=False, show_edge=False, padding=(0, 1))
    table.add_column(style="bold cyan", width=18)
    table.add_column()

    table.add_row("Bio:", data.get("bio") or "—")
    table.add_row("Company:", data.get("company") or "—")
    table.add_row("Location:", data.get("location") or "—")
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
    table = Table(title="Top Repositories", show_edge=False, padding=(0, 1))
    table.add_column("#", style="dim", width=3, justify="right")
    table.add_column("Name", style="bold cyan")
    table.add_column("Stars", justify="right")
    table.add_column("Language")
    table.add_column("Description")

    for i, repo in enumerate(repos[:5], start=1):
        table.add_row(
            str(i),
            repo.get("name", ""),
            str(repo.get("stargazers_count", 0)),
            repo.get("language") or "—",
            (repo.get("description") or "—")[:60],
        )

    console.print()
    console.print(table)
    console.print()


def display_events(events: list) -> None:
    """Display recent events as a Rich table."""
    table = Table(title="Recent Events", show_edge=False, padding=(0, 1))
    table.add_column("Type", style="bold yellow", width=18)
    table.add_column("Repo", style="cyan")
    table.add_column("Details")

    for event in events[:10]:
        etype = event.get("type", "").replace("Event", "")
        repo_name = event.get("repo", {}).get("name", "—")
        detail = _event_detail(event)
        table.add_row(etype, repo_name, detail)

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