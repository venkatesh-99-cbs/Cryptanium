"""
Cryptanium Scanner Engine — npm audit Scanner

Runs ``npm audit --json`` to find known vulnerabilities in
Node.js dependencies.
"""

from __future__ import annotations

import logging
from pathlib import Path

from backend.services.scanner.base import BaseScanner
from backend.services.scanner.models import Finding, LanguageInfo, ProjectInfo, Severity
from backend.services.scanner.utils import generate_finding_id, normalize_severity

logger = logging.getLogger("cryptanium.scanner.npm_audit")


class NpmAuditScanner(BaseScanner):
    """
    Node.js dependency vulnerability scanning via ``npm audit``.

    Requires ``package.json`` and ideally ``package-lock.json``
    in the repository root.
    """

    @property
    def name(self) -> str:
        return "npm-audit"

    def is_supported(self, project_info: ProjectInfo, language_info: LanguageInfo) -> bool:
        return project_info.has_package_json and (
            project_info.has_package_lock_json
            or project_info.has_yarn_lock
            or project_info.has_pnpm_lock
        )

    def build_command(self, repo_path: Path) -> list[str]:
        return ["npm", "audit", "--json"]

    def parse(self, raw_output: str) -> list[dict]:
        data = self._safe_parse_json(raw_output)
        if not data or not isinstance(data, dict):
            return []

        advisories: list[dict] = []

        # npm v7+ format: { "vulnerabilities": { "<pkg>": { ... } } }
        vulns = data.get("vulnerabilities", {})
        if isinstance(vulns, dict):
            for pkg_name, info in vulns.items():
                if isinstance(info, dict):
                    info["_package"] = pkg_name
                    advisories.append(info)

        # npm v6 format: { "advisories": { "<id>": { ... } } }
        if not advisories:
            legacy = data.get("advisories", {})
            if isinstance(legacy, dict):
                advisories = list(legacy.values())

        return advisories

    def normalize(self, parsed_results: list[dict], repo_path: Path) -> list[Finding]:
        findings: list[Finding] = []

        for item in parsed_results:
            try:
                pkg_name = item.get("_package", item.get("module_name", "unknown"))
                severity_raw = item.get("severity", "moderate")
                title = item.get("title", "")
                url = item.get("url", "")
                recommendation = item.get("recommendation", item.get("fixAvailable", ""))
                via = item.get("via", [])

                # Build description from 'via' entries
                description_parts: list[str] = []
                if title:
                    description_parts.append(title)
                if isinstance(via, list):
                    for entry in via:
                        if isinstance(entry, dict):
                            entry_title = entry.get("title", "")
                            if entry_title and entry_title not in description_parts:
                                description_parts.append(entry_title)
                        elif isinstance(entry, str):
                            description_parts.append(entry)

                description = "; ".join(description_parts) if description_parts else f"Vulnerability in {pkg_name}"

                # Normalize recommendation
                if isinstance(recommendation, dict):
                    recommendation = f"Fix available: update {pkg_name}"
                elif isinstance(recommendation, bool):
                    recommendation = f"Fix available: {'yes' if recommendation else 'no'}"
                elif not recommendation:
                    recommendation = f"Review {pkg_name} for vulnerability"

                finding = Finding(
                    id=generate_finding_id(),
                    tool=self.name,
                    title=f"Vulnerable dependency: {pkg_name}",
                    description=str(description),
                    severity=Severity(normalize_severity(severity_raw)),
                    file="package.json",
                    line=0,
                    column=0,
                    rule=url or "",
                    category="dependency",
                    recommendation=str(recommendation),
                    raw_output=item,
                )
                findings.append(finding)
            except Exception as exc:
                logger.debug("Skipping malformed npm audit result: %s", exc)

        return findings

    def _is_acceptable_exit_code(self, code: int) -> bool:
        # npm audit exits with 1 when vulnerabilities are found
        return code in (0, 1)
