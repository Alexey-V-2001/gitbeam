# gitbeam

A CLI tool to inspect GitHub user profiles — fast, secure, terminal-first.

## Features

- User profile with bio, company, location, stats
- Top repositories sorted by stars
- Recent public events (pushes, PRs, issues, forks)
- Followers list
- Token authentication via `GITHUB_TOKEN` for higher rate limits
- JSON cache with 5-minute TTL
- Full error handling and rate limit awareness
- Rate limit status logged on every request

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
python gitbeam.py <username>              # user profile
python gitbeam.py <username> repos        # top 5 repositories
python gitbeam.py <username> events       # 10 most recent events
python gitbeam.py <username> followers    # followers list
python gitbeam.py auth status             # check token
python gitbeam.py <username> --no-cache   # bypass cache
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

## Requirements

- Python 3.10+
- Dependencies: `requests`, `rich`

## License

MIT — see [LICENSE](LICENSE) for details.