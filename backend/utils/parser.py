"""
Input Parser & Model Validation Module for Cryptanium Member 4.
Parses, sanitizes, and validates normalized scanner findings input.
"""

from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, field_validator, model_validator


class FindingItem(BaseModel):
    """Normalized finding item representation."""
    severity: str = Field(..., description="Finding severity (Critical, High, Medium, Low, Info)")
    tool: str = Field(default="Unknown Tool", description="Scanner tool name (e.g. Bandit, Gitleaks, Trivy)")
    file: str = Field(default="Unknown File", description="Target file path")
    line: Optional[int] = Field(default=None, description="Line number if applicable")
    description: str = Field(default="No description provided", description="Vulnerability description")
    recommendation: Optional[str] = Field(default=None, description="Suggested fix recommendation")
    owasp: Optional[str] = Field(default=None, description="OWASP Top 10 category (e.g. A03, A01)")
    cve: Optional[str] = Field(default=None, description="CVE Identifier if available")
    is_secret: bool = Field(default=False, description="Whether this finding is an exposed secret")
    is_dependency: bool = Field(default=False, description="Whether this finding is a vulnerable dependency")

    @field_validator("severity", mode="before")
    @classmethod
    def normalize_severity(cls, value: Any) -> str:
        if not value or not isinstance(value, str):
            return "Info"
        val = value.strip().capitalize()
        valid = {"Critical", "High", "Medium", "Low", "Info"}
        if val in valid:
            return val
        # Handle uppercase / lowercase variants
        upper = value.strip().upper()
        if upper == "CRITICAL":
            return "Critical"
        if upper == "HIGH":
            return "High"
        if upper == "MEDIUM":
            return "Medium"
        if upper == "LOW":
            return "Low"
        return "Info"

    @model_validator(mode="after")
    def auto_detect_flags(self) -> "FindingItem":
        tool_lower = (self.tool or "").lower()
        desc_lower = (self.description or "").lower()
        owasp_upper = (self.owasp or "").upper()

        if not self.is_secret:
            if "gitleaks" in tool_lower or "secret" in desc_lower or "password" in desc_lower or "key" in desc_lower or owasp_upper == "A07":
                self.is_secret = True

        if not self.is_dependency:
            if "trivy" in tool_lower or "safety" in tool_lower or "dependency" in tool_lower or "cve" in desc_lower or owasp_upper == "A06":
                self.is_dependency = True

        return self


class ScanPayload(BaseModel):
    """Normalized payload delivered after scanning."""
    repository: str = Field(default="Unknown Repository", description="Repository name or URI")
    branch: str = Field(default="main", description="Branch name scanned")
    language: str = Field(default="Generic", description="Primary repository language")
    scan_date: Optional[str] = Field(default=None, description="ISO timestamp of scan execution")
    findings: List[FindingItem] = Field(default_factory=list, description="List of detected findings")

    @classmethod
    def parse_payload(cls, raw_data: Any) -> "ScanPayload":
        """Parses a dictionary or JSON string into a validated ScanPayload."""
        if isinstance(raw_data, str):
            return cls.model_validate_json(raw_data)
        elif isinstance(raw_data, dict):
            return cls.model_validate(raw_data)
        else:
            raise ValueError(f"Unsupported payload type: {type(raw_data)}")

    @classmethod
    def from_scan_report(cls, scan_report: Any, repository: str = "", branch: str = "main") -> "ScanPayload":
        """Converts a Scanner Engine ScanReport object into a ScanPayload."""
        findings_items = []
        report_findings = getattr(scan_report, "findings", []) or []
        for f in report_findings:
            tool_name = getattr(f, "tool", "Scanner") or "Scanner"
            sev_raw = getattr(f, "severity", "Info")
            sev_str = str(sev_raw.value if hasattr(sev_raw, "value") else sev_raw).capitalize()
            desc = getattr(f, "description", None) or getattr(f, "title", "Vulnerability detected")
            rec = getattr(f, "recommendation", None)
            category = getattr(f, "category", None) or getattr(f, "rule", None)
            
            findings_items.append(
                FindingItem(
                    severity=sev_str,
                    tool=tool_name,
                    file=getattr(f, "file", "N/A"),
                    line=getattr(f, "line", None),
                    description=desc,
                    recommendation=rec,
                    owasp=category if (category and category.startswith("A")) else None,
                    cve=category if (category and "CVE" in category.upper()) else None,
                    is_secret="secret" in tool_name.lower() or "gitleaks" in tool_name.lower(),
                    is_dependency="audit" in tool_name.lower() or "trivy" in tool_name.lower(),
                )
            )

        lang = "Generic"
        if hasattr(scan_report, "language_info") and scan_report.language_info:
            lang = getattr(scan_report.language_info, "primary_language", "Generic") or "Generic"

        repo_name = repository or getattr(scan_report, "repo_url", "Unknown Repository")

        return cls(
            repository=repo_name,
            branch=branch,
            language=lang,
            scan_date=getattr(scan_report, "completed_at", None) and str(getattr(scan_report, "completed_at")),
            findings=findings_items,
        )
