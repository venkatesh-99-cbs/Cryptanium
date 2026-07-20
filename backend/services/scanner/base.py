"""
Cryptanium Scanner Engine — Base Scanner

Abstract base class that every concrete scanner inherits from.
Defines the contract (``is_supported``, ``build_command``, ``parse``,
``normalize``) and provides a concrete ``execute`` template-method
that orchestrates the full lifecycle.
"""

from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from pathlib import Path

from backend.services.scanner.command_runner import CommandRunner
from backend.services.scanner.exceptions import (
    ParseError,
    ScannerNotInstalledError,
    ScannerTimeoutError,
)
from backend.services.scanner.models import (
    CommandResult,
    Finding,
    LanguageInfo,
    ProjectInfo,
    ScanResult,
)
from backend.services.scanner.parser import OutputParser

logger = logging.getLogger("cryptanium.scanner")


class BaseScanner(ABC):
    """
    Template-method base class for security scanners.

    Subclasses implement the four abstract hooks; ``execute()``
    orchestrates them into a pipeline that never crashes.
    """

    def __init__(self, command_runner: CommandRunner | None = None) -> None:
        self._runner = command_runner or CommandRunner()

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable scanner name (e.g. ``'semgrep'``)."""

    @property
    def timeout(self) -> int:
        """Maximum execution time in seconds.  Override if needed."""
        return 300

    # ------------------------------------------------------------------
    # Abstract hooks
    # ------------------------------------------------------------------

    @abstractmethod
    def is_supported(
        self, project_info: ProjectInfo, language_info: LanguageInfo
    ) -> bool:
        """Return ``True`` if this scanner should run for the given project."""

    @abstractmethod
    def build_command(self, repo_path: Path) -> list[str]:
        """Return the CLI command (list of tokens) to invoke."""

    @abstractmethod
    def parse(self, raw_output: str) -> list[dict]:
        """Parse the raw CLI output into a list of intermediate dicts."""

    @abstractmethod
    def normalize(self, parsed_results: list[dict], repo_path: Path) -> list[Finding]:
        """Convert intermediate dicts into ``Finding`` instances."""

    # ------------------------------------------------------------------
    # Template method — concrete
    # ------------------------------------------------------------------

    async def execute(self, repo_path: Path) -> ScanResult:
        """
        Full scanner lifecycle:

        1. Build command
        2. Run via ``CommandRunner``
        3. Parse output
        4. Normalize into ``Finding`` list

        Returns a ``ScanResult`` that is **always** safe to consume,
        even when the scanner fails partway through.
        """
        start = time.monotonic()
        logger.info("Scanner '%s' started on %s", self.name, repo_path)

        try:
            # 1. Build
            cmd = self.build_command(repo_path)
            if not cmd:
                raise ScannerNotInstalledError(self.name)

            # 2. Run
            result: CommandResult = await self._runner.run(
                cmd=cmd,
                cwd=repo_path,
                timeout=self.timeout,
            )

            if result.timed_out:
                raise ScannerTimeoutError(self.name, self.timeout)

            # Some scanners use non-zero exit codes for "findings found"
            if not self._is_acceptable_exit_code(result.return_code):
                # Check if tool is missing
                if "not found" in result.stderr.lower() or "not recognized" in result.stderr.lower():
                    raise ScannerNotInstalledError(self.name)

                logger.warning(
                    "Scanner '%s' exited with code %d: %s",
                    self.name, result.return_code, result.stderr[:300],
                )

            # 3. Parse
            raw = result.stdout or ""
            try:
                parsed = self.parse(raw)
            except Exception as exc:
                raise ParseError(self.name, str(exc)) from exc

            # 4. Normalize
            findings = self.normalize(parsed, repo_path)

            elapsed = time.monotonic() - start
            logger.info(
                "Scanner '%s' completed: %d findings (%.1fs)",
                self.name, len(findings), elapsed,
            )
            return ScanResult(
                tool=self.name,
                success=True,
                findings=findings,
                duration_seconds=round(elapsed, 3),
            )

        except (ScannerNotInstalledError, ScannerTimeoutError, ParseError) as exc:
            elapsed = time.monotonic() - start
            logger.error("Scanner '%s' failed: %s", self.name, exc.message)
            return ScanResult(
                tool=self.name,
                success=False,
                error=exc.message,
                duration_seconds=round(elapsed, 3),
            )
        except Exception as exc:
            elapsed = time.monotonic() - start
            logger.exception("Scanner '%s' unexpected error", self.name)
            return ScanResult(
                tool=self.name,
                success=False,
                error=str(exc),
                duration_seconds=round(elapsed, 3),
            )

    # ------------------------------------------------------------------
    # Helpers for subclasses
    # ------------------------------------------------------------------

    def _is_acceptable_exit_code(self, code: int) -> bool:
        """
        Return ``True`` if *code* is considered a non-error exit.

        Many scanners exit with 1 when they *find* issues, which is
        not an error from our perspective.  Override in subclasses
        that have different conventions.
        """
        return code in (0, 1)

    @staticmethod
    def _safe_parse_json(raw: str):
        """Delegate to the shared ``OutputParser``."""
        return OutputParser.safe_parse_json(raw)
