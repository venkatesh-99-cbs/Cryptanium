"""
Cryptanium AI Service.
Orchestrates OpenRouter calls for:
  1. Scan analysis (summary + recommendations)
  2. Interactive chat assistant
Falls back gracefully when no API key is configured.
"""
from __future__ import annotations

import json
import logging
from typing import Any

from app.services.ai.openrouter_client import OpenRouterClient
from app.services.ai.prompt_builder import (
    CHAT_SYSTEM,
    RECOMMENDATIONS_SYSTEM,
    SUMMARY_SYSTEM,
    build_chat_prompt,
    build_recommendations_prompt,
    build_summary_prompt,
)

logger = logging.getLogger("cryptanium.ai.service")


class AIService:
    """High-level AI analysis service used by the scan pipeline and chat API."""

    def __init__(self) -> None:
        self._client = OpenRouterClient()

    # ------------------------------------------------------------------
    # Scan analysis
    # ------------------------------------------------------------------

    def generate_summary(
        self,
        findings: list[dict[str, Any]],
        repo_name: str,
    ) -> dict[str, Any]:
        """
        Generate an executive summary for a scan.

        Returns a dict with keys:
            executive_summary, risk_level, key_concerns
        Falls back to a placeholder if the API key is missing.
        """
        try:
            user_prompt = build_summary_prompt(findings, repo_name)
            raw = self._client.complete(
                system_prompt=SUMMARY_SYSTEM,
                user_prompt=user_prompt,
                temperature=0.25,
                max_tokens=1024,
            )
            result = json.loads(raw)
            # Normalise
            return {
                "executive_summary": result.get("executive_summary", ""),
                "risk_level": result.get("risk_level", "Unknown"),
                "key_concerns": result.get("key_concerns", []),
            }
        except RuntimeError as exc:
            # No API key — return informative placeholder
            logger.warning("AI summary skipped (no API key): %s", exc)
            return _placeholder_summary(findings, repo_name)
        except (json.JSONDecodeError, KeyError) as exc:
            logger.error("AI summary parse error: %s", exc)
            return _placeholder_summary(findings, repo_name)
        except Exception as exc:
            logger.error("AI summary failed: %s", exc)
            return _placeholder_summary(findings, repo_name)

    def generate_recommendations(
        self,
        findings: list[dict[str, Any]],
        repo_name: str,
    ) -> list[dict[str, Any]]:
        """
        Generate prioritised remediation recommendations.

        Returns a list of recommendation dicts.
        """
        if not findings:
            return []

        try:
            user_prompt = build_recommendations_prompt(findings, repo_name)
            raw = self._client.complete(
                system_prompt=RECOMMENDATIONS_SYSTEM,
                user_prompt=user_prompt,
                temperature=0.2,
                max_tokens=2048,
            )
            result = json.loads(raw)
            return result.get("recommendations", [])
        except RuntimeError as exc:
            logger.warning("AI recommendations skipped (no API key): %s", exc)
            return _placeholder_recommendations(findings)
        except (json.JSONDecodeError, KeyError) as exc:
            logger.error("AI recommendations parse error: %s", exc)
            return _placeholder_recommendations(findings)
        except Exception as exc:
            logger.error("AI recommendations failed: %s", exc)
            return _placeholder_recommendations(findings)

    # ------------------------------------------------------------------
    # Chat
    # ------------------------------------------------------------------

    def chat(
        self,
        user_message: str,
        scan_context: dict[str, Any] | None = None,
    ) -> str:
        """
        Answer a user question with optional scan context.
        Returns the AI response string.
        """
        try:
            user_prompt = build_chat_prompt(user_message, scan_context)
            return self._client.complete(
                system_prompt=CHAT_SYSTEM,
                user_prompt=user_prompt,
                temperature=0.5,
                max_tokens=1500,
            )
        except RuntimeError as exc:
            # No API key configured
            logger.warning("AI chat using local fallback: %s", exc)
            return _placeholder_chat(user_message, scan_context)
            return (
                "⚠️ **AI features are not configured.** "
                "To enable real AI responses, add your `OPENROUTER_API_KEY` to the `.env` file. "
                "You can get a free key at https://openrouter.ai — the `nvidia/nemotron-4-340b-instruct` model is used."
            )
        except Exception as exc:
            logger.error("AI chat error: %s", exc)
            return _placeholder_chat(user_message, scan_context)
            return (
                "I encountered an error while processing your request. "
                "Please try again in a moment, or check the server logs for details."
            )


