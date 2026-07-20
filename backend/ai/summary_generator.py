"""
AI Summary Generator Module for Cryptanium Member 4.
Summarizes repository scan findings into executive insights without hallucinating findings.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from backend.utils.parser import ScanPayload
from backend.trust.trust_engine import TrustScoreResult
from backend.ai.prompts import (
    SYSTEM_SUMMARY_PROMPT,
    build_summary_user_prompt,
)
from backend.ai.client import OpenRouterClient

logger = logging.getLogger(__name__)


class AISummaryGenerator:
    """LLM wrapper with offline fallback for executive security summarization."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("OPENROUTER_MODEL", "nvidia/nemotron-4-340b-instruct")
        self.client = OpenRouterClient(
            api_keys=[self.api_key] if self.api_key else None,
            default_model=self.model,
        ) if self.api_key else None

    def generate_summary(self, payload: ScanPayload, trust_result: TrustScoreResult) -> Dict[str, str]:
        """
        Generates executive summary containing:
        - repository_overview
        - security_posture
        - most_severe_findings
        - deployment_readiness
        """
        findings = payload.findings
        formatted_findings = self._format_findings_for_prompt(findings)

        if self.client and self.client.api_keys:
            try:
                return self._call_llm_summary(payload, trust_result, formatted_findings)
            except Exception as e:
                logger.warning(f"LLM API call failed: {e}. Falling back to rule-based summary.")
                return self._generate_fallback_summary(payload, trust_result)
        else:
            return self._generate_fallback_summary(payload, trust_result)

    def _format_findings_for_prompt(self, findings) -> str:
        if not findings:
            return "No vulnerabilities detected."
        lines = []
        # Limit findings to top 30 to prevent token overflow on huge repos
        for idx, f in enumerate(findings[:30], 1):
            line = f"{idx}. [{f.severity}] {f.tool} - {f.file}:{f.line or 'N/A'} - {f.description} (OWASP: {f.owasp or 'N/A'})"
            lines.append(line)
        if len(findings) > 30:
            lines.append(f"... and {len(findings) - 30} additional findings truncated for length.")
        return "\n".join(lines)

    def _call_llm_summary(self, payload: ScanPayload, trust_result: TrustScoreResult, formatted_findings: str) -> Dict[str, str]:
        """Calls OpenRouter API to produce summary."""
        user_prompt = build_summary_user_prompt(
            repository=payload.repository,
            branch=payload.branch,
            language=payload.language,
            score=trust_result.final_score,
            risk_level=trust_result.risk_level,
            findings_summary=formatted_findings,
        )

        parsed = self.client.chat_completion(
            system_prompt=SYSTEM_SUMMARY_PROMPT,
            user_prompt=user_prompt,
            temperature=0.2,
            json_mode=True,
        )
        return {
            "repository_overview": parsed.get("repository_overview", ""),
            "security_posture": parsed.get("security_posture", ""),
            "most_severe_findings": parsed.get("most_severe_findings", ""),
            "deployment_readiness": parsed.get("deployment_readiness", ""),
        }

    def _generate_fallback_summary(self, payload: ScanPayload, trust_result: TrustScoreResult) -> Dict[str, str]:
        """Deterministic, zero-hallucination fallback summarizer when offline or no API key is provided."""
        findings = payload.findings
        total = len(findings)
        critical_count = sum(1 for f in findings if f.severity == "Critical")
        high_count = sum(1 for f in findings if f.severity == "High")
        med_count = sum(1 for f in findings if f.severity == "Medium")

        # 1. Repository Overview
        repo_overview = (
            f"Repository '{payload.repository}' on branch '{payload.branch}' is written primarily in {payload.language}. "
            f"Automated security scans analyzed code artifacts and identified a total of {total} findings."
        )

        # 2. Security Posture
        sec_posture = (
            f"The repository achieved a Trust Score of {trust_result.final_score}/100, placing it in the '{trust_result.risk_level}' risk tier. "
            f"Scoring deductions reflect base severity findings and safety rules."
        )

        # 3. Most Severe Findings
        if critical_count > 0 or high_count > 0:
            top_findings = [f for f in findings if f.severity in ("Critical", "High")][:3]
            top_desc = "; ".join([f"[{f.severity}] {f.description} ({f.file})" for f in top_findings])
            most_severe = f"The audit detected {critical_count} Critical and {high_count} High severity vulnerabilities. Notable issues: {top_desc}."
        elif total > 0:
            most_severe = f"No Critical or High issues detected. Primary concerns involve {med_count} Medium severity finding(s)."
        else:
            most_severe = "No security vulnerabilities were detected during scanning."

        # 4. Deployment Readiness
        if trust_result.risk_level in ("Critical", "Risky") or critical_count > 0:
            readiness = "NOT READY FOR DEPLOYMENT. Critical or high-severity vulnerabilities must be remediated prior to staging or production releases."
        elif trust_result.risk_level == "Moderate" or high_count > 0:
            readiness = "CONDITIONAL DEPLOYMENT. High and medium issues should be resolved or risk-accepted prior to production deployment."
        else:
            readiness = "READY FOR DEPLOYMENT. Security posture meets standard deployment thresholds."

        return {
            "repository_overview": repo_overview,
            "security_posture": sec_posture,
            "most_severe_findings": most_severe,
            "deployment_readiness": readiness,
        }
