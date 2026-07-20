"""
Cryptanium Scanner Engine — Result Normalizer

Merges, de-duplicates, and sorts findings from all scanners into
a single unified list.
"""

from __future__ import annotations

import logging
from typing import Sequence

from backend.services.scanner.models import Finding, ScanResult, Severity

logger = logging.getLogger("cryptanium.normalizer")

# Sort order: most severe first
_SEVERITY_ORDER: dict[Severity, int] = {
    Severity.CRITICAL: 0,
    Severity.HIGH: 1,
    Severity.MEDIUM: 2,
    Severity.LOW: 3,
    Severity.INFO: 4,
    Severity.UNKNOWN: 5,
}


class ResultNormalizer:
    """
    Merge and de-duplicate findings across all scanners.

    Two findings are considered duplicates when they share the same
    file, line, and rule.  In case of a collision the higher-severity
    finding wins.
    """

    def normalize(self, scan_results: Sequence[ScanResult]) -> list[Finding]:
        """
        Collect all findings, de-duplicate, and sort by severity.
        """
        all_findings: list[Finding] = []

        for result in scan_results:
            if result.success:
                all_findings.extend(result.findings)

        logger.info(
            "Normalizing %d raw findings from %d scanners",
            len(all_findings),
            len(scan_results),
        )

        unique = self._deduplicate(all_findings)
        sorted_findings = self._sort_by_severity(unique)

        logger.info(
            "Normalization complete: %d unique findings", len(sorted_findings)
        )
        return sorted_findings

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _deduplicate(findings: list[Finding]) -> list[Finding]:
        """
        Remove duplicates where (file, line, rule) collide.

        When duplicates are found, the finding with the higher severity
        is kept.
        """
        seen: dict[tuple[str, int, str], Finding] = {}

        for f in findings:
            key = (f.file, f.line, f.rule)
            if key in seen:
                existing = seen[key]
                if _SEVERITY_ORDER.get(f.severity, 5) < _SEVERITY_ORDER.get(existing.severity, 5):
                    seen[key] = f
            else:
                seen[key] = f

        return list(seen.values())

    @staticmethod
    def _sort_by_severity(findings: list[Finding]) -> list[Finding]:
        """Sort CRITICAL → INFO."""
        return sorted(
            findings,
            key=lambda f: _SEVERITY_ORDER.get(f.severity, 5),
        )