# ------------------------------------------------------------------
# Fallback helpers (used when no API key is set)
# ------------------------------------------------------------------

def _count_by_severity(findings: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    for f in findings:
        sev = f.get("severity", "Low")
        counts[sev] = counts.get(sev, 0) + 1
    return counts


def _placeholder_summary(
    findings: list[dict[str, Any]], repo_name: str
) -> dict[str, Any]:
    counts = _count_by_severity(findings)
    total = len(findings)
    risk = (
        "Critical" if counts["Critical"] > 0
        else "High" if counts["High"] > 0
        else "Moderate" if counts["Medium"] > 0
        else "Low"
    )
    return {
        "executive_summary": (
            f"The repository '{repo_name}' was scanned and {total} security finding(s) were identified. "
            f"Of these, {counts['Critical']} are critical, {counts['High']} high, "
            f"{counts['Medium']} medium, and {counts['Low']} low severity. "
            "Configure OPENROUTER_API_KEY for a detailed AI-generated analysis."
        ),
        "risk_level": risk,
        "key_concerns": [
            f"{counts['Critical']} critical severity findings require immediate attention",
            f"{counts['High']} high severity findings should be addressed promptly",
        ],
    }


def _placeholder_recommendations(
    findings: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    seen_rules: set[str] = set()
    recs: list[dict[str, Any]] = []
    priority = 1

    severity_order = ["Critical", "High", "Medium", "Low"]
    sorted_findings = sorted(
        findings,
        key=lambda f: severity_order.index(f.get("severity", "Low"))
        if f.get("severity", "Low") in severity_order
        else 99,
    )

    for f in sorted_findings[:8]:
        rule = f.get("rule_id") or f.get("description", "unknown")
        if rule in seen_rules:
            continue
        seen_rules.add(rule)
        recs.append(
            {
                "priority": priority,
                "title": f.get("description", "Security Issue")[:80],
                "finding_type": rule,
                "action": (
                    f"Review and remediate the {f.get('severity', 'Unknown').lower()} severity "
                    f"finding in {f.get('file_path', 'the codebase')}. "
                    "Configure OPENROUTER_API_KEY for detailed AI guidance."
                ),
                "severity": f.get("severity", "Unknown"),
            }
        )
        priority += 1

    return recs


def _placeholder_chat(
    user_message: str, scan_context: dict[str, Any] | None,
) -> str:
    """Provide useful scan-grounded guidance when an LLM provider is unavailable."""
    if not scan_context:
        return (
            "The AI provider is not configured. Configure OPENROUTER_API_KEY to enable model responses, "
            "or select a completed scan to receive deterministic scan guidance."
        )

    findings = scan_context.get("findings", [])
    counts = _count_by_severity(findings)
    repo = scan_context.get("repository_name", "this repository")
    priority = next(
        (finding for finding in findings if finding.get("severity") in {"Critical", "High"}),
        findings[0] if findings else None,
    )
    response = (
        f"For {repo}, the selected scan recorded {len(findings)} finding(s): "
        f"{counts['Critical']} critical, {counts['High']} high, {counts['Medium']} medium, and {counts['Low']} low. "
    )
    if priority:
        response += (
            f"Start with the {priority.get('severity', 'highest')} severity issue "
            f"\"{priority.get('description') or priority.get('rule_id') or 'security finding'}\" "
            f"in {priority.get('file_path') or 'the affected code'}. "
        )
    else:
        response += "No individual findings were persisted for this scan. "
    return response + f"Local scan guidance for your question: {user_message.strip()}"
