"""
Formatter Utility Module for Cryptanium Member 4.
Provides styling tokens, color mappings, date formatting, and text helpers.
"""

from datetime import datetime, timezone
from typing import Dict, Tuple

# Risk Level Colors (Hex and Human Name)
RISK_COLOR_MAP: Dict[str, Tuple[str, str]] = {
    "Excellent": ("#10B981", "Green"),   # 90-100
    "Good": ("#3B82F6", "Blue"),        # 75-89
    "Moderate": ("#F59E0B", "Amber"),     # 60-74
    "Risky": ("#F97316", "Orange"),     # 40-59
    "Critical": ("#EF4444", "Red"),       # 0-39
}

SEVERITY_COLOR_MAP: Dict[str, str] = {
    "Critical": "#DC2626",
    "High": "#EA580C",
    "Medium": "#D97706",
    "Low": "#2563EB",
    "Info": "#6B7280",
}

OWASP_TITLES: Dict[str, str] = {
    "A01": "A01:2021 - Broken Access Control",
    "A02": "A02:2021 - Cryptographic Failures",
    "A03": "A03:2021 - Injection",
    "A04": "A04:2021 - Insecure Design",
    "A05": "A05:2021 - Security Misconfiguration",
    "A06": "A06:2021 - Vulnerable and Outdated Components",
    "A07": "A07:2021 - Identification and Authentication Failures",
    "A08": "A08:2021 - Software and Data Integrity Failures",
    "A09": "A09:2021 - Security Logging and Monitoring Failures",
    "A10": "A10:2021 - Server-Side Request Forgery (SSRF)",
}


def get_current_date_formatted() -> str:
    """Returns current UTC timestamp formatted for reports."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def format_owasp_category(code: str) -> str:
    """Expands short OWASP code (e.g. A03) into full category title."""
    if not code:
        return "Unmapped / General Security"
    code_upper = code.strip().upper()
    return OWASP_TITLES.get(code_upper, f"{code_upper} - OWASP Category")


def get_risk_color_hex(risk_level: str) -> str:
    """Returns hex color code for a given risk level."""
    return RISK_COLOR_MAP.get(risk_level, ("#6B7280", "Gray"))[0]


def get_severity_color_hex(severity: str) -> str:
    """Returns hex color code for a finding severity."""
    sev = severity.capitalize() if severity else "Info"
    return SEVERITY_COLOR_MAP.get(sev, "#6B7280")


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncates string with ellipsis if it exceeds max_length."""
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."
