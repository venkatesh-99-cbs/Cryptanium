"""
Cryptanium Scanner Engine — pip-audit Scanner

Runs ``pip-audit`` against ``requirements.txt`` to find known
vulnerabilities in Python dependencies.
"""

from __future__ import annotations

import logging
from pathlib import Path

from backend.services.scanner.base import BaseScanner
from backend.services.scanner.models import Finding, LanguageInfo, ProjectInfo, Severity
from backend.services.scanner.utils import generate_finding_id, normalize_severity

logger = logging.getLogger("cryptanium.scanner.pip_audit")


class PipAuditScanner(BaseScanner):
    """
    Python dependency vulnerability scanning via pip-audit.

    Requires ``requirements.txt`` in the repository root.
    """

    @property
    def name(self) -> str:
        return "pip-audit"

    def is_supported(self, project_info: ProjectInfo, language_info: LanguageInfo) -> bool:
        return project_info.has_requirements_txt

    def build_command(self, repo_path: Path) -> list[str]:
        requirements_path = repo_path / "requirements.txt"
        return [
            "pip-audit",
            "-r", str(requirements_path),
            "--format", "json",
            "--progress-spinner", "off",
        ]

    def parse(self, raw_output: str) -> list[dict]:
        data = self._safe_parse_json(raw_output)
        if not data:
            return []

        # pip-audit JSON: {"dependencies": [...]}
        if isinstance(data, dict):
            deps = data.get("dependencies", [])
            # Filter to only vulnerable packages
            return [
                dep for dep in deps
                if dep.get("vulns") and len(dep.get("vulns", [])) > 0
            ]

        if isinstance(data, list):
            return data

        return []

    def normalize(self, parsed_results: list[dict], repo_path: Path) -> list[Finding]:
        findings: list[Finding] = []

        for dep in parsed_results:
            try:
                pkg_name = dep.get("name", "unknown")
                pkg_version = dep.get("version", "unknown")
                vulns = dep.get("vulns", [])

                for vuln in vulns:
                    vuln_id = vuln.get("id", "")
                    description = vuln.get("description", "")
                    fix_versions = vuln.get("fix_versions", [])
                    fix_str = ", ".join(fix_versions) if fix_versions else "No fix available"

                    # Determine severity from aliases or default to HIGH
                    severity = Severity.HIGH
                    aliases = vuln.get("aliases", [])
                    if any("CRITICAL" in str(a).upper() for a in aliases):
                        severity = Severity.CRITICAL

                    finding = Finding(
                        id=generate_finding_id(),
                        tool=self.name,
                        title=f"Vulnerable dependency: {pkg_name} {pkg_version}",
                        description=description or f"{vuln_id}: {pkg_name}=={pkg_version} is vulnerable",
                        severity=severity,
                        file="requirements.txt",
                        line=0,
                        column=0,
                        rule=vuln_id,
                        category="dependency",
                        recommendation=f"Upgrade {pkg_name} to {fix_str}",
                        raw_output=dep,
                    )
                    findings.append(finding)
            except Exception as exc:
                logger.debug("Skipping malformed pip-audit result: %s", exc)

        return findings
