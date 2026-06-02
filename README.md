# gitbeam

A CLI tool to inspect GitHub user profiles — fast, secure, terminal-first.

## Features

- 👤 Fetch and display any GitHub user profile
- 🎨 Rich terminal output with colors and layout
- 🔑 Optional token via `GITHUB_TOKEN` for higher rate limits
- 💾 Local JSON cache with 5-minute TTL
- 🛡️ Full error handling with friendly messages
- ⚡ `--no-cache` flag to force fresh data
- ✓ `auth status` command to verify your token

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
# Basic lookup (anonymous — 60 req/hour)
python gitbeam.py torvalds

# Force refresh, bypass cache
python gitbeam.py torvalds --no-cache

# Check your token
python gitbeam.py auth status
```

### With a personal access token

Create a token at [https://github.com/settings/tokens](https://github.com/settings/tokens)
(with **no scopes** — public data only).

```bash
export GITHUB_TOKEN=ghp_xxxxxxxxxxxx
python gitbeam.py octocat
```

With a valid token, the rate limit increases to **5000 requests/hour**.

## Example

```
$ python gitbeam.py octocat

02:29:03 [INFO] 🔓 No token set — operating anonymously (60 req/hour).
02:29:03 [INFO] 🔍 Fetching data for 'octocat'...

───────────────── 👤 The Octocat  —  @octocat ──────────────────
 📝 Bio:            │ —                          
 🏢 Company:        │ @github                    
 📍 Location:       │ San Francisco              
 📦 Public repos:   │ 8                          
 👥 Followers:      │ 22755                      
 🔗 Profile:        │ https://github.com/octocat 
────────────────────────────────────────────────────────────────

```

## Requirements

- Python 3.10 or newer
- See `requirements.txt` for Python dependencies

## License

MIT — see [LICENSE](LICENSE) for details.