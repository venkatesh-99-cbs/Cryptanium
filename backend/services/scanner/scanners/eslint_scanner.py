"""
Cryptanium Scanner Engine — ESLint Scanner

Runs ``npx eslint --format json`` on JavaScript / TypeScript files
to detect code quality and potential security issues.
"""

from __future__ import annotations

import logging
from pathlib import Path

from backend.services.scanner.base import BaseScanner
from backend.services.scanner.models import Finding, LanguageInfo, ProjectInfo, Severity
from backend.services.scanner.utils import generate_finding_id, make_relative_path

logger = logging.getLogger("cryptanium.scanner.eslint")

# ESLint numeric severity → string
_ESLINT_SEVERITY: dict[int, Severity] = {
    0: Severity.INFO,    # off
    1: Severity.MEDIUM,  # warn
    2: Severity.HIGH,    # error
}


class ESLintScanner(BaseScanner):
    """
    JavaScript / TypeScript linting via ESLint.

    Uses ``npx eslint`` so a local ESLint installation in the
    project is preferred over a global one.
    """

    @property
    def name(self) -> str:
        return "eslint"

    @property
    def timeout(self) -> int:
        return 300

    def is_supported(self, project_info: ProjectInfo, language_info: LanguageInfo) -> bool:
        all_langs = {language_info.primary_language} | set(language_info.secondary_languages)
        js_langs = {"javascript", "typescript"}
        return bool(all_langs & js_langs) and project_info.has_package_json

    def build_command(self, repo_path: Path) -> list[str]:
        return [
            "npx", "eslint",
            str(repo_path),
            "--format", "json",
            "--no-error-on-unmatched-pattern",
        ]

    def parse(self, raw_output: str) -> list[dict]:
        data = self._safe_parse_json(raw_output)
        if not data or not isinstance(data, list):
            return []
        return data  # ESLint returns a list of file results

    def normalize(self, parsed_results: list[dict], repo_path: Path) -> list[Finding]:
        findings: list[Finding] = []
        repo_str = str(repo_path)

        for file_result in parsed_results:
            try:
                file_path = file_result.get("filePath", "")
                messages = file_result.get("messages", [])

                for msg in messages:
                    severity_num = msg.get("severity", 1)
                    severity = _ESLINT_SEVERITY.get(severity_num, Severity.MEDIUM)

                    rule_id = msg.get("ruleId", "") or ""
                    message = msg.get("message", "")

                    finding = Finding(
                        id=generate_finding_id(),
                        tool=self.name,
                        title=rule_id or "eslint-finding",
                        description=message,
                        severity=severity,
                        file=make_relative_path(file_path, repo_str),
                        line=msg.get("line", 0),
                        column=msg.get("column", 0),
                        rule=rule_id,
                        category="code-quality",
                        recommendation=msg.get("fix", {}).get("text", "") if isinstance(msg.get("fix"), dict) else "",
                        raw_output=msg,
                    )
                    findings.append(finding)
            except Exception as exc:
                logger.debug("Skipping malformed eslint result: %s", exc)

        return findings

    def _is_acceptable_exit_code(self, code: int) -> bool:
        # ESLint exits 1 on warnings/errors found
        return code in (0, 1, 2)
