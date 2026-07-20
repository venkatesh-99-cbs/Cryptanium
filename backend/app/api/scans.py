from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.scan import ScanRequest, ScanResponse
from app.services.scan_service import ScanService, ScanServiceError

router = APIRouter(tags=["Scans"])


def get_scan_service() -> ScanService:
    return ScanService()


@router.get(
    "/scans",
    response_model=list[ScanResponse],
    summary="List all scan jobs",
)
def list_scans(
    db: Session = Depends(get_db),
    scan_service: ScanService = Depends(get_scan_service),
):
    """Retrieve list of all scan jobs."""
    return scan_service.list_scans(db=db)


@router.get(
    "/scans/{id}",
    response_model=ScanResponse,
    summary="Get scan job details by ID",
)
def get_scan(
    id: int,
    db: Session = Depends(get_db),
    scan_service: ScanService = Depends(get_scan_service),
):
    """Retrieve details for a specific scan job."""
    return scan_service.get_scan_by_id(db=db, scan_id=id)


@router.post(
    "/scan",
    response_model=ScanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Initiate immediate repository scan",
)
def create_scan(
    request: ScanRequest,
    db: Session = Depends(get_db),
    scan_service: ScanService = Depends(get_scan_service),
):
    """Triggers immediate scan for requested repository and returns results."""
    try:
        return scan_service.execute_scan(request=request, db=db)
    except ScanServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.post(
    "/scans/{id}/start",
    response_model=ScanResponse,
    summary="Start a scan job",
)
def start_scan(
    id: int,
    db: Session = Depends(get_db),
    scan_service: ScanService = Depends(get_scan_service),
):
    """Transition scan job status to in_progress."""
    return scan_service.start_scan_job(db=db, scan_id=id)


@router.post(
    "/scans/{id}/cancel",
    response_model=ScanResponse,
    summary="Cancel a scan job",
)
def cancel_scan(
    id: int,
    db: Session = Depends(get_db),
    scan_service: ScanService = Depends(get_scan_service),
):
    """Cancel a pending or in-progress scan job."""
    return scan_service.cancel_scan_job(db=db, scan_id=id)
