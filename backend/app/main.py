from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, dashboard, health, reports, repositories, scans, ai
from app.core.config import settings
from app.core.logger import logger
from app.database.base import Base
from app.database.database import engine, init_db
import app.database.models  # noqa: F401
from app.utils.exceptions import BaseAppException, app_exception_handler

logger.info(f"Initializing Cryptanium Backend (Database: {settings.DATABASE_URL})")

# Run automatic lightweight database initialization & column migrations
init_db(engine)

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Cryptanium - AI-Powered Repository Trust & Security Analysis Platform",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register custom global exception handler
app.add_exception_handler(BaseAppException, app_exception_handler)

# Register API Routers
app.include_router(auth.router)
app.include_router(repositories.router)
app.include_router(scans.router)
app.include_router(reports.router)
app.include_router(dashboard.router)
app.include_router(health.router)
app.include_router(ai.router)


@app.get("/", summary="Root status check")
async def root():
    return {
        "project": settings.APP_NAME,
        "status": "running",
        "version": "1.0.0",
        "documentation": "/docs",
    }