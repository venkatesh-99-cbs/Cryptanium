"""
Tests for individual scanner implementations.

Every scanner is tested with mocked subprocess output to verify
parsing and normalization logic without requiring CLI tools to
be installed.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from backend.services.scanner.command_runner import CommandRunner
from backend.services.scanner.models import CommandResult, LanguageInfo, ProjectInfo, Severity
from backend.services.scanner.scanners.semgrep_scanner import SemgrepScanner
from backend.services.scanner.scanners.bandit_scanner import BanditScanner
from backend.services.scanner.scanners.gitleaks_scanner import GitleaksScanner
from backend.services.scanner.scanners.pip_audit_scanner import PipAuditScanner
from backend.services.scanner.scanners.npm_audit_scanner import NpmAuditScanner
from backend.services.scanner.scanners.eslint_scanner import ESLintScanner


REPO_PATH = Path("/tmp/cryptanium/test-scan/repo")


def _make_mock_runner(stdout: str, return_code: int = 0) -> CommandRunner:
    """Create a CommandRunner with mocked output."""
    runner = CommandRunner()
    runner.run = AsyncMock(return_value=CommandResult(
        command="mocked",
        return_code=return_code,
        stdout=stdout,
        stderr="",
        timed_out=False,
        duration_seconds=1.0,
    ))
    return runner


# ── SemgrepScanner ───────────────────────────────────────────────────

class TestSemgrepScanner:
    def test_is_supported_python(self):
        scanner = SemgrepScanner()
        info = ProjectInfo()
        lang = LanguageInfo(primary_language="python")
        assert scanner.is_supported(info, lang) is True

    def test_is_supported_go(self):
        scanner = SemgrepScanner()
        info = ProjectInfo()
        lang = LanguageInfo(primary_language="go")
        assert scanner.is_supported(info, lang) is False

    def test_parse_and_normalize(self):
        raw = json.dumps({
            "results": [
                {
                    "check_id": "python.lang.security.audit.eval-injection",
                    "path": "/tmp/cryptanium/test-scan/repo/app.py",
                    "start": {"line": 42, "col": 5},
                    "end": {"line": 42, "col": 30},
                    "extra": {
                        "severity": "ERROR",
                        "message": "Detected eval() usage",
                        "metadata": {"category": "security"},
                    },
                }
            ]
        })
        scanner = SemgrepScanner()
        parsed = scanner.parse(raw)
        assert len(parsed) == 1
        findings = scanner.normalize(parsed, REPO_PATH)
        assert len(findings) == 1
        assert findings[0].tool == "semgrep"
        assert findings[0].severity == Severity.HIGH
        assert findings[0].line == 42

    @pytest.mark.asyncio
    async def test_execute(self):
        raw = json.dumps({"results": [
            {
                "check_id": "test.rule",
                "path": "main.py",
                "start": {"line": 1, "col": 1},
                "extra": {"severity": "WARNING", "message": "Test", "metadata": {}},
            }
        ]})
        runner = _make_mock_runner(raw)
        scanner = SemgrepScanner(command_runner=runner)
        result = await scanner.execute(REPO_PATH)
        assert result.success is True
        assert len(result.findings) == 1


# ── BanditScanner ────────────────────────────────────────────────────

class TestBanditScanner:
    def test_is_supported(self):
        scanner = BanditScanner()
        lang = LanguageInfo(primary_language="python")
        assert scanner.is_supported(ProjectInfo(), lang) is True

        lang_js = LanguageInfo(primary_language="javascript")
        assert scanner.is_supported(ProjectInfo(), lang_js) is False

    def test_parse_and_normalize(self):
        raw = json.dumps({
            "results": [
                {
                    "test_id": "B105",
                    "test_name": "hardcoded_password_string",
                    "filename": "/tmp/cryptanium/test-scan/repo/config.py",
                    "line_number": 10,
                    "issue_severity": "HIGH",
                    "issue_confidence": "MEDIUM",
                    "issue_text": "Possible hardcoded password",
                }
            ]
        })
        scanner = BanditScanner()
        parsed = scanner.parse(raw)
        findings = scanner.normalize(parsed, REPO_PATH)
        assert len(findings) == 1
        assert findings[0].rule == "B105"
        assert findings[0].severity == Severity.HIGH


# ── GitleaksScanner ──────────────────────────────────────────────────

class TestGitleaksScanner:
    def test_is_supported_always(self):
        scanner = GitleaksScanner()
        # Gitleaks should always be supported
        assert scanner.is_supported(ProjectInfo(), LanguageInfo()) is True
        assert scanner.is_supported(
            ProjectInfo(), LanguageInfo(primary_language="python")
        ) is True

    def test_normalize(self):
        parsed = [
            {
                "RuleID": "aws-access-key",
                "Description": "AWS Access Key",
                "File": "/tmp/cryptanium/test-scan/repo/config.py",
                "StartLine": 5,
                "Entropy": 4.2,
            }
        ]
        scanner = GitleaksScanner()
        findings = scanner.normalize(parsed, REPO_PATH)
        assert len(findings) == 1
        assert findings[0].category == "secret"
        assert findings[0].severity == Severity.HIGH
        assert "aws-access-key" in findings[0].title


# ── PipAuditScanner ─────────────────────────────────────────────────

class TestPipAuditScanner:
    def test_is_supported(self):
        scanner = PipAuditScanner()
        assert scanner.is_supported(
            ProjectInfo(has_requirements_txt=True),
            LanguageInfo(primary_language="python"),
        ) is True
        assert scanner.is_supported(
            ProjectInfo(has_requirements_txt=False),
            LanguageInfo(primary_language="python"),
        ) is False

    def test_parse_and_normalize(self):
        raw = json.dumps({
            "dependencies": [
                {
                    "name": "requests",
                    "version": "2.25.0",
                    "vulns": [
                        {
                            "id": "PYSEC-2023-001",
                            "description": "SSRF vulnerability",
                            "fix_versions": ["2.31.0"],
                            "aliases": [],
                        }
                    ],
                },
                {
                    "name": "flask",
                    "version": "2.3.0",
                    "vulns": [],
                },
            ]
        })
        scanner = PipAuditScanner()
        parsed = scanner.parse(raw)
        assert len(parsed) == 1  # Only vulnerable packages
        findings = scanner.normalize(parsed, REPO_PATH)
        assert len(findings) == 1
        assert findings[0].category == "dependency"
        assert "requests" in findings[0].title
        assert "2.31.0" in findings[0].recommendation


# ── NpmAuditScanner ──────────────────────────────────────────────────

class TestNpmAuditScanner:
    def test_is_supported(self):
        scanner = NpmAuditScanner()
        assert scanner.is_supported(
            ProjectInfo(has_package_json=True, has_package_lock_json=True),
            LanguageInfo(primary_language="javascript"),
        ) is True
        assert scanner.is_supported(
            ProjectInfo(has_package_json=True, has_package_lock_json=False),
            LanguageInfo(primary_language="javascript"),
        ) is False

    def test_parse_v7_format(self):
        raw = json.dumps({
            "vulnerabilities": {
                "lodash": {
                    "severity": "high",
                    "via": [{"title": "Prototype Pollution"}],
                    "fixAvailable": True,
                },
                "express": {
                    "severity": "moderate",
                    "via": ["lodash"],
                    "fixAvailable": True,
                },
            }
        })
        scanner = NpmAuditScanner()
        parsed = scanner.parse(raw)
        assert len(parsed) == 2
        findings = scanner.normalize(parsed, REPO_PATH)
        assert len(findings) == 2
        assert all(f.category == "dependency" for f in findings)


# ── ESLintScanner ────────────────────────────────────────────────────

class TestESLintScanner:
    def test_is_supported(self):
        scanner = ESLintScanner()
        assert scanner.is_supported(
            ProjectInfo(has_package_json=True),
            LanguageInfo(primary_language="javascript"),
        ) is True
        assert scanner.is_supported(
            ProjectInfo(has_package_json=False),
            LanguageInfo(primary_language="javascript"),
        ) is False

    def test_parse_and_normalize(self):
        raw = json.dumps([
            {
                "filePath": "/tmp/cryptanium/test-scan/repo/index.js",
                "messages": [
                    {
                        "ruleId": "no-eval",
                        "severity": 2,
                        "message": "eval can be harmful",
                        "line": 15,
                        "column": 3,
                    },
                    {
                        "ruleId": "no-unused-vars",
                        "severity": 1,
                        "message": "'x' is defined but never used",
                        "line": 3,
                        "column": 7,
                    },
                ],
            }
        ])
        scanner = ESLintScanner()
        parsed = scanner.parse(raw)
        assert len(parsed) == 1  # 1 file result
        findings = scanner.normalize(parsed, REPO_PATH)
        assert len(findings) == 2
        assert findings[0].severity == Severity.HIGH  # severity 2
        assert findings[1].severity == Severity.MEDIUM  # severity 1
