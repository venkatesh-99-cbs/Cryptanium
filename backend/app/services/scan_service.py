from datetime import datetime, timezone
from typing import Any
from sqlalchemy.orm import Session

from app.database.models import Repository, Scan
from app.schemas.scan import FindingItem, ScanRequest, ScanResponse, ScanSummary
from app.services.scanner.scanner_service import scan_repository
from app.utils.exceptions import NotFoundException, ValidationException


class ScanServiceError(Exception):
    """Exception raised for errors during scan execution."""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class ScanService:
    """Service handling repository scan job lifecycle and persistence."""

    def execute_scan(self, request: ScanRequest, db: Session) -> ScanResponse:
        """Legacy helper performing immediate scan execution and recording results."""
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

        identifier = repo_name_str or repo_id_str or "unknown-repository"
        repo_display_name = repo_name_str or f"repo-{repo_id_str}"

        # Step 1: Call placeholder scanner service
        raw_scan_results: dict[str, Any] = scan_repository(identifier)

        summary_data = raw_scan_results.get("summary", {})
        total_findings = summary_data.get("total_findings", 0)
        high_sev = summary_data.get("high_severity_count", 0)
        med_sev = summary_data.get("medium_severity_count", 0)
        low_sev = summary_data.get("low_severity_count", 0)

        # Map FK if repo_id is integer matching Repository table
        repo_fk: int | None = None
        if repo_id_str and repo_id_str.isdigit():
            repo_fk = int(repo_id_str)

        scan_record = Scan(
            repository_id=repo_id_str,
            repository_name=repo_display_name,
            status=raw_scan_results.get("status", "completed"),
            trust_score=raw_scan_results.get("trust_score", 85),
            findings_count=total_findings,
            high_severity_count=high_sev,
            medium_severity_count=med_sev,
            low_severity_count=low_sev,
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
        )
        db.add(scan_record)
        db.commit()
        db.refresh(scan_record)

        findings_list = [
            FindingItem(**item) for item in raw_scan_results.get("findings", [])
        ]
        scan_summary = ScanSummary(
            total_findings=total_findings,
            high_severity_count=high_sev,
            medium_severity_count=med_sev,
            low_severity_count=low_sev,
        )

        return ScanResponse(
            scan_id=scan_record.id,
            repository_id=repo_id_str if repo_id_str is not None else scan_record.repository_id,
            repository_name=scan_record.repository_name,
            status=scan_record.status,
            trust_score=scan_record.trust_score or 85,
            findings_count=scan_record.findings_count,
            summary=scan_summary,
            findings=findings_list,
            started_at=scan_record.started_at,
            completed_at=scan_record.completed_at,
            created_at=scan_record.created_at,
        )

    def create_scan_job(
        self, db: Session, repository_id: int | str, repository_name: str | None = None
    ) -> ScanResponse:
        """Create a new pending scan job for a repository."""
        repo_id_int: int | None = None
        repo_name: str = repository_name or ""

        if isinstance(repository_id, int) or (isinstance(repository_id, str) and repository_id.isdigit()):
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
            trust_score=85,
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

    def _map_to_response(self, scan: Scan) -> ScanResponse:
        summary = ScanSummary(
            total_findings=scan.findings_count or 0,
            high_severity_count=scan.high_severity_count or 0,
            medium_severity_count=scan.medium_severity_count or 0,
            low_severity_count=scan.low_severity_count or 0,
        )
        return ScanResponse(
            scan_id=scan.id,
            repository_id=scan.repository_id,
            repository_name=scan.repository_name,
            status=scan.status,
            trust_score=scan.trust_score or 85,
            findings_count=scan.findings_count or 0,
            summary=summary,
            started_at=scan.started_at,
            completed_at=scan.completed_at,
            created_at=scan.created_at,
        )
