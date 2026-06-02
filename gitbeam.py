"""
gitbeam — CLI GitHub profile inspector
Usage: python gitbeam.py <username>
"""

import sys
import requests
from rich.console import Console
from rich.table import Table

API_BASE = "https://api.github.com"
USER_AGENT = "gitbeam/0.1.0"
TIMEOUT = 10


def get_user(username):
    url = f"{API_BASE}/users/{username}"
    headers = {"User-Agent": USER_AGENT}
    try:
        resp = requests.get(url, headers=headers, timeout=TIMEOUT)
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}", file=sys.stderr)
        return None

    if resp.status_code == 200:
        return resp.json()
    elif resp.status_code == 404:
        print(f"❌ User '{username}' not found.", file=sys.stderr)
        return None
    elif resp.status_code == 403:
        print("❌ Access forbidden. Rate limit may be exceeded (60 req/hour without token).", file=sys.stderr)
        return None
    else:
        print(f"❌ API error: {resp.status_code} {resp.reason}", file=sys.stderr)
        return None


def display(data):
    console = Console()

    table = Table(show_header=False, show_edge=False, padding=(0, 1))
    table.add_column(style="bold", width=20)
    table.add_column()

    table.add_row("📝 Bio:", data.get('bio') or '—')
    table.add_row("🏢 Company:", data.get('company') or '—')
    table.add_row("📍 Location:", data.get('location') or '—')
    table.add_row("📦 Public repos:", str(data.get('public_repos', 0)))
    table.add_row("👥 Followers:", str(data.get('followers', 0)))

    console.print()
    console.print("=" * 40)
    console.print(f"  👤 {data.get('name') or data.get('login')}")
    console.print(f"  @{data.get('login')}")
    console.print("=" * 40)
    console.print(table)
    console.print("=" * 40)
    console.print()


def main():
    if len(sys.argv) < 2:
        print("Usage: python gitbeam.py <username>", file=sys.stderr)
        sys.exit(1)

    username = sys.argv[1]
    print(f"🔍 Fetching data for '{username}'...", file=sys.stderr)
    data = get_user(username)
    if data:
        display(data)


if __name__ == "__main__":
    main()