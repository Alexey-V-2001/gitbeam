# gitbeam

A simple CLI tool to fetch and display GitHub user profile information
directly in your terminal.

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
python gitbeam.py <username>
```

### Example

```bash
$ python gitbeam.py octocat
🔍 Fetching data for 'octocat'...

========================================
  👤 The Octocat
  @octocat
========================================
 📝 Bio:              │ —             
 🏢 Company:          │ @github       
 📍 Location:         │ San Francisco 
 📦 Public repos:     │ 8             
 👥 Followers:        │ 22755         
========================================
```

## Requirements

- Python 3.10 or newer
- `requests` (installed automatically via `requirements.txt`)

## License

MIT — see [LICENSE](LICENSE) for details.