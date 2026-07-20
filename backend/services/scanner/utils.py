"""
Cryptanium Scanner Engine — Utility Functions

Small, pure helpers shared across the engine.  None of these
functions perform I/O; they are safe to call from any context.
"""

from __future__ import annotations

import re
import uuid


# Pre-compiled patterns
_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
_REPO_URL_HTTPS = re.compile(
    r"^https?://[a-zA-Z0-9\-]+\.[a-zA-Z]{2,}"  # scheme + host
    r"(/[a-zA-Z0-9\-._~:/?#\[\]@!$&'()*+,;=%]*)?$"  # path
)
_REPO_URL_SSH = re.compile(
    r"^git@[a-zA-Z0-9\-]+\.[a-zA-Z]{2,}"  # git@host
    r":[a-zA-Z0-9\-._~/]+\.git$"  # :user/repo.git
)


def validate_repo_url(url: str) -> bool:
    """
    Return ``True`` if *url* looks like a valid Git repository URL.

    Accepts HTTPS URLs (``https://github.com/user/repo``) and SSH
    URLs (``git@github.com:user/repo.git``).
    """
    if not url or not isinstance(url, str):
        return False
    url = url.strip()
    return bool(_REPO_URL_HTTPS.match(url) or _REPO_URL_SSH.match(url))


def sanitize_path(path: str) -> str:
    """
    Strip surrounding whitespace and null bytes from a filesystem path.

    This is a lightweight defence; the engine relies on ``pathlib.Path``
    for proper resolution and never constructs paths from user input
    directly.
    """
    if not path:
        return ""
    return path.strip().replace("\x00", "")


def strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences (color codes) from *text*."""
    if not text:
        return ""
    return _ANSI_RE.sub("", text)


def generate_finding_id() -> str:
    """Return a short, unique identifier suitable for a ``Finding.id``."""
    return uuid.uuid4().hex[:12]


def normalize_severity(raw: str) -> str:
    """
    Map scanner-specific severity strings to the canonical set.

    Returns one of: CRITICAL, HIGH, MEDIUM, LOW, INFO, UNKNOWN.
    """
    if not raw:
        return "UNKNOWN"

    mapping: dict[str, str] = {
        # Semgrep / Bandit
        "error": "HIGH",
        "warning": "MEDIUM",
        "info": "INFO",
        "note": "INFO",
        # Bandit confidence
        "high": "HIGH",
        "medium": "MEDIUM",
        "low": "LOW",
        # npm audit
        "critical": "CRITICAL",
        "moderate": "MEDIUM",
        # ESLint
        "2": "HIGH",
        "1": "MEDIUM",
        "0": "INFO",
    }
    return mapping.get(raw.strip().lower(), raw.upper() if raw.upper() in {
        "CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"
    } else "UNKNOWN")


def make_relative_path(file_path: str, workspace: str) -> str:
    """
    Convert an absolute *file_path* to a workspace-relative path.

    If *file_path* does not start with *workspace*, return it unchanged.
    """
    if not file_path or not workspace:
        return file_path or ""
    # Normalise separators
    fp = file_path.replace("\\", "/")
    ws = workspace.rstrip("/").replace("\\", "/")
    if fp.startswith(ws):
        return fp[len(ws):].lstrip("/")
    return fp
