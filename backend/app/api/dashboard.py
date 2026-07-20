from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.schemas import DashboardResponse
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def get_dashboard_service() -> DashboardService:
    return DashboardService()


@router.get(
    "",
    response_model=DashboardResponse,
    summary="Get aggregated security dashboard metrics",
)
def get_dashboard(
    db: Session = Depends(get_db),
    dashboard_service: DashboardService = Depends(get_dashboard_service),
):
    """Retrieve security dashboard analytics including total repos, scans, trust score, vulnerability breakdown, and recent scan history."""
    try:
        return dashboard_service.get_dashboard_data(db=db)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch dashboard metrics: {str(exc)}",
        )
