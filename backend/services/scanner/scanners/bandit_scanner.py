"""
Cryptanium Scanner Engine — Bandit Scanner

Runs ``bandit -r <repo> -f json`` for Python-specific security analysis.
"""

from __future__ import annotations

import logging
from pathlib import Path

from backend.services.scanner.base import BaseScanner
from backend.services.scanner.models import Finding, LanguageInfo, ProjectInfo, Severity
from backend.services.scanner.utils import generate_finding_id, make_relative_path, normalize_severity

logger = logging.getLogger("cryptanium.scanner.bandit")


class BanditScanner(BaseScanner):
    """
    Python-only static analysis via Bandit.

    Detects common security issues such as hardcoded passwords,
    SQL injection, shell injection, and use of insecure modules.
    """

    @property
    def name(self) -> str:
        return "bandit"

    def is_supported(self, project_info: ProjectInfo, language_info: LanguageInfo) -> bool:
        all_langs = {language_info.primary_language} | set(language_info.secondary_languages)
        return "python" in all_langs

    def build_command(self, repo_path: Path) -> list[str]:
        return [
            "bandit",
            "-r", str(repo_path),
            "-f", "json",
            "-q",
            "--exit-zero",
        ]

    def parse(self, raw_output: str) -> list[dict]:
        data = self._safe_parse_json(raw_output)
        if not data or not isinstance(data, dict):
            return []
        return data.get("results", [])

    def normalize(self, parsed_results: list[dict], repo_path: Path) -> list[Finding]:
        findings: list[Finding] = []
        repo_str = str(repo_path)

        for item in parsed_results:
            try:
                severity_raw = item.get("issue_severity", "MEDIUM")
                confidence = item.get("issue_confidence", "MEDIUM")

                finding = Finding(
                    id=generate_finding_id(),
                    tool=self.name,
                    title=item.get("test_name", "bandit-finding"),
                    description=item.get("issue_text", ""),
                    severity=Severity(normalize_severity(severity_raw)),
                    file=make_relative_path(item.get("filename", ""), repo_str),
                    line=item.get("line_number", 0),
                    column=0,
                    rule=item.get("test_id", ""),
                    category="security",
                    recommendation=f"Confidence: {confidence}. Review and remediate.",
                    raw_output=item,
                )
                findings.append(finding)
            except Exception as exc:
                logger.debug("Skipping malformed bandit result: %s", exc)

        return findings
