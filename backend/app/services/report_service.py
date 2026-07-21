import json
import os
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.database.models import Report, Scan
from app.schemas.report import ReportResponse
from app.utils.exceptions import NotFoundException

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
except Exception:  # pragma: no cover - reportlab may be unavailable in some environments
    colors = None  # type: ignore[assignment]
    letter = None  # type: ignore[assignment]
    getSampleStyleSheet = None  # type: ignore[assignment]
    Paragraph = Spacer = SimpleDocTemplate = Table = TableStyle = None  # type: ignore[assignment]


class ReportService:
    """Service handling report persistence, download paths, and artifact generation."""

    def __init__(self) -> None:
        self.storage_dir = Path(__file__).resolve().parents[3] / "reports_storage"
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def list_reports(self, db: Session) -> list[ReportResponse]:
        reports = db.query(Report).order_by(Report.generated_at.desc()).all()
        return [
            ReportResponse(
                id=r.id,
                scan_id=r.scan_id,
                report_type=r.report_type,
                report_path=r.report_path,
                generated_at=r.generated_at,
                download_url=f"/reports/{r.id}/pdf",
            )
            for r in reports
        ]

    def get_report_by_id(self, db: Session, report_id: int) -> ReportResponse:
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report:
            report = self._generate_report_for_scan(db=db, scan_id=report_id)
            if not report:
                raise NotFoundException(f"Report with ID {report_id} not found.")
        return ReportResponse(
            id=report.id,
            scan_id=report.scan_id,
            report_type=report.report_type,
            report_path=report.report_path,
            generated_at=report.generated_at,
            download_url=f"/reports/{report.id}/pdf",
        )

    def generate_report(self, db: Session, report_id: int) -> ReportResponse:
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report:
            report = self._generate_report_for_scan(db=db, scan_id=report_id)
            if not report:
                raise NotFoundException(f"Report with ID {report_id} not found.")
        self._ensure_artifacts(db=db, report=report)
        return self.get_report_by_id(db=db, report_id=report.id)

    def get_report_download(self, db: Session, report_id: int) -> dict[str, Any]:
        report = self.get_report_by_id(db=db, report_id=report_id)
        report_row = db.query(Report).filter(Report.id == report.id).first()
        if not report_row:
            raise NotFoundException(f"Report with ID {report_id} not found.")
        self._ensure_artifacts(db=db, report=report_row)
        report_path = report_row.report_path or str(self.storage_dir / f"report_{report_row.id}.pdf")
        json_path = str(self.storage_dir / f"report_{report_row.id}.json")
        return {
            "report_id": report.id,
            "scan_id": report.scan_id,
            "report_type": report.report_type,
            "download_url": report.download_url,
            "pdf_path": report_path,
            "json_path": json_path,
            "message": "Report metadata retrieved successfully for download.",
        }

    def _generate_report_for_scan(self, db: Session, scan_id: int) -> Report | None:
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if not scan:
            return None
        report = Report(
            scan_id=scan.id,
            report_type="pdf",
            report_path=str(self.storage_dir / f"report_{scan.id}.pdf"),
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        self._ensure_artifacts(db=db, report=report)
        return report

    def _ensure_artifacts(self, db: Session, report: Report) -> None:
        scan = db.query(Scan).filter(Scan.id == report.scan_id).first()
        if not scan:
            return

        pdf_path = str(self.storage_dir / f"report_{report.id}.pdf")
        json_path = str(self.storage_dir / f"report_{report.id}.json")

        findings: list[dict[str, Any]] = []
        if scan.findings_json:
            try:
                findings = json.loads(scan.findings_json)
            except (TypeError, json.JSONDecodeError):
                findings = []

        report_payload = {
            "scan_id": scan.id,
            "repository": scan.repository_name or "Unknown Repository",
            "status": scan.status,
            "trust_score": scan.trust_score or 0,
            "findings_count": scan.findings_count or 0,
            "findings": findings,
            "ai_summary": scan.ai_summary or "",
            "ai_recommendations": json.loads(scan.ai_recommendations or "[]") if scan.ai_recommendations else [],
            "critical_count": scan.critical_severity_count or 0,
            "high_count": scan.high_severity_count or 0,
            "medium_count": scan.medium_severity_count or 0,
            "low_count": scan.low_severity_count or 0,
        }

        with open(json_path, "w", encoding="utf-8") as handle:
            json.dump(report_payload, handle, indent=2)

        self._write_pdf(pdf_path, report_payload)

        report.report_path = pdf_path
        report.generated_at = report.generated_at or scan.completed_at or scan.created_at
        db.commit()

    def _write_pdf(self, pdf_path: str, payload: dict[str, Any]) -> None:
        if not all([colors, letter, getSampleStyleSheet, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle]):
            with open(pdf_path, "w", encoding="utf-8") as handle:
                handle.write("PDF generation unavailable in this environment.\n")
            return

        styles = getSampleStyleSheet()
        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        story = []
        story.append(Paragraph("Cryptanium Security Report", styles["Title"]))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"Repository: {payload.get('repository', 'Unknown')}", styles["Heading2"]))
        story.append(Paragraph(f"Status: {payload.get('status', 'unknown')}", styles["BodyText"]))
        story.append(Paragraph(f"Trust Score: {payload.get('trust_score', 0)}/100", styles["BodyText"]))
        story.append(Paragraph(f"Findings: {payload.get('findings_count', 0)}", styles["BodyText"]))
        story.append(Spacer(1, 12))
        findings = payload.get("findings", []) or []
        rows = [["Severity", "Description", "Tool"]]
        for finding in findings[:10]:
            rows.append([finding.get("severity", "Low"), (finding.get("description") or "")[:120], finding.get("tool", "")])
        table = Table(rows, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#7B61FF")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ]))
        story.append(table)
        doc.build(story)
