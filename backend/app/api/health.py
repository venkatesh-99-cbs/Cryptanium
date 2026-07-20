from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.database import get_db

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    summary="System Health & Status Check",
)
def check_health(db: Session = Depends(get_db)):
    """Check health status of backend, database connectivity, and GitHub API configuration."""
    db_status = "healthy"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "unhealthy"

    github_configured = bool(settings.GITHUB_CLIENT_ID and settings.GITHUB_CLIENT_SECRET)
    github_status = "configured" if github_configured else "unconfigured"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database": db_status,
        "github_api": github_status,
        "version": getattr(settings, "API_VERSION", "1.0.0"),
    }
