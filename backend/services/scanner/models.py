"""
Cryptanium Scanner Engine — Pydantic Models

Central model definitions shared by every component in the engine.
All scanner output is normalized into `Finding` instances so that
downstream consumers never need to know which tool produced a result.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class Severity(str, Enum):
    """Unified severity levels across all scanners."""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"
    UNKNOWN = "UNKNOWN"


class ScanStatus(str, Enum):
    """Overall status of a scan execution."""

    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"


# ---------------------------------------------------------------------------
# Detection models
# ---------------------------------------------------------------------------

class ProjectInfo(BaseModel):
    """Information about files / markers discovered in the repository."""

    has_requirements_txt: bool = False
    has_pyproject_toml: bool = False
    has_setup_py: bool = False
    has_package_json: bool = False
    has_package_lock_json: bool = False
    has_yarn_lock: bool = False
    has_pnpm_lock: bool = False
    has_dockerfile: bool = False
    has_docker_compose: bool = False
    has_github_workflows: bool = False
    marker_files: list[str] = Field(default_factory=list)


class LanguageInfo(BaseModel):
    """Detected languages and their relative weight."""

    primary_language: str = "unknown"
    secondary_languages: list[str] = Field(default_factory=list)
    file_counts: dict[str, int] = Field(default_factory=dict)
    total_files: int = 0


# ---------------------------------------------------------------------------
# Command result
# ---------------------------------------------------------------------------

class CommandResult(BaseModel):
    """Result of running a subprocess command."""

    command: str = ""
    return_code: int = -1
    stdout: str = ""
    stderr: str = ""
    timed_out: bool = False
    duration_seconds: float = 0.0


# ---------------------------------------------------------------------------
# Finding — the universal output schema
# ---------------------------------------------------------------------------

class Finding(BaseModel):
    """
    A single security finding.

    Every scanner normalizes its output into this schema so that
    downstream consumers (Trust Score, AI, Reports, Database)
    can work with a single contract.
    """

    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    tool: str = ""
    title: str = ""
    description: str = ""
    severity: Severity = Severity.UNKNOWN
    file: str = ""
    line: int = 0
    column: int = 0
    rule: str = ""
    category: str = ""
    recommendation: str = ""
    raw_output: dict[str, Any] | None = None


# ---------------------------------------------------------------------------
# Per-scanner result
# ---------------------------------------------------------------------------

class ScanResult(BaseModel):
    """Outcome of a single scanner execution."""

    tool: str = ""
    success: bool = False
    findings: list[Finding] = Field(default_factory=list)
    error: str | None = None
    duration_seconds: float = 0.0


# ---------------------------------------------------------------------------
# Full scan report
# ---------------------------------------------------------------------------

class ScanReport(BaseModel):
    """
    The final output returned by ``ScanOrchestrator.scan()``.

    Contains every finding, per-scanner metadata, detection info,
    and timing data.  This is what the Backend API hands off to
    downstream modules.
    """

    scan_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    repo_url: str = ""
    status: ScanStatus = ScanStatus.SUCCESS
    findings: list[Finding] = Field(default_factory=list)
    scan_results: list[ScanResult] = Field(default_factory=list)
    project_info: ProjectInfo = Field(default_factory=ProjectInfo)
    language_info: LanguageInfo = Field(default_factory=LanguageInfo)
    frameworks: list[str] = Field(default_factory=list)
    package_managers: list[str] = Field(default_factory=list)
    total_findings: int = 0
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    info_count: int = 0
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
    duration_seconds: float = 0.0
