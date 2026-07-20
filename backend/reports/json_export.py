"""
JSON Report Export Generator Module for Cryptanium Member 4.
Exports normalized findings, trust metrics, summaries, and recommendations to standardized JSON.
"""

import json
from typing import Dict, Any, List, Optional
from backend.utils.parser import ScanPayload
from backend.trust.trust_engine import TrustScoreResult
from backend.utils.formatter import get_current_date_formatted


class JSONReportGenerator:
    """Generates standardized downloadable JSON security reports."""

    def build_report_data(
        self,
        payload: ScanPayload,
        trust_result: TrustScoreResult,
        summary: Dict[str, str],
        recommendations: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Constructs full report dictionary conforming to schema requirements."""
        return {
            "repository": payload.repository,
            "branch": payload.branch,
            "language": payload.language,
            "scan_date": payload.scan_date or get_current_date_formatted(),
            "trust_score": trust_result.final_score,
            "risk_level": trust_result.risk_level,
            "score_breakdown": trust_result.to_dict(),
            "summary": summary,
            "recommendations": recommendations,
            "findings": [f.model_dump() for f in payload.findings],
        }

    def generate_json_string(
        self,
        payload: ScanPayload,
        trust_result: TrustScoreResult,
        summary: Dict[str, str],
        recommendations: List[Dict[str, Any]],
        indent: int = 2,
    ) -> str:
        """Returns JSON report as formatted string."""
        report_data = self.build_report_data(payload, trust_result, summary, recommendations)
        return json.dumps(report_data, indent=indent, ensure_ascii=False)

    def save_json_file(
        self,
        payload: ScanPayload,
        trust_result: TrustScoreResult,
        summary: Dict[str, str],
        recommendations: List[Dict[str, Any]],
        output_filepath: str,
    ) -> str:
        """Saves JSON report to specified file path and returns path."""
        json_str = self.generate_json_string(payload, trust_result, summary, recommendations)
        with open(output_filepath, "w", encoding="utf-8") as f:
            f.write(json_str)
        return output_filepath
