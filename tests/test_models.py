"""
Tests for Pydantic models.

Validates serialization, defaults, severity enum, and the full
ScanReport contract.
"""

from __future__ import annotations

import json

import pytest

from backend.services.scanner.models import (
    CommandResult,
    Finding,
    LanguageInfo,
    ProjectInfo,
    ScanReport,
    ScanResult,
    ScanStatus,
    Severity,
)


# ── Finding ──────────────────────────────────────────────────────────

class TestFinding:
    def test_defaults(self):
        f = Finding()
        assert f.id  # auto-generated
        assert f.tool == ""
        assert f.severity == Severity.UNKNOWN
        assert f.line == 0
        assert f.column == 0
        assert f.raw_output is None

    def test_custom_values(self):
        f = Finding(
            id="abc123",
            tool="semgrep",
            title="SQL Injection",
            severity=Severity.CRITICAL,
            file="app.py",
            line=42,
            rule="sql-injection",
        )
        assert f.id == "abc123"
        assert f.tool == "semgrep"
        assert f.severity == Severity.CRITICAL
        assert f.file == "app.py"
        assert f.line == 42

    def test_json_round_trip(self):
        f = Finding(
            tool="bandit",
            title="Hardcoded Password",
            severity=Severity.HIGH,
            file="config.py",
            line=10,
        )
        data = json.loads(f.model_dump_json())
        restored = Finding(**data)
        assert restored.tool == f.tool
        assert restored.severity == f.severity


# ── Severity ─────────────────────────────────────────────────────────

class TestSeverity:
    def test_all_values(self):
        expected = {"CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO", "UNKNOWN"}
        assert {s.value for s in Severity} == expected

    def test_string_comparison(self):
        assert Severity.CRITICAL == "CRITICAL"
        assert Severity.HIGH != "MEDIUM"


# ── ProjectInfo ──────────────────────────────────────────────────────

class TestProjectInfo:
    def test_defaults(self):
        p = ProjectInfo()
        assert p.has_requirements_txt is False
        assert p.has_package_json is False
        assert p.marker_files == []

    def test_populated(self):
        p = ProjectInfo(
            has_requirements_txt=True,
            has_dockerfile=True,
            marker_files=["requirements.txt", "Dockerfile"],
        )
        assert p.has_requirements_txt is True
        assert len(p.marker_files) == 2


# ── LanguageInfo ─────────────────────────────────────────────────────

class TestLanguageInfo:
    def test_defaults(self):
        li = LanguageInfo()
        assert li.primary_language == "unknown"
        assert li.secondary_languages == []
        assert li.total_files == 0

    def test_python_repo(self):
        li = LanguageInfo(
            primary_language="python",
            secondary_languages=["javascript"],
            file_counts={"python": 50, "javascript": 10},
            total_files=60,
        )
        assert li.primary_language == "python"
        assert "javascript" in li.secondary_languages


# ── CommandResult ────────────────────────────────────────────────────

class TestCommandResult:
    def test_defaults(self):
        cr = CommandResult()
        assert cr.return_code == -1
        assert cr.timed_out is False

    def test_successful(self):
        cr = CommandResult(
            command="git clone",
            return_code=0,
            stdout="Cloning...",
            stderr="",
            duration_seconds=1.5,
        )
        assert cr.return_code == 0


# ── ScanResult ───────────────────────────────────────────────────────

class TestScanResult:
    def test_successful_result(self):
        findings = [Finding(tool="test", title="Issue")]
        sr = ScanResult(tool="test", success=True, findings=findings, duration_seconds=2.0)
        assert sr.success is True
        assert len(sr.findings) == 1

    def test_failed_result(self):
        sr = ScanResult(tool="test", success=False, error="Timeout")
        assert sr.success is False
        assert sr.error == "Timeout"


# ── ScanReport ───────────────────────────────────────────────────────

class TestScanReport:
    def test_defaults(self):
        report = ScanReport()
        assert report.scan_id  # auto-generated UUID
        assert report.status == ScanStatus.SUCCESS
        assert report.findings == []
        assert report.total_findings == 0

    def test_full_report(self):
        findings = [
            Finding(tool="semgrep", severity=Severity.HIGH),
            Finding(tool="bandit", severity=Severity.MEDIUM),
        ]
        report = ScanReport(
            repo_url="https://github.com/test/repo",
            status=ScanStatus.PARTIAL,
            findings=findings,
            total_findings=2,
            high_count=1,
            medium_count=1,
        )
        assert report.total_findings == 2
        assert report.high_count == 1

    def test_json_serialization(self):
        report = ScanReport(repo_url="https://github.com/test/repo")
        data = json.loads(report.model_dump_json())
        assert "scan_id" in data
        assert data["repo_url"] == "https://github.com/test/repo"
