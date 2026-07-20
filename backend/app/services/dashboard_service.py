from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.models import Scan
from app.database.schemas import DashboardResponse, RecentScanItem


class DashboardService:
    """Service providing aggregate security metrics and recent scan analytics."""

    def get_dashboard_data(self, db: Session) -> DashboardResponse:
        """Compute aggregate metrics across scan history using SQLAlchemy ORM."""
        total_scans = db.query(func.count(Scan.id)).scalar() or 0

        if total_scans == 0:
            return DashboardResponse(
                total_repositories=0,
                total_scans=0,
                average_trust_score=0.0,
                total_vulnerabilities=0,
                high_severity_count=0,
                medium_severity_count=0,
                low_severity_count=0,
                recent_scans=[],
            )

        total_repositories = (
            db.query(func.count(func.distinct(Scan.repository_name))).scalar() or 0
        )
        raw_avg_trust = db.query(func.avg(Scan.trust_score)).scalar()
        average_trust_score = (
            round(float(raw_avg_trust), 2) if raw_avg_trust is not None else 0.0
        )

        total_vulnerabilities = db.query(func.sum(Scan.findings_count)).scalar() or 0
        high_severity_count = (
            db.query(func.sum(Scan.high_severity_count)).scalar() or 0
        )
        medium_severity_count = (
            db.query(func.sum(Scan.medium_severity_count)).scalar() or 0
        )
        low_severity_count = db.query(func.sum(Scan.low_severity_count)).scalar() or 0

        # Fetch last 10 scans ordered by creation date descending
        recent_scan_records = (
            db.query(Scan)
            .order_by(Scan.created_at.desc(), Scan.id.desc())
            .limit(10)
            .all()
        )

        recent_scans = [
            RecentScanItem(
                scan_id=scan.id,
                repository_id=scan.repository_id,
                repository_name=scan.repository_name,
                status=scan.status,
                trust_score=scan.trust_score or 85,
                findings_count=scan.findings_count,
                created_at=scan.created_at,
            )
            for scan in recent_scan_records
        ]

        return DashboardResponse(
            total_repositories=total_repositories,
            total_scans=total_scans,
            average_trust_score=average_trust_score,
            total_vulnerabilities=total_vulnerabilities,
            high_severity_count=high_severity_count,
            medium_severity_count=medium_severity_count,
            low_severity_count=low_severity_count,
            recent_scans=recent_scans,
        )
