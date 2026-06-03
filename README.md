# gitbeam

A CLI tool to inspect GitHub user profiles — fast, secure, terminal-first.

## Features

- User profile with bio, company, location, stats
- Top repositories sorted by stars
- Recent public events (pushes, PRs, issues, forks)
- Followers list
- Token authentication via `GITHUB_TOKEN` for higher rate limits
- JSON cache with 5‑minute TTL (cross‑platform cache directory)
- Retry with backoff on rate limits and server errors
- Full error handling and rate limit awareness
- Paranoid about your token: never in logs, tracebacks, or cache

## Installation

```bash
git clone https://github.com/Alexey-V-2001/gitbeam.git
cd gitbeam
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

## Usage

```bash
python gitbeam.py user <username>              # user profile
python gitbeam.py repos <username>             # top 5 repositories
python gitbeam.py events <username>            # 10 most recent events
python gitbeam.py followers <username>         # followers list
python gitbeam.py auth status                  # check token
python gitbeam.py user <username> --no-cache   # bypass cache
```

### Authentication

Create a token at [https://github.com/settings/tokens](https://github.com/settings/tokens)
(no scopes needed for public data).

```bash
export GITHUB_TOKEN=ghp_xxxxxxxxxxxx
```

## Examples

### Profile

```
────────────────── The Octocat  —  @octocat ──────────────────
 Bio:               │ —                          
 Company:           │ @github                    
 Location:          │ San Francisco              
 Public repos:      │ 8                          
 Followers:         │ 22755                      
 Profile:           │ https://github.com/octocat 
──────────────────────────────────────────────────────────────
```

### Repositories

```
                                    Top Repositories                                    
┏━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃   # ┃ Name               ┃ Stars ┃ Language ┃ Description                            ┃
┡━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│   1 │ boysenberry-repo-1 │   446 │ —        │ Testing                                │
│   2 │ linguist           │   720 │ Ruby     │ Language Savant. If your repository's  │
│     │                    │       │          │ language is being repo                 │
│   3 │ test-repo1         │   454 │ —        │ —                                      │
│   4 │ hello-worId        │   745 │ —        │ My first repository on GitHub.         │
│   5 │ git-consortium     │   574 │ —        │ This repo is for demonstration         │
│     │                    │       │          │ purposes only.                         │
└─────┴────────────────────┴───────┴──────────┴────────────────────────────────────────┘
```

### Followers

```
                     Followers (showing 100)                     
┏━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃    # ┃ Login            ┃ Profile                             ┃
┡━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│    1 │ alice            │ https://github.com/alice            │
│    2 │ bob              │ https://github.com/bob              │
│  ... │ ...              │ https://github.com/...              │
└──────┴──────────────────┴─────────────────────────────────────┘
```

## Security

- Token is **only** read from `GITHUB_TOKEN` — never in CLI args, never in code, never in URLs.
- Token scrubbed from all log records, tracebacks, and exception messages (three layers of defense).
- Every HTTP request has a fixed timeout — the CLI never hangs on a stalled connection.
- Automatic retry with exponential backoff on 429/5xx (GET only, idempotent).
- Usernames validated against GitHub's pattern — no SSRF through path manipulation.
- API URL hostname verified before every request — blocked if it points elsewhere.
- Cache directory `0o700`, files `0o600`, atomic writes via tempfile + rename.
- All GitHub-supplied text (bio, descriptions, event titles) escaped before terminal rendering — no Rich markup injection.
- `Ctrl+C` → clean exit 130. `BrokenPipeError` → silent exit.

## Cache

Responses are cached for 5 minutes in your system cache directory
(`~/.cache/gitbeam/` on Linux, `~/Library/Caches/gitbeam/` on macOS,
`%LOCALAPPDATA%\gitbeam\` on Windows). Use `--no-cache` to force a fresh request.

## Requirements

- Python 3.10+
- Dependencies: `requests>=2.32`, `rich>=13`, `platformdirs>=4`

## License

MIT — see [LICENSE](LICENSE) for details.