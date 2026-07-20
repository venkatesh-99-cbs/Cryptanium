from fastapi import FastAPI

from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="AI-Powered Repository Security Analyzer",
)


@app.get("/")
async def root():
    return {
        "project": settings.APP_NAME,
        "status": "running",
        "version": "1.0.0",
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
    }