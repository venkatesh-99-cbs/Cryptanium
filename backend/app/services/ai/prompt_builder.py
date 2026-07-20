"""
Prompt builders for Cryptanium AI analysis.
Produces structured system + user prompts for:
  1. Security finding summary (executive overview)
  2. Prioritized recommendations
  3. Interactive chat with scan context
"""
from __future__ import annotations

from typing import Any


# ---------------------------------------------------------------------------
# System prompts
# ---------------------------------------------------------------------------

SUMMARY_SYSTEM = """You are Cryptanium AI — an expert application-security engineer embedded in an automated DevSecOps platform.

Your job is to produce an EXECUTIVE SUMMARY of a repository security scan for a technical lead or CISO.

Rules:
- Be precise, professional, and concise.
- Use plain English — no markdown headers, no bullet lists in the summary prose.
- Respond with a JSON object with exactly this structure:
  {
    "executive_summary": "<3-5 sentence prose summary>",
    "risk_level": "<Critical | High | Moderate | Low>",
    "key_concerns": ["<concern1>", "<concern2>", "<concern3>"]
  }
- Do NOT wrap the JSON in markdown fences.
- key_concerns must have between 2 and 5 items."""

RECOMMENDATIONS_SYSTEM = """You are Cryptanium AI — a principal security engineer providing actionable remediation guidance.

Rules:
- Respond with a JSON object with exactly this structure:
  {
    "recommendations": [
      {
        "priority": 1,
        "title": "<short title>",
        "finding_type": "<e.g. SQL Injection | Hardcoded Secret | Outdated Dependency>",
        "action": "<specific, actionable fix in 1-2 sentences>",
        "severity": "<Critical | High | Medium | Low>"
      }
    ]
  }
- Return at most 8 recommendations, ordered by priority (1 = most urgent).
- Do NOT wrap the JSON in markdown fences.
- Be specific and technical. Reference file types or patterns when relevant."""

CHAT_SYSTEM = """You are Cryptanium AI — an expert cybersecurity assistant integrated into the Cryptanium Repository Security Platform.

You help developers and security engineers understand their scan results, interpret vulnerabilities, and get remediation guidance.

Rules:
- Be helpful, concise, and technically accurate.
- If the user references a specific vulnerability, explain it clearly and give a concrete fix.
- When relevant, include a code example (use triple backtick fences with language tag).
- Do NOT invent findings that were not in the scan context.
- If no scan context is provided, answer general security questions helpfully.
- Respond in plain conversational text (NOT JSON)."""


# ---------------------------------------------------------------------------
# User prompt builders
# ---------------------------------------------------------------------------

def build_summary_prompt(findings: list[dict[str, Any]], repo_name: str) -> str:
    finding_lines: list[str] = []
    for i, f in enumerate(findings[:40], 1):  # cap at 40 to stay within token budget
        sev = f.get("severity", "Unknown")
        desc = f.get("description", "No description")
        tool = f.get("tool", "Unknown")
        path = f.get("file_path", "")
        finding_lines.append(f"  {i}. [{sev}] {desc} (tool: {tool}, file: {path})")

    findings_block = "\n".join(finding_lines) if finding_lines else "  No findings recorded."

    return f"""Repository: {repo_name}
Total findings: {len(findings)}

<findings>
{findings_block}
</findings>

Generate an executive summary for this repository scan."""


def build_recommendations_prompt(findings: list[dict[str, Any]], repo_name: str) -> str:
    # Deduplicate by (severity, rule_id)
    seen: set[str] = set()
    unique_findings: list[dict[str, Any]] = []
    for f in findings:
        key = f"{f.get('severity', '')}:{f.get('rule_id', f.get('description', ''))}"
        if key not in seen:
            seen.add(key)
            unique_findings.append(f)
        if len(unique_findings) >= 30:
            break

    finding_lines: list[str] = []
    for i, f in enumerate(unique_findings, 1):
        sev = f.get("severity", "Unknown")
        desc = f.get("description", "No description")
        rule = f.get("rule_id", "")
        tool = f.get("tool", "Unknown")
        path = f.get("file_path", "")
        finding_lines.append(
            f"  {i}. [{sev}] {desc} | rule: {rule} | tool: {tool} | file: {path}"
        )

    findings_block = "\n".join(finding_lines) if finding_lines else "  No findings."

    return f"""Repository: {repo_name}
Total unique findings: {len(unique_findings)}

<findings>
{findings_block}
</findings>

Generate prioritized security recommendations to address the above findings."""


def build_chat_prompt(
    user_message: str,
    scan_context: dict[str, Any] | None = None,
) -> str:
    if not scan_context:
        return user_message

    repo = scan_context.get("repository_name", "Unknown")
    trust_score = scan_context.get("trust_score", "N/A")
    total = scan_context.get("findings_count", 0)
    summary = scan_context.get("ai_summary", "")

    findings = scan_context.get("findings", [])[:10]
    finding_lines = []
    for f in findings:
        sev = f.get("severity", "?")
        desc = f.get("description", "")
        path = f.get("file_path", "")
        finding_lines.append(f"  - [{sev}] {desc} ({path})")
    findings_block = "\n".join(finding_lines) or "  No findings."

    context_block = f"""Scan context for repository: {repo}
Trust Score: {trust_score}/100
Total Findings: {total}
{f'AI Executive Summary: {summary}' if summary else ''}

Recent findings sample:
{findings_block}"""

    return f"""{context_block}

User question: {user_message}"""
