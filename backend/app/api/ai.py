"""
AI REST endpoints for the Cryptanium platform.

POST /ai/chat           — Interactive AI assistant (with optional scan context)
POST /ai/analyze/{id}  — Auto-generate summary + recommendations for a scan
GET  /ai/summary/{id}  — Retrieve persisted AI summary for a scan
"""
from __future__ import annotations

import json
import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import Scan
from app.services.ai.ai_service import AIService

logger = logging.getLogger("cryptanium.api.ai")
router = APIRouter(prefix="/ai", tags=["AI Assistant"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    message: str
    scan_id: int | None = None  # optional — provides scan context to the AI


class ChatResponse(BaseModel):
    response: str
    model: str = "nvidia/nemotron-4-340b-instruct"


class AnalyzeResponse(BaseModel):
    scan_id: int
    executive_summary: str
    risk_level: str
    key_concerns: list[str]
    recommendations: list[dict[str, Any]]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_ai_service() -> AIService:
    return AIService()


def _build_scan_context(scan: Scan) -> dict[str, Any]:
    """Convert a Scan ORM record to the context dict the AI service expects."""
    findings: list[dict[str, Any]] = []
    # The raw findings_json is stored as JSON text when available
    raw_json = getattr(scan, "findings_json", None)
    if raw_json:
        try:
            findings = json.loads(raw_json)
        except (json.JSONDecodeError, TypeError):
            findings = []

    ai_summary = getattr(scan, "ai_summary", None) or ""

    return {
        "repository_name": scan.repository_name,
        "trust_score": scan.trust_score or 0,
        "findings_count": scan.findings_count or 0,
        "ai_summary": ai_summary,
        "findings": findings,
    }


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="AI Security Assistant Chat",
)
def ai_chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    ai_service: AIService = Depends(_get_ai_service),
) -> ChatResponse:
    """
    Send a message to the Cryptanium AI assistant.
    Optionally provide a `scan_id` to give the AI context about a specific scan.
    """
    scan_context: dict[str, Any] | None = None

    if request.scan_id is not None:
        scan = db.query(Scan).filter(Scan.id == request.scan_id).first()
        if scan:
            scan_context = _build_scan_context(scan)

    response_text = ai_service.chat(
        user_message=request.message,
        scan_context=scan_context,
    )

    return ChatResponse(response=response_text)


@router.post(
    "/analyze/{scan_id}",
    response_model=AnalyzeResponse,
    summary="Generate AI Analysis for a Scan",
)
def analyze_scan(
    scan_id: int,
    db: Session = Depends(get_db),
    ai_service: AIService = Depends(_get_ai_service),
) -> AnalyzeResponse:
    """
    Auto-generate an AI executive summary and prioritised recommendations
    for the specified scan. Results are persisted to the database.
    """
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan {scan_id} not found.",
        )

    # Load findings from persisted JSON
    findings: list[dict[str, Any]] = []
    raw_json = getattr(scan, "findings_json", None)
    if raw_json:
        try:
            findings = json.loads(raw_json)
        except (json.JSONDecodeError, TypeError):
            findings = []

    repo_name = scan.repository_name or "Unknown Repository"

    # Generate
    summary_data = ai_service.generate_summary(findings, repo_name)
    recommendations = ai_service.generate_recommendations(findings, repo_name)

    # Persist AI results back to the scan record
    try:
        scan.ai_summary = summary_data.get("executive_summary", "")  # type: ignore[attr-defined]
        scan.ai_risk_level = summary_data.get("risk_level", "Unknown")  # type: ignore[attr-defined]
        scan.ai_key_concerns = json.dumps(summary_data.get("key_concerns", []))  # type: ignore[attr-defined]
        scan.ai_recommendations = json.dumps(recommendations)  # type: ignore[attr-defined]
        db.commit()
        db.refresh(scan)
    except Exception as exc:
        logger.warning("Could not persist AI results: %s", exc)
        db.rollback()

    return AnalyzeResponse(
        scan_id=scan_id,
        executive_summary=summary_data.get("executive_summary", ""),
        risk_level=summary_data.get("risk_level", "Unknown"),
        key_concerns=summary_data.get("key_concerns", []),
        recommendations=recommendations,
    )


@router.get(
    "/summary/{scan_id}",
    response_model=AnalyzeResponse,
    summary="Get Persisted AI Summary for a Scan",
)
def get_ai_summary(
    scan_id: int,
    db: Session = Depends(get_db),
) -> AnalyzeResponse:
    """
    Retrieve the previously generated AI summary and recommendations for a scan.
    Returns 404 if no AI analysis has been run yet.
    """
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan {scan_id} not found.",
        )

    ai_summary = getattr(scan, "ai_summary", None) or ""
    ai_risk_level = getattr(scan, "ai_risk_level", None) or "Unknown"
    ai_concerns_raw = getattr(scan, "ai_key_concerns", None) or "[]"
    ai_recs_raw = getattr(scan, "ai_recommendations", None) or "[]"

    try:
        key_concerns = json.loads(ai_concerns_raw)
    except (json.JSONDecodeError, TypeError):
        key_concerns = []
    try:
        recommendations = json.loads(ai_recs_raw)
    except (json.JSONDecodeError, TypeError):
        recommendations = []

    if not ai_summary and not recommendations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No AI analysis found for scan {scan_id}. Call POST /ai/analyze/{scan_id} first.",
        )

    return AnalyzeResponse(
        scan_id=scan_id,
        executive_summary=ai_summary,
        risk_level=ai_risk_level,
        key_concerns=key_concerns,
        recommendations=recommendations,
    )
