from datetime import datetime
from pydantic import BaseModel, ConfigDict, model_validator


class ScanRequest(BaseModel):
    repository_id: str | int | None = None
    repository_name: str | None = None
    tools: list[str] | None = None

    @model_validator(mode="after")
    def validate_repository_identifier(self) -> "ScanRequest":
        repo_id_str = (
            str(self.repository_id).strip()
            if self.repository_id is not None
            else ""
        )
        repo_name_str = (
            self.repository_name.strip() if self.repository_name else ""
        )

        if not repo_id_str and not repo_name_str:
            raise ValueError(
                "Either 'repository_id' or 'repository_name' must be provided."
            )
        return self


class FindingItem(BaseModel):
    id: str
    rule_id: str
    severity: str
    description: str
    file_path: str
    line_number: int
    tool: str = ""


class ScanSummary(BaseModel):
    total_findings: int
    high_severity_count: int
    medium_severity_count: int
    low_severity_count: int


class ScanResponse(BaseModel):
    scan_id: int
    repository_id: str | int | None = None
    repository_name: str = ""
    status: str = "completed"
    trust_score: int = 0
    findings_count: int = 0
    summary: ScanSummary | None = None
    findings: list[FindingItem] = []
    ai_summary: str | None = None
    ai_recommendations: list[dict] = []
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class RecentScanItem(BaseModel):
    scan_id: int
    repository_id: str | int | None = None
    repository_name: str
    status: str
    trust_score: int = 85
    findings_count: int = 0
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class DashboardResponse(BaseModel):
    total_repositories: int
    total_scans: int
    average_trust_score: float
    total_vulnerabilities: int
    high_severity_count: int
    medium_severity_count: int
    low_severity_count: int
    recent_scans: list[RecentScanItem]
