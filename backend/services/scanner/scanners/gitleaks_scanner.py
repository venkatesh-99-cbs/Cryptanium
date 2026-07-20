"""
Cryptanium Scanner Engine — Gitleaks Scanner

Runs ``gitleaks detect`` to find hardcoded secrets, API keys,
passwords, and tokens committed to source control.
Always enabled — secret detection is language-agnostic.
"""

from __future__ import annotations

import logging
import tempfile
from pathlib import Path

from backend.services.scanner.base import BaseScanner
from backend.services.scanner.models import Finding, LanguageInfo, ProjectInfo, Severity
from backend.services.scanner.parser import OutputParser
from backend.services.scanner.utils import generate_finding_id, make_relative_path

logger = logging.getLogger("cryptanium.scanner.gitleaks")


class GitleaksScanner(BaseScanner):
    """
    Secret detection via Gitleaks.

    Runs in ``--no-git`` mode to scan the working tree rather than
    Git history, which is faster and more appropriate for shallow
    clones.
    """

    @property
    def name(self) -> str:
        return "gitleaks"

    def is_supported(self, project_info: ProjectInfo, language_info: LanguageInfo) -> bool:
        # Gitleaks is language-agnostic — always run it.
        return True

    def build_command(self, repo_path: Path) -> list[str]:
        # Write JSON to a temp file to avoid stdout pollution
        self._report_path = Path(tempfile.gettempdir()) / f"gitleaks_{id(self)}.json"
        return [
            "gitleaks", "detect",
            "--source", str(repo_path),
            "--report-format", "json",
            "--report-path", str(self._report_path),
            "--no-git",
            "--exit-code", "0",
        ]

    def parse(self, raw_output: str) -> list[dict]:
        # Gitleaks writes results to the report file, not stdout
        report_path = getattr(self, "_report_path", None)
        if report_path and report_path.exists():
            try:
                content = report_path.read_text(encoding="utf-8", errors="replace")
                data = OutputParser.safe_parse_json(content)
                return data if isinstance(data, list) else []
            except Exception as exc:
                logger.debug("Error reading gitleaks report: %s", exc)
                return []
            finally:
                try:
                    report_path.unlink(missing_ok=True)
                except Exception:
                    pass

        # Fallback: try parsing stdout
        data = self._safe_parse_json(raw_output)
        return data if isinstance(data, list) else []

    def normalize(self, parsed_results: list[dict], repo_path: Path) -> list[Finding]:
        findings: list[Finding] = []
        repo_str = str(repo_path)

        for item in parsed_results:
            try:
                rule_id = item.get("RuleID", item.get("ruleID", ""))
                description = item.get("Description", item.get("description", ""))
                file_path = item.get("File", item.get("file", ""))
                line = item.get("StartLine", item.get("startLine", 0))
                entropy = item.get("Entropy", item.get("entropy", 0))

                finding = Finding(
                    id=generate_finding_id(),
                    tool=self.name,
                    title=f"Secret Detected: {rule_id}" if rule_id else "Secret Detected",
                    description=description or f"Potential secret found (entropy: {entropy:.2f})",
                    severity=Severity.HIGH,
                    file=make_relative_path(file_path, repo_str),
                    line=line,
                    column=0,
                    rule=rule_id,
                    category="secret",
                    recommendation="Remove the secret from source code and rotate it immediately.",
                    raw_output=item,
                )
                findings.append(finding)
            except Exception as exc:
                logger.debug("Skipping malformed gitleaks result: %s", exc)

        return findings

    def _is_acceptable_exit_code(self, code: int) -> bool:
        # Gitleaks exits with 1 when leaks are found (with default config)
        # We pass --exit-code 0 so it should always be 0
        return code in (0, 1)
