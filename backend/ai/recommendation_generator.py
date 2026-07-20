"""
AI Recommendation Engine Module for Cryptanium Member 4.
Generates prioritized remediation steps sorted by severity.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from backend.utils.parser import ScanPayload, FindingItem
from backend.ai.prompts import (
    SYSTEM_RECOMMENDATION_PROMPT,
    build_recommendation_user_prompt,
)

logger = logging.getLogger(__name__)

SEVERITY_PRIORITY_ORDER = {
    "Critical": 1,
    "High": 2,
    "Medium": 3,
    "Low": 4,
    "Info": 5,
}


class RecommendationItem:
    """Standardized remediation recommendation structure."""
    def __init__(self, priority: str, issue: str, recommended_fix: str, reason: str, severity: str = "Info"):
        self.priority = priority
        self.issue = issue
        self.recommended_fix = recommended_fix
        self.reason = reason
        self.severity = severity

    def to_dict(self) -> Dict[str, Any]:
        return {
            "priority": self.priority,
            "issue": self.issue,
            "recommended_fix": self.recommended_fix,
            "reason": self.reason,
            "severity": self.severity,
        }


class AIRecommendationEngine:
    """Generates prioritized remediation recommendations."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY") or os.getenv("OPENROUTER_API_KEY")
        self.model = model

    def generate_recommendations(self, payload: ScanPayload) -> List[Dict[str, Any]]:
        """
        Generates prioritized remediation recommendations sorted by severity.
        Returns a list of dictionaries with priority, issue, recommended_fix, reason.
        """
        findings = payload.findings
        if not findings:
            return [{
                "priority": "Low",
                "issue": "Continuous Monitoring",
                "recommended_fix": "Maintain automated static analysis in CI/CD pipeline.",
                "reason": "Repository has zero current findings. Ensure regression checks remain active.",
                "severity": "Info",
            }]

        # Sort findings by severity priority first
        sorted_findings = sorted(
            findings,
            key=lambda f: SEVERITY_PRIORITY_ORDER.get(f.severity, 99)
        )

        if self.api_key:
            try:
                rec_list = self._call_llm_recommendations(sorted_findings)
                if rec_list:
                    return rec_list
            except Exception as e:
                logger.warning(f"LLM recommendation call failed: {e}. Using deterministic engine.")

        return self._generate_rule_recommendations(sorted_findings)

    def _generate_rule_recommendations(self, sorted_findings: List[FindingItem]) -> List[Dict[str, Any]]:
        """Generates structured recommendations deterministically from finding data."""
        recommendations = []

        for f in sorted_findings:
            sev = f.severity
            priority = "Urgent" if sev == "Critical" else (sev if sev in ("High", "Medium", "Low") else "Low")

            issue = f"{f.description} ({f.file}:{f.line})" if f.line else f"{f.description} ({f.file})"

            if f.recommendation:
                rec_fix = f.recommendation
            elif f.is_secret:
                rec_fix = "Revoke exposed API key/secret immediately, clean git history, and use environment variables."
            elif f.is_dependency:
                rec_fix = f"Upgrade package to a non-vulnerable version or apply security patch for {f.cve or 'CVE'}."
            elif f.owasp == "A03":
                rec_fix = "Use parameterized queries, ORM models, or input sanitization libraries."
            else:
                rec_fix = f"Review code in {f.file} and apply defensive coding best practices to resolve {f.tool} alert."

            reason = (
                f"Fixing this {sev} severity issue addresses potential security risk tagged under {f.owasp or 'general security'}."
            )

            recommendations.append(
                RecommendationItem(
                    priority=priority,
                    issue=issue,
                    recommended_fix=rec_fix,
                    reason=reason,
                    severity=sev,
                ).to_dict()
            )

        return recommendations

    def _call_llm_recommendations(self, sorted_findings: List[FindingItem]) -> List[Dict[str, Any]]:
        import urllib.request

        findings_summary = "\n".join([
            f"- [{f.severity}] {f.description} in {f.file}:{f.line or 'N/A'}. Tool: {f.tool}. OWASP: {f.owasp or 'N/A'}. Suggestion: {f.recommendation or 'N/A'}"
            for f in sorted_findings
        ])

        user_prompt = build_recommendation_user_prompt(findings_summary)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        req_body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_RECOMMENDATION_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
        }

        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=json.dumps(req_body).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            resp_data = json.loads(response.read().decode("utf-8"))
            content_str = resp_data["choices"][0]["message"]["content"]
            parsed = json.loads(content_str)
            if isinstance(parsed, list):
                return parsed
            elif isinstance(parsed, dict) and "recommendations" in parsed:
                return parsed["recommendations"]
        return []
