from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ReportBase(BaseModel):
    scan_id: int
    report_type: str = "pdf"
    report_path: str | None = None


class ReportCreate(ReportBase):
    pass


class ReportResponse(ReportBase):
    id: int
    generated_at: datetime | None = None
    download_url: str | None = None

    model_config = ConfigDict(from_attributes=True)
