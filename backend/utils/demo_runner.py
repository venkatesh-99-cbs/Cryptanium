"""
Demo Runner for Cryptanium Member 4.
Executes full pipeline from raw finding input -> score calculation -> AI summary/recommendations -> PDF & JSON exports.
"""

import os
import sys
import json

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.utils.parser import ScanPayload
from backend.trust.trust_engine import TrustEngine
from backend.ai.summary_generator import AISummaryGenerator
from backend.ai.recommendation_generator import AIRecommendationEngine
from backend.reports.json_export import JSONReportGenerator
from backend.reports.pdf_generator import PDFReportGenerator

MOCK_INPUT_DATA = {
    "repository": "venkatesh-99-cbs/Cryptanium",
    "branch": "main",
    "language": "Python",
    "findings": [
        {
            "severity": "Critical",
            "tool": "Bandit",
            "file": "backend/app/main.py",
            "line": 52,
            "description": "Possible SQL injection in dynamic query construction",
            "recommendation": "Use parameterized queries or SQLAlchemy ORM methods.",
            "owasp": "A03"
        },
        {
            "severity": "High",
            "tool": "Gitleaks",
            "file": "backend/.env",
            "line": 8,
            "description": "Exposed OpenRouter API Key detected in codebase",
            "recommendation": "Revoke API key immediately and add .env to .gitignore.",
            "owasp": "A07"
        },
        {
            "severity": "Medium",
            "tool": "Trivy",
            "file": "backend/requirements.txt",
            "line": 14,
            "description": "Outdated urllib3 library vulnerable to ReDoS CVE-2023-45803",
            "recommendation": "Upgrade urllib3 to version >= 2.0.7",
            "owasp": "A06"
        },
        {
            "severity": "Low",
            "tool": "Bandit",
            "file": "backend/utils/formatter.py",
            "line": 88,
            "description": "Standard pseudo-random generator (random) used for non-cryptographic purpose",
            "recommendation": "Use 'secrets' module for security-sensitive random numbers.",
            "owasp": "A02"
        },
        {
            "severity": "Info",
            "tool": "Semgrep",
            "file": "Dockerfile",
            "line": 2,
            "description": "Base image tag 'latest' used instead of fixed version pin",
            "recommendation": "Pin Docker base image to a specific version digest or tag.",
            "owasp": "A05"
        }
    ]
}


def run_member4_pipeline(input_data: dict, output_dir: str = ".") -> dict:
    """Executes Member 4's end-to-end security report processing."""
    print("=== Cryptanium Security Report Pipeline (Member 4) ===")

    # 1. Parse Input
    print("[1/5] Parsing scan payload...")
    payload = ScanPayload.parse_payload(input_data)
    print(f"      Repository: {payload.repository} ({payload.branch})")
    print(f"      Findings Count: {len(payload.findings)}")

    # 2. Calculate Trust Score
    print("[2/5] Calculating Trust Score...")
    engine = TrustEngine()
    trust_result = engine.calculate_score(payload)
    print(f"      Final Score: {trust_result.final_score}/100")
    print(f"      Risk Level: {trust_result.risk_level}")

    # 3. AI Summaries & Recommendations
    print("[3/5] Generating AI Executive Summary & Recommendations...")
    summary_gen = AISummaryGenerator()
    summary = summary_gen.generate_summary(payload, trust_result)

    rec_gen = AIRecommendationEngine()
    recommendations = rec_gen.generate_recommendations(payload)

    # 4. Generate JSON Export
    print("[4/5] Generating JSON Report...")
    json_path = os.path.join(output_dir, "cryptanium_security_report.json")
    JSONReportGenerator().save_json_file(payload, trust_result, summary, recommendations, json_path)
    print(f"      JSON Report saved to: {json_path}")

    # 5. Generate PDF Report
    print("[5/5] Generating PDF Report...")
    pdf_path = os.path.join(output_dir, "cryptanium_security_report.pdf")
    PDFReportGenerator().generate_pdf(payload, trust_result, summary, recommendations, pdf_path)
    print(f"      PDF Report saved to: {pdf_path}")

    return {
        "trust_score": trust_result.final_score,
        "risk_level": trust_result.risk_level,
        "json_report": json_path,
        "pdf_report": pdf_path,
    }


if __name__ == "__main__":
    run_member4_pipeline(MOCK_INPUT_DATA)
