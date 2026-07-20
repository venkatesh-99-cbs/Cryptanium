"""
Cryptanium Scanner Engine — Scan Orchestrator

The **primary entry point** for the Scanner Engine.

The Backend API calls::

    orchestrator = ScanOrchestrator()
    report = await orchestrator.scan("https://github.com/user/repo")

The orchestrator manages the entire pipeline:

    Clone → Detect → Select Scanners → Execute in Parallel →
    Normalize → Cleanup → Return ScanReport
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path

from backend.services.clone.cleanup import CleanupService
from backend.services.clone.clone_service import CloneService
from backend.services.clone.workspace import WorkspaceManager
from backend.services.detector.framework_detector import FrameworkDetector
from backend.services.detector.language_detector import LanguageDetector
from backend.services.detector.package_detector import PackageDetector
from backend.services.detector.project_detector import ProjectDetector
from backend.services.scanner.command_runner import CommandRunner
from backend.services.scanner.exceptions import CloneError, InvalidRepositoryError, ScannerEngineError
from backend.services.scanner.models import (
    ScanReport,
    ScanResult,
    ScanStatus,
    Severity,
)
from backend.services.scanner.normalizer import ResultNormalizer
from backend.services.scanner.scanner_factory import ScannerFactory

logger = logging.getLogger("cryptanium.orchestrator")


class ScanOrchestrator:
    """
    Orchestrate a full security scan of a Git repository.

    This class is **the only thing the Backend API needs to import**.
    All internal wiring (cloning, detection, scanning, cleanup) is
    handled automatically.
    """

    def __init__(self) -> None:
        self._workspace_manager = WorkspaceManager()
        self._command_runner = CommandRunner()
        self._clone_service = CloneService(command_runner=self._command_runner)
        self._cleanup_service = CleanupService(workspace_manager=self._workspace_manager)
        self._project_detector = ProjectDetector()
        self._language_detector = LanguageDetector()
        self._framework_detector = FrameworkDetector()
        self._package_detector = PackageDetector()
        self._scanner_factory = ScannerFactory(command_runner=self._command_runner)
        self._normalizer = ResultNormalizer()

    async def scan(
        self,
        repo_url: str,
        debug: bool = False,
        tools: list[str] | None = None,
    ) -> ScanReport:
        """
        Run the full scan pipeline against *repo_url*.

        Parameters
        ----------
        repo_url:
            HTTPS or SSH Git URL to clone and scan.
        debug:
            If ``True``, the cloned workspace is preserved after the
            scan for manual inspection.

        Returns
        -------
        ScanReport
            A fully populated report with all findings, detection
            metadata, and timing information.
        """
        start = time.monotonic()
        started_at = datetime.now(timezone.utc)
        workspace: Path | None = None

        report = ScanReport(repo_url=repo_url, started_at=started_at)

        try:
            # ── 1. Create workspace ──────────────────────────────
            logger.info("Scan started for %s", repo_url)
            workspace = self._workspace_manager.create()

            # ── 2. Clone ─────────────────────────────────────────
            repo_path = await self._clone_service.clone(repo_url, workspace)

            # ── 3. Detect project characteristics ────────────────
            logger.info("Detection started")
            project_info = self._project_detector.detect(repo_path)
            language_info = self._language_detector.detect(repo_path)
            frameworks = self._framework_detector.detect(repo_path, project_info)
            package_managers = self._package_detector.detect(repo_path, project_info)
            logger.info("Detection completed")

            report.project_info = project_info
            report.language_info = language_info
            report.frameworks = frameworks
            report.package_managers = package_managers

            # ── 4. Select scanners ───────────────────────────────
            scanners = self._scanner_factory.get_scanners(project_info, language_info)
            if tools:
                requested = {tool.strip().lower() for tool in tools}
                scanners = [scanner for scanner in scanners if scanner.name.lower() in requested]

            if not scanners:
                logger.warning("No compatible scanners — returning empty report")
                report.status = ScanStatus.SUCCESS
                self._finalize(report, start)
                return report

            # ── 5. Execute scanners concurrently ─────────────────
            logger.info(
                "Executing %d scanner(s) concurrently: %s",
                len(scanners),
                [s.name for s in scanners],
            )

            # Render's free tier benefits from bounded concurrency: scanners
            # are still independent, but never oversubscribe the small CPU.
            limit = max(1, min(int(os.getenv("SCANNER_MAX_CONCURRENCY", "2")), len(scanners)))
            semaphore = asyncio.Semaphore(limit)

            async def run_scanner(scanner):
                async with semaphore:
                    return await scanner.execute(repo_path)

            tasks = [run_scanner(scanner) for scanner in scanners]
            results: list[ScanResult | BaseException] = await asyncio.gather(
                *tasks, return_exceptions=True
            )

            # ── 6. Collect results ───────────────────────────────
            scan_results: list[ScanResult] = []
            for i, result in enumerate(results):
                if isinstance(result, BaseException):
                    logger.error(
                        "Scanner task %d raised: %s", i, result
                    )
                    scan_results.append(ScanResult(
                        tool=scanners[i].name,
                        success=False,
                        error=str(result),
                    ))
                else:
                    scan_results.append(result)

            report.scan_results = scan_results

            # ── 7. Normalize ─────────────────────────────────────
            all_findings = self._normalizer.normalize(scan_results)
            report.findings = all_findings
            report.total_findings = len(all_findings)

            # Count by severity
            report.critical_count = sum(1 for f in all_findings if f.severity == Severity.CRITICAL)
            report.high_count = sum(1 for f in all_findings if f.severity == Severity.HIGH)
            report.medium_count = sum(1 for f in all_findings if f.severity == Severity.MEDIUM)
            report.low_count = sum(1 for f in all_findings if f.severity == Severity.LOW)
            report.info_count = sum(1 for f in all_findings if f.severity == Severity.INFO)

            # Determine overall status
            any_failed = any(not r.success for r in scan_results)
            any_succeeded = any(r.success for r in scan_results)
            if any_failed and any_succeeded:
                report.status = ScanStatus.PARTIAL
            elif any_failed:
                report.status = ScanStatus.FAILED
            else:
                report.status = ScanStatus.SUCCESS

            logger.info(
                "Scan completed: %d findings (%d critical, %d high, %d medium, %d low, %d info)",
                report.total_findings,
                report.critical_count,
                report.high_count,
                report.medium_count,
                report.low_count,
                report.info_count,
            )

        except (InvalidRepositoryError, CloneError) as exc:
            logger.error("Scan failed during setup: %s", exc.message)
            report.status = ScanStatus.FAILED
            report.scan_results = [ScanResult(tool="clone", success=False, error=exc.message)]

        except ScannerEngineError as exc:
            logger.error("Scan failed: %s", exc.message)
            report.status = ScanStatus.FAILED

        except Exception as exc:
            logger.exception("Unexpected error during scan")
            report.status = ScanStatus.FAILED
            report.scan_results = [ScanResult(tool="engine", success=False, error=str(exc))]

        finally:
            # ── 8. Cleanup ───────────────────────────────────────
            if workspace:
                self._cleanup_service.cleanup(workspace, debug=debug)

            self._finalize(report, start)

        return report

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _finalize(report: ScanReport, start: float) -> None:
        """Set timing fields on the report."""
        report.completed_at = datetime.now(timezone.utc)
        report.duration_seconds = round(time.monotonic() - start, 3)
