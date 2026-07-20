"""
Scanner & AI Trust Integration Bridge for Cryptanium.
Connects Scanner Orchestrator (Member 3) with Trust Score & AI Generators (Member 4).
"""

import os
import asyncio
import logging
from typing import Dict, Any, Optional

from backend.services.scanner.orchestrator import ScanOrchestrator
from backend.utils.parser import ScanPayload
from backend.trust.trust_engine import TrustEngine
from backend.ai.summary_generator import AISummaryGenerator
from backend.ai.recommendation_generator import AIRecommendationEngine
from backend.reports.pdf_generator import PDFReportGenerator
from backend.reports.json_export import JSONReportGenerator

logger = logging.getLogger("cryptanium.scanner_service")


async def run_full_scan_pipeline(
    repo_url_or_identifier: str,
    repository_name: str = "",
    branch: str = "main",
    output_dir: str = "reports_storage",
) -> Dict[str, Any]:
    """
    Executes end-to-end security pipeline:
    Clone -> Detect -> Multi-tool Scan -> Normalize -> Trust Engine -> AI Summaries & Recs -> PDF/JSON Reports.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Format URL if short name given
    target_url = repo_url_or_identifier
    if not target_url.startswith("http://") and not target_url.startswith("https://") and not target_url.startswith("git@"):
        target_url = f"https://github.com/{target_url}"

    repo_name = repository_name or repo_url_or_identifier

    # 2. Run Scanner Orchestrator (Member 3)
    orchestrator = ScanOrchestrator()
    scan_report = await orchestrator.scan(target_url)

    # 3. Convert ScanReport to ScanPayload (Member 4)
    payload = ScanPayload.from_scan_report(scan_report, repository=repo_name, branch=branch)

    # 4. Calculate Trust Score (Member 4)
    engine = TrustEngine()
    trust_result = engine.calculate_score(payload)

    # 5. Generate AI Executive Summary & Recommendations (Member 4)
    summary_gen = AISummaryGenerator()
    summary = summary_gen.generate_summary(payload, trust_result)

    rec_gen = AIRecommendationEngine()
    recommendations = rec_gen.generate_recommendations(payload)

    # 6. Generate JSON and PDF Reports
    safe_repo_slug = repo_name.replace("/", "_").replace("\\", "_")
    json_filename = f"report_{scan_report.scan_id}_{safe_repo_slug}.json"
    pdf_filename = f"report_{scan_report.scan_id}_{safe_repo_slug}.pdf"
    
    json_path = os.path.join(output_dir, json_filename)
    pdf_path = os.path.join(output_dir, pdf_filename)

    JSONReportGenerator().save_json_file(payload, trust_result, summary, recommendations, json_path)
    PDFReportGenerator().generate_pdf(payload, trust_result, summary, recommendations, pdf_path)

    return {
        "scan_id": scan_report.scan_id,
        "status": scan_report.status.value if hasattr(scan_report.status, "value") else str(scan_report.status),
        "trust_score": trust_result.final_score,
        "risk_level": trust_result.risk_level,
        "total_findings": scan_report.total_findings,
        "critical_count": scan_report.critical_count,
        "high_count": scan_report.high_count,
        "medium_count": scan_report.medium_count,
        "low_count": scan_report.low_count,
        "info_count": scan_report.info_count,
        "duration_seconds": scan_report.duration_seconds,
        "summary": summary,
        "recommendations": recommendations,
        "findings": [f.model_dump() for f in payload.findings],
        "pdf_path": pdf_path,
        "json_path": json_path,
    }


def scan_repository(repo_identifier: str) -> Dict[str, Any]:
    """Synchronous fallback/legacy wrapper for background task execution."""
    return asyncio.run(run_full_scan_pipeline(repo_identifier))
