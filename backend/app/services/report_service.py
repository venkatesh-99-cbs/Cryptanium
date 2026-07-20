from sqlalchemy.orm import Session

from app.database.models import Report, Scan
from app.schemas.report import ReportResponse
from app.utils.exceptions import NotFoundException


class ReportService:
    """Service handling report metadata retrieval and download URLs."""

    def list_reports(self, db: Session) -> list[ReportResponse]:
        """List all generated security reports."""
        reports = db.query(Report).order_by(Report.generated_at.desc()).all()
        return [
            ReportResponse(
                id=r.id,
                scan_id=r.scan_id,
                report_type=r.report_type,
                report_path=r.report_path,
                generated_at=r.generated_at,
                download_url=f"/reports/download/{r.id}",
            )
            for r in reports
        ]

    def get_report_by_id(self, db: Session, report_id: int) -> ReportResponse:
        """Fetch report metadata by ID."""
        r = db.query(Report).filter(Report.id == report_id).first()
        if not r:
            # If no report DB entry exists yet, auto-populate report entry if scan exists
            scan = db.query(Scan).filter(Scan.id == report_id).first()
            if scan:
                r = Report(
                    scan_id=scan.id,
                    report_type="pdf",
                    report_path=f"/reports/scan_{scan.id}_report.pdf",
                )
                db.add(r)
                db.commit()
                db.refresh(r)
            else:
                raise NotFoundException(f"Report with ID {report_id} not found.")

        return ReportResponse(
            id=r.id,
            scan_id=r.scan_id,
            report_type=r.report_type,
            report_path=r.report_path,
            generated_at=r.generated_at,
            download_url=f"/reports/download/{r.id}",
        )

    def get_report_download(self, db: Session, report_id: int) -> dict:
        """Retrieve report download metadata and download link."""
        report = self.get_report_by_id(db, report_id)
        return {
            "report_id": report.id,
            "scan_id": report.scan_id,
            "report_type": report.report_type,
            "download_url": report.download_url,
            "file_path": report.report_path or f"/reports/scan_{report.scan_id}_report.pdf",
            "message": "Report metadata retrieved successfully for download.",
        }
