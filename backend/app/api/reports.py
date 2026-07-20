from fastapi import APIRouter, Depends
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
    "/download/{id}",
    summary="Get report download link and metadata",
)
def download_report(
    id: int,
    db: Session = Depends(get_db),
    report_service: ReportService = Depends(get_report_service),
):
    """Retrieve report download path and URL for specified report ID."""
    return report_service.get_report_download(db=db, report_id=id)
