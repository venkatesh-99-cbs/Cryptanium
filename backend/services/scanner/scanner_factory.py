"""
Cryptanium Scanner Engine — Scanner Factory

Selects the compatible set of scanners for a given repository
based on detected project info and languages.

Uses the **Strategy + Factory** pattern: each scanner self-reports
its compatibility via ``is_supported()``, and the factory simply
filters the full registry.
"""

from __future__ import annotations

import logging

from backend.services.scanner.base import BaseScanner
from backend.services.scanner.command_runner import CommandRunner
from backend.services.scanner.models import LanguageInfo, ProjectInfo
from backend.services.scanner.scanners.bandit_scanner import BanditScanner
from backend.services.scanner.scanners.eslint_scanner import ESLintScanner
from backend.services.scanner.scanners.gitleaks_scanner import GitleaksScanner
from backend.services.scanner.scanners.npm_audit_scanner import NpmAuditScanner
from backend.services.scanner.scanners.pip_audit_scanner import PipAuditScanner
from backend.services.scanner.scanners.semgrep_scanner import SemgrepScanner

logger = logging.getLogger("cryptanium.scanner_factory")


class ScannerFactory:
    """
    Build the list of scanners that should run for a repository.

    Every registered scanner's ``is_supported()`` method is consulted;
    only those that return ``True`` are included in the result.

    The factory ensures that:

    * **Python projects** → Semgrep, Bandit, pip-audit, Gitleaks
    * **Node projects**   → Semgrep, npm audit, ESLint, Gitleaks
    * **Mixed repos**     → union of all compatible scanners
    * **All repos**       → Gitleaks (secret detection is universal)
    """

    def __init__(self, command_runner: CommandRunner | None = None) -> None:
        self._runner = command_runner or CommandRunner()

    def get_scanners(
        self,
        project_info: ProjectInfo,
        language_info: LanguageInfo,
    ) -> list[BaseScanner]:
        """
        Return a list of scanner instances compatible with the project.
        """
        registry = self._build_registry()
        compatible: list[BaseScanner] = []

        for scanner in registry:
            try:
                if scanner.is_supported(project_info, language_info):
                    compatible.append(scanner)
                    logger.info("Scanner selected: %s", scanner.name)
                else:
                    logger.debug("Scanner skipped (not supported): %s", scanner.name)
            except Exception as exc:
                logger.warning(
                    "Error checking support for %s: %s", scanner.name, exc
                )

        if not compatible:
            logger.warning("No compatible scanners found for this repository")

        logger.info(
            "Scanner factory selected %d scanner(s): %s",
            len(compatible),
            [s.name for s in compatible],
        )
        return compatible

    def _build_registry(self) -> list[BaseScanner]:
        """
        Instantiate every known scanner.

        To add a new scanner, simply append it here and implement
        ``BaseScanner``.  No other code needs to change.
        """
        return [
            SemgrepScanner(command_runner=self._runner),
            BanditScanner(command_runner=self._runner),
            GitleaksScanner(command_runner=self._runner),
            PipAuditScanner(command_runner=self._runner),
            NpmAuditScanner(command_runner=self._runner),
            ESLintScanner(command_runner=self._runner),
        ]
