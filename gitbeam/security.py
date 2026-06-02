"""Token safety utilities for gitbeam."""

import logging
import re

# Matches GitHub personal access token prefixes:
#   ghp_ (classic), github_pat_ (fine-grained), ghs_ (server-to-server)
_TOKEN_RE = re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}")


def scrub_token(text: str) -> str:
    """Replace any GitHub token found in *text* with '<REDACTED>'."""
    return _TOKEN_RE.sub("<REDACTED>", text)


class TokenFilter(logging.Filter):
    """Logging filter that scrubs tokens from all log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = scrub_token(str(record.msg))
        if record.args:
            record.args = tuple(scrub_token(str(a)) for a in record.args)
        return True
