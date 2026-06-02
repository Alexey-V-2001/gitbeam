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


def print_error(message: str) -> None:
    """Print an error message to stderr via Rich (styled red)."""
    console.print(message, style="red")


def print_success(message: str) -> None:
    """Print a success message via Rich (styled green)."""
    console.print(message, style="green")
