"""
Scan service — orchestrates the full security scan pipeline:
  Clone → Scan → Trust Score → AI Summary + Recommendations → Persist
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
import threading
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database.models import Repository, Scan
from app.schemas.scan import FindingItem, ScanRequest, ScanResponse, ScanSummary
from app.services.ai.ai_service import AIService
from app.utils.exceptions import NotFoundException

logger = logging.getLogger("cryptanium.scan_service")

# ---------------------------------------------------------------------------
# Ensure project root is on sys.path so that "backend.services.*" scanner
# imports resolve correctly regardless of where uvicorn is started from
# (project root vs backend/ directory).
# ---------------------------------------------------------------------------
_here = os.path.dirname(os.path.abspath(__file__))      # .../backend/app/services/
_project_root = os.path.abspath(os.path.join(_here, "..", "..", ".."))  # Cryptanium/
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

try:
    from backend.services.scanner.orchestrator import ScanOrchestrator
    from backend.services.scanner.models import ScanStatus
except ModuleNotFoundError:
    from services.scanner.orchestrator import ScanOrchestrator  # type: ignore[no-redef]
    from services.scanner.models import ScanStatus  # type: ignore[no-redef]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _compute_trust_score(findings: list[dict[str, Any]]) -> int:
    """
    Compute a trust score 0–100 based on severity counts.
    Starts at 100 and deducts per finding.
    """
    score = 100
    deductions = {"Critical": 20, "High": 10, "Medium": 4, "Low": 1}
    for f in findings:
        sev = f.get("severity", "Low")
        score -= deductions.get(sev, 1)
    return max(0, min(100, score))


def _normalise_severity(raw: str) -> str:
    """Map scanner enum values to title-case for consistent frontend display."""
    mapping = {
        "CRITICAL": "Critical", "HIGH": "High", "MEDIUM": "Medium",
        "LOW": "Low", "INFO": "Info", "UNKNOWN": "Low",
    }
    return mapping.get(raw.upper(), raw.capitalize())


# ---------------------------------------------------------------------------
# Exception
# ---------------------------------------------------------------------------

class ScanServiceError(Exception):
    """Raised for errors during scan execution."""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

class ScanService:
    """Service handling repository scan job lifecycle and persistence."""

    # The scanner creates temporary workspaces and invokes CPU/network-heavy
    # command-line tools. One active job keeps resource use predictable and
    # makes the live-scan view unambiguous.
    _active_scan_lock = threading.Lock()

    # ------------------------------------------------------------------
    # Main pipeline: execute a full scan end-to-end
    # ------------------------------------------------------------------

    def execute_scan(self, request: ScanRequest, db: Session) -> ScanResponse:
        """Run the full scan pipeline and persist results to the database."""
        if not self._active_scan_lock.acquire(blocking=False):
            raise ScanServiceError(
                "Another repository is currently being scanned. Wait for it to finish before starting a new scan.",
                status_code=409,
            )

        try:
            return self._execute_scan(request=request, db=db)
        finally:
            self._active_scan_lock.release()

    def _execute_scan(self, request: ScanRequest, db: Session) -> ScanResponse:
        """Execute a scan while the process-wide single-scan lock is held."""
        repo_id_str = (
            str(request.repository_id).strip()
            if request.repository_id is not None
            else None
        )
        repo_name_str = (
            request.repository_name.strip() if request.repository_name else None
        )

        if not repo_id_str and not repo_name_str:
            raise ScanServiceError(
                "Either repository_id or repository_name must be provided.",
                status_code=400,
            )

        repository: Repository | None = None
        if repo_id_str:
            filters = [Repository.github_repo_id == repo_id_str]
            if repo_id_str.isdigit():
                filters.append(Repository.id == int(repo_id_str))
            repository = db.query(Repository).filter(or_(*filters)).first()

        # A frontend repository returned directly by GitHub carries its clone
        # URL. Prefer the matching stored record so scan history uses the
        # familiar owner/repository name instead of the raw URL.
        if repository is None and repo_name_str and repo_name_str.startswith(("https://", "http://", "git@")):
            repository = db.query(Repository).filter(Repository.clone_url == repo_name_str).first()

        if repo_id_str and repository is None and not repo_name_str:
            raise ScanServiceError(
                f"Repository {repo_id_str} was not found. Sync GitHub repositories and try again.",
                status_code=404,
            )

        identifier = (
            repository.clone_url if repository and repository.clone_url
            else repo_name_str or repo_id_str or "unknown-repository"
        )
        resolved_repository_id = str(repository.id) if repository else repo_id_str
        repo_display_name = (
            repository.full_name if repository else (repo_name_str or f"repo-{repo_id_str}")
        )

        # Normalise a shorthand owner/repository name to a full GitHub URL.
        target_url = identifier
        if not target_url.startswith(("https://", "http://", "git@")):
            target_url = f"https://github.com/{target_url}"

        # ── 1. Run scanner ───────────────────────────────────────────────
        logger.info("Starting scan for %s", target_url)
        try:
            report = asyncio.run(
                ScanOrchestrator().scan(target_url, tools=request.tools)
            )
        except Exception as exc:
            logger.error("Scanner failed: %s", exc)
            raise ScanServiceError(
                f"Scanner failed: {exc}", status_code=500
            ) from exc

        # ── 2. Serialise findings with normalised field names ────────────
        raw_findings: list[dict[str, Any]] = []
        for finding in report.findings:
            sev_raw = (
                finding.severity.value
                if hasattr(finding.severity, "value")
                else str(finding.severity)
            )
            raw_findings.append({
                "id": finding.id,
                "rule_id": finding.rule or "",
                "severity": _normalise_severity(sev_raw),
                "description": finding.description or finding.title or "",
                "file_path": finding.file or "",
                "line_number": finding.line or 0,
                "tool": finding.tool or "",
            })

        total_findings = len(raw_findings)
        critical_sev = sum(1 for f in raw_findings if f.get("severity") == "Critical")
        high_sev = sum(1 for f in raw_findings if f.get("severity") == "High")
        med_sev = sum(1 for f in raw_findings if f.get("severity") == "Medium")
        low_sev = sum(1 for f in raw_findings if f.get("severity") == "Low")

        # ── 3. Compute real trust score ──────────────────────────────────
        trust_score = _compute_trust_score(raw_findings)

        # ── 4. AI analysis ───────────────────────────────────────────────
        ai_service = AIService()
        summary_data = ai_service.generate_summary(raw_findings, repo_display_name)
        recommendations = ai_service.generate_recommendations(raw_findings, repo_display_name)

        # ── 5. Persist to database ───────────────────────────────────────
        report_status = report.status.value if hasattr(report.status, "value") else str(report.status)
        scan_status = "completed" if report_status.lower() == "success" else report_status.lower()
        scan_record = Scan(
            repository_id=resolved_repository_id,
            repository_name=repo_display_name,
            status=scan_status.lower(),
            trust_score=trust_score,
            findings_count=total_findings,
            critical_severity_count=critical_sev,
            high_severity_count=high_sev,
            medium_severity_count=med_sev,
            low_severity_count=low_sev,
            findings_json=json.dumps(raw_findings),
            scanner_results_json=json.dumps(
                [result.model_dump(mode="json") for result in report.scan_results]
            ),
            ai_summary=summary_data.get("executive_summary", ""),
            ai_risk_level=summary_data.get("risk_level", "Unknown"),
            ai_key_concerns=json.dumps(summary_data.get("key_concerns", [])),
            ai_recommendations=json.dumps(recommendations),
            started_at=report.started_at,
            completed_at=report.completed_at,
        )
        db.add(scan_record)
        if repository is not None:
            repository.last_scan = report.completed_at
        db.commit()
        db.refresh(scan_record)

        # ── 6. Build response ────────────────────────────────────────────
        findings_list = self._to_finding_items(raw_findings)
        scan_summary = ScanSummary(
            total_findings=total_findings,
            high_severity_count=high_sev + critical_sev,
            medium_severity_count=med_sev,
            low_severity_count=low_sev,
        )

        return ScanResponse(
            scan_id=scan_record.id,
            repository_id=resolved_repository_id,
            repository_name=scan_record.repository_name,
            status=scan_record.status,
            trust_score=trust_score,
            findings_count=total_findings,
            summary=scan_summary,
            findings=findings_list,
            ai_summary=summary_data.get("executive_summary"),
            ai_recommendations=recommendations,
            started_at=scan_record.started_at,
            completed_at=scan_record.completed_at,
            created_at=scan_record.created_at,
        )

    # ------------------------------------------------------------------
    # CRUD helpers
    # ------------------------------------------------------------------

    def create_scan_job(
        self, db: Session, repository_id: int | str, repository_name: str | None = None
    ) -> ScanResponse:
        """Create a new pending scan job for a repository."""
        repo_name: str = repository_name or ""

        if isinstance(repository_id, int) or (
            isinstance(repository_id, str) and repository_id.isdigit()
        ):
            repo_id_int = int(repository_id)
            repo = db.query(Repository).filter(Repository.id == repo_id_int).first()
            if repo:
                repo_name = repo.name

        if not repo_name:
            repo_name = f"repo-{repository_id}"

        scan_record = Scan(
            repository_id=str(repository_id),
            repository_name=repo_name,
            status="pending",
            trust_score=None,
            findings_count=0,
        )
        db.add(scan_record)
        db.commit()
        db.refresh(scan_record)
        return self._map_to_response(scan_record)

    def list_scans(self, db: Session) -> list[ScanResponse]:
        """Retrieve all scan jobs from the database."""
        scans = db.query(Scan).order_by(Scan.created_at.desc()).all()
        return [self._map_to_response(s) for s in scans]

    def get_scan_by_id(self, db: Session, scan_id: int) -> ScanResponse:
        """Retrieve scan job by ID."""
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if not scan:
            raise NotFoundException(f"Scan with ID {scan_id} not found.")
        return self._map_to_response(scan)

    def start_scan_job(self, db: Session, scan_id: int) -> ScanResponse:
        """Transition scan job status to in_progress."""
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if not scan:
            raise NotFoundException(f"Scan with ID {scan_id} not found.")
        scan.status = "in_progress"
        scan.started_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(scan)
        return self._map_to_response(scan)

    def cancel_scan_job(self, db: Session, scan_id: int) -> ScanResponse:
        """Cancel a pending or in_progress scan job."""
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if not scan:
            raise NotFoundException(f"Scan with ID {scan_id} not found.")
        scan.status = "cancelled"
        db.commit()
        db.refresh(scan)
        return self._map_to_response(scan)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _to_finding_items(self, raw: list[dict[str, Any]]) -> list[FindingItem]:
        items: list[FindingItem] = []
        for r in raw:
            try:
                items.append(
                    FindingItem(
                        id=str(r.get("id", "")),
                        rule_id=r.get("rule_id", ""),
                        severity=r.get("severity", "Low"),
                        description=r.get("description", ""),
                        file_path=r.get("file_path", ""),
                        line_number=int(r.get("line_number", 0)),
                        tool=r.get("tool", ""),
                    )
                )
            except Exception:
                continue
        return items

    def _map_to_response(self, scan: Scan) -> ScanResponse:
        crit = getattr(scan, "critical_severity_count", None) or 0
        summary = ScanSummary(
            total_findings=scan.findings_count or 0,
            high_severity_count=(scan.high_severity_count or 0) + crit,
            medium_severity_count=scan.medium_severity_count or 0,
            low_severity_count=scan.low_severity_count or 0,
        )

        # Restore findings list if available
        findings: list[FindingItem] = []
        raw_json = getattr(scan, "findings_json", None)
        if raw_json:
            try:
                findings = self._to_finding_items(json.loads(raw_json))
            except Exception:
                findings = []

        # Restore AI recommendations
        ai_recs: list[dict] = []
        raw_recs = getattr(scan, "ai_recommendations", None)
        if raw_recs:
            try:
                ai_recs = json.loads(raw_recs)
            except Exception:
                ai_recs = []

        return ScanResponse(
            scan_id=scan.id,
            repository_id=scan.repository_id,
            repository_name=scan.repository_name,
            status=scan.status,
            trust_score=scan.trust_score or 0,
            findings_count=scan.findings_count or 0,
            summary=summary,
            findings=findings,
            ai_summary=getattr(scan, "ai_summary", None),
            ai_recommendations=ai_recs,
            started_at=scan.started_at,
            completed_at=scan.completed_at,
            created_at=scan.created_at,
        )
