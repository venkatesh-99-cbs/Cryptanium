"""
Cryptanium Scanner Engine — Semgrep Scanner

Runs ``semgrep scan --json`` against the repository.
Supports Python, JavaScript, and TypeScript (always compatible).
"""

from __future__ import annotations

import logging
from pathlib import Path

from backend.services.scanner.base import BaseScanner
from backend.services.scanner.models import Finding, LanguageInfo, ProjectInfo, Severity
from backend.services.scanner.utils import generate_finding_id, make_relative_path, normalize_severity

logger = logging.getLogger("cryptanium.scanner.semgrep")

_SUPPORTED_LANGUAGES = {"python", "javascript", "typescript"}


class SemgrepScanner(BaseScanner):
    """
    Static analysis via Semgrep.

    Semgrep supports dozens of languages so it is compatible with
    almost every repository.  We always enable it when the primary
    or secondary language is Python, JavaScript, or TypeScript.
    """

    @property
    def name(self) -> str:
        return "semgrep"

    @property
    def timeout(self) -> int:
        return 600  # large repos can be slow

    def is_supported(self, project_info: ProjectInfo, language_info: LanguageInfo) -> bool:
        all_langs = {language_info.primary_language} | set(language_info.secondary_languages)
        return bool(all_langs & _SUPPORTED_LANGUAGES)

    def build_command(self, repo_path: Path) -> list[str]:
        return [
            "semgrep", "scan",
            "--json",
            "--quiet",
            "--no-git-ignore",
            str(repo_path),
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
                check_id = item.get("check_id", "")
                extra = item.get("extra", {})
                severity_raw = extra.get("severity", "WARNING")
                message = extra.get("message", "")
                metadata = extra.get("metadata", {})

                finding = Finding(
                    id=generate_finding_id(),
                    tool=self.name,
                    title=check_id.split(".")[-1] if check_id else "semgrep-finding",
                    description=message,
                    severity=Severity(normalize_severity(severity_raw)),
                    file=make_relative_path(item.get("path", ""), repo_str),
                    line=item.get("start", {}).get("line", 0),
                    column=item.get("start", {}).get("col", 0),
                    rule=check_id,
                    category=metadata.get("category", "security"),
                    recommendation=metadata.get("fix", extra.get("fix", "")),
                    raw_output=item,
                )
                findings.append(finding)
            except Exception as exc:
                logger.debug("Skipping malformed semgrep result: %s", exc)

        return findings
