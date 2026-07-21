import os

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.report import ReportResponse
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["Reports"])


def get_report_service() -> ReportService:
    return ReportService()


@router.get(
    "",
    response_model=list[ReportResponse],
    summary="List all generated report metadata",
)
def list_reports(
    db: Session = Depends(get_db),
    report_service: ReportService = Depends(get_report_service),
):
    """Retrieve metadata for all generated security reports."""
    return report_service.list_reports(db=db)


@router.get(
    "/{id}",
    response_model=ReportResponse,
    summary="Get report metadata by ID",
)
def get_report_by_id(
    id: int,
    db: Session = Depends(get_db),
    report_service: ReportService = Depends(get_report_service),
):
    """Retrieve specific report metadata by ID."""
    return report_service.get_report_by_id(db=db, report_id=id)


@router.get(
    "/{id}/pdf",
    summary="Download PDF security report",
)
def download_pdf_report(
    id: int,
    db: Session = Depends(get_db),
    report_service: ReportService = Depends(get_report_service),
):
    """Downloads the generated PDF report for a given scan or report ID."""
    report_meta = report_service.get_report_download(db=db, report_id=id)
    pdf_path = report_meta.get("pdf_path")
    if not pdf_path or not os.path.exists(pdf_path):
        pdf_path = f"reports_storage/report_{id}.pdf"
        if not os.path.exists(pdf_path):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PDF report file not found.")

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=os.path.basename(pdf_path),
    )


@router.get(
    "/{id}/json",
    summary="Download JSON security report",
)
def download_json_report(
    id: int,
    db: Session = Depends(get_db),
    report_service: ReportService = Depends(get_report_service),
):
    """Downloads the generated JSON report for a given scan or report ID."""
    report_meta = report_service.get_report_download(db=db, report_id=id)
    json_path = report_meta.get("json_path")
    if not json_path or not os.path.exists(json_path):
        json_path = f"reports_storage/report_{id}.json"
        if not os.path.exists(json_path):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="JSON report file not found.")

    return FileResponse(
        json_path,
        media_type="application/json",
        filename=os.path.basename(json_path),
    )
