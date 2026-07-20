"""
Comprehensive Unit & Integration Test Suite for Cryptanium Member 4.
Run with: python -m unittest backend/utils/test_member4.py
"""

import os
import json
import tempfile
import unittest

from backend.utils.parser import ScanPayload, FindingItem
from backend.utils.formatter import format_owasp_category, get_risk_color_hex
from backend.trust.severity import SeverityLevel
from backend.trust.scoring_rules import (
    SeverityDeductionRule,
    SecretExposurePenaltyRule,
    VulnerableDependencyPenaltyRule,
    FindingVolumePenaltyRule,
)
from backend.trust.trust_engine import TrustEngine
from backend.ai.summary_generator import AISummaryGenerator
from backend.ai.recommendation_generator import AIRecommendationEngine
from backend.reports.json_export import JSONReportGenerator
from backend.reports.pdf_generator import PDFReportGenerator


class TestMember4Modules(unittest.TestCase):

    def setUp(self):
        """Set up mock scan data."""
        self.mock_input_dict = {
            "repository": "cryptanium/auth-service",
            "branch": "feature/oauth",
            "language": "Python",
            "findings": [
                {
                    "severity": "Critical",
                    "tool": "Bandit",
                    "file": "app/auth.py",
                    "line": 52,
                    "description": "Use of hardcoded password / SQL injection pattern",
                    "recommendation": "Use parameterized queries and environment secrets.",
                    "owasp": "A03"
                },
                {
                    "severity": "High",
                    "tool": "Gitleaks",
                    "file": "config.py",
                    "line": 12,
                    "description": "AWS API key exposed in source code",
                    "recommendation": "Revoke key and store in Vault.",
                    "owasp": "A07"
                },
                {
                    "severity": "Medium",
                    "tool": "Trivy",
                    "file": "requirements.txt",
                    "line": 5,
                    "description": "Vulnerable PyYAML version with remote code execution CVE-2020-14343",
                    "recommendation": "Upgrade PyYAML to >= 5.4",
                    "owasp": "A06"
                },
                {
                    "severity": "Low",
                    "tool": "Flake8",
                    "file": "utils.py",
                    "line": 102,
                    "description": "Unused import statement",
                    "recommendation": "Remove unused import",
                    "owasp": "A05"
                }
            ]
        }
        self.payload = ScanPayload.parse_payload(self.mock_input_dict)

    def test_parser_and_models(self):
        """Test payload parsing, normalization, and auto-flagging."""
        self.assertEqual(self.payload.repository, "cryptanium/auth-service")
        self.assertEqual(len(self.payload.findings), 4)

        # Check secret detection
        gitleaks_finding = self.payload.findings[1]
        self.assertTrue(gitleaks_finding.is_secret)

        # Check dependency detection
        trivy_finding = self.payload.findings[2]
        self.assertTrue(trivy_finding.is_dependency)

    def test_trust_engine_scoring(self):
        """Test Trust Engine score deduction math and risk mapping."""
        engine = TrustEngine()
        result = engine.calculate_score(self.payload)

        # Deductions:
        # Critical (25) + High (15) + Medium (8) + Low (3) = 51.0 base severity
        # Secret penalty (15.0 x 2 = 30.0) for 2 secrets ("password" and "AWS API key")
        # Vulnerable dependency penalty (10.0) for 1 dep ("Trivy")
        # Total deduction = 51 + 30 + 10 = 91.0
        # Score = 100 - 91.0 = 9.0 (Risk Level: Critical)
        self.assertEqual(result.final_score, 9.0)
        self.assertEqual(result.risk_level, "Critical")

    def test_trust_engine_boundaries(self):
        """Test score clamping between 0 and 100."""
        # 1. Zero findings -> Score 100 (Excellent)
        clean_payload = ScanPayload.parse_payload({"repository": "clean-repo", "findings": []})
        engine = TrustEngine()
        clean_res = engine.calculate_score(clean_payload)
        self.assertEqual(clean_res.final_score, 100.0)
        self.assertEqual(clean_res.risk_level, "Excellent")

        # 2. Extreme findings -> Score 0 (Critical)
        extreme_findings = [{"severity": "Critical", "description": f"Bug {i}"} for i in range(10)]
        extreme_payload = ScanPayload.parse_payload({"repository": "bad-repo", "findings": extreme_findings})
        extreme_res = engine.calculate_score(extreme_payload)
        self.assertEqual(extreme_res.final_score, 0.0)
        self.assertEqual(extreme_res.risk_level, "Critical")

    def test_ai_summary_generator_fallback(self):
        """Test AI Summary Generator fallback behavior without API key."""
        engine = TrustEngine()
        trust_result = engine.calculate_score(self.payload)

        generator = AISummaryGenerator(api_key=None)
        summary = generator.generate_summary(self.payload, trust_result)

        self.assertIn("repository_overview", summary)
        self.assertIn("security_posture", summary)
        self.assertIn("most_severe_findings", summary)
        self.assertIn("deployment_readiness", summary)
        self.assertIn("NOT READY FOR DEPLOYMENT", summary["deployment_readiness"])

    def test_ai_recommendation_engine(self):
        """Test AI Recommendation Engine sorting and item attributes."""
        engine = AIRecommendationEngine(api_key=None)
        recs = engine.generate_recommendations(self.payload)

        self.assertEqual(len(recs), 4)
        # Verify Critical / Urgent is first
        self.assertIn(recs[0]["priority"], ["Urgent", "Critical"])
        self.assertIn("issue", recs[0])
        self.assertIn("recommended_fix", recs[0])
        self.assertIn("reason", recs[0])

    def test_json_export_generator(self):
        """Test JSON Report Generator output serialization."""
        engine = TrustEngine()
        trust_res = engine.calculate_score(self.payload)
        summary = AISummaryGenerator().generate_summary(self.payload, trust_res)
        recs = AIRecommendationEngine().generate_recommendations(self.payload)

        json_gen = JSONReportGenerator()
        json_str = json_gen.generate_json_string(self.payload, trust_res, summary, recs)

        data = json.loads(json_str)
        self.assertEqual(data["repository"], "cryptanium/auth-service")
        self.assertEqual(data["trust_score"], 9.0)
        self.assertEqual(data["risk_level"], "Critical")
        self.assertIn("summary", data)
        self.assertIn("recommendations", data)
        self.assertEqual(len(data["findings"]), 4)

    def test_pdf_report_generator(self):
        """Test PDF Report Generator file output generation."""
        engine = TrustEngine()
        trust_res = engine.calculate_score(self.payload)
        summary = AISummaryGenerator().generate_summary(self.payload, trust_res)
        recs = AIRecommendationEngine().generate_recommendations(self.payload)

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
            pdf_path = tmp_file.name

        try:
            pdf_gen = PDFReportGenerator()
            out_path = pdf_gen.generate_pdf(self.payload, trust_res, summary, recs, pdf_path)
            self.assertTrue(os.path.exists(out_path))
            self.assertGreater(os.path.getsize(out_path), 1000)
        finally:
            if os.path.exists(pdf_path):
                os.remove(pdf_path)


if __name__ == "__main__":
    unittest.main()
