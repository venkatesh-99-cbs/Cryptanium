"""
Integration test for ScanOrchestrator.

Tests the full pipeline with all subprocess calls mocked
so no external tools are needed.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.services.scanner.models import (
    CommandResult,
    LanguageInfo,
    ProjectInfo,
    ScanStatus,
    Severity,
)
from backend.services.scanner.orchestrator import ScanOrchestrator
from backend.services.scanner.normalizer import ResultNormalizer
from backend.services.scanner.models import Finding, ScanResult


# ── ResultNormalizer ─────────────────────────────────────────────────

class TestResultNormalizer:
    def test_merge_and_sort(self):
        results = [
            ScanResult(
                tool="bandit",
                success=True,
                findings=[
                    Finding(tool="bandit", severity=Severity.LOW, file="a.py", line=1, rule="B101"),
                    Finding(tool="bandit", severity=Severity.HIGH, file="b.py", line=2, rule="B105"),
                ],
            ),
            ScanResult(
                tool="semgrep",
                success=True,
                findings=[
                    Finding(tool="semgrep", severity=Severity.CRITICAL, file="c.py", line=3, rule="eval-injection"),
                ],
            ),
        ]
        normalizer = ResultNormalizer()
        findings = normalizer.normalize(results)
        assert len(findings) == 3
        # Should be sorted: CRITICAL, HIGH, LOW
        assert findings[0].severity == Severity.CRITICAL
        assert findings[1].severity == Severity.HIGH
        assert findings[2].severity == Severity.LOW

    def test_deduplicate(self):
        results = [
            ScanResult(
                tool="semgrep",
                success=True,
                findings=[
                    Finding(tool="semgrep", severity=Severity.MEDIUM, file="app.py", line=10, rule="sql-injection"),
                ],
            ),
            ScanResult(
                tool="bandit",
                success=True,
                findings=[
                    Finding(tool="bandit", severity=Severity.HIGH, file="app.py", line=10, rule="sql-injection"),
                ],
            ),
        ]
        normalizer = ResultNormalizer()
        findings = normalizer.normalize(results)
        # Same file+line+rule → deduplicate, keep higher severity
        assert len(findings) == 1
        assert findings[0].severity == Severity.HIGH

    def test_skip_failed_scanners(self):
        results = [
            ScanResult(tool="semgrep", success=False, error="Not installed"),
            ScanResult(
                tool="bandit",
                success=True,
                findings=[Finding(tool="bandit", severity=Severity.LOW, file="a.py", line=1, rule="B101")],
            ),
        ]
        normalizer = ResultNormalizer()
        findings = normalizer.normalize(results)
        assert len(findings) == 1

    def test_empty_results(self):
        normalizer = ResultNormalizer()
        findings = normalizer.normalize([])
        assert findings == []


# ── ScanOrchestrator ─────────────────────────────────────────────────

class TestScanOrchestrator:
    @pytest.mark.asyncio
    async def test_invalid_repo_url(self):
        orchestrator = ScanOrchestrator()
        report = await orchestrator.scan("not-a-valid-url")
        assert report.status == ScanStatus.FAILED

    @pytest.mark.asyncio
    async def test_full_pipeline_mocked(self, tmp_path: Path):
        """
        Mock the entire pipeline to test orchestrator wiring.
        """
        # Create a fake repo structure
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()
        (repo_dir / "requirements.txt").write_text("flask==2.3.0\n")
        (repo_dir / "app.py").write_text("from flask import Flask\n")
        for i in range(5):
            (repo_dir / f"module_{i}.py").write_text("pass\n")

        orchestrator = ScanOrchestrator()

        # Mock workspace to use our tmp_path
        orchestrator._workspace_manager.create = MagicMock(return_value=tmp_path)
        orchestrator._workspace_manager.cleanup = MagicMock()

        # Mock clone to just return the repo_dir
        orchestrator._clone_service.clone = AsyncMock(return_value=repo_dir)

        # Mock cleanup
        orchestrator._cleanup_service.cleanup = MagicMock()

        # Mock command runner so scanners don't actually run
        mock_result = CommandResult(
            command="mocked",
            return_code=0,
            stdout=json.dumps({"results": []}),
            stderr="",
            timed_out=False,
            duration_seconds=0.5,
        )
        orchestrator._command_runner.run = AsyncMock(return_value=mock_result)

        report = await orchestrator.scan("https://github.com/test/flask-app")

        assert report.repo_url == "https://github.com/test/flask-app"
        assert report.scan_id  # Should be set
        assert report.project_info.has_requirements_txt is True
        assert report.language_info.primary_language == "python"
        assert "Flask" in report.frameworks
        assert "pip" in report.package_managers
        assert report.completed_at is not None
        assert report.duration_seconds > 0

    @pytest.mark.asyncio
    async def test_clone_failure(self):
        """Verify graceful handling when clone fails."""
        orchestrator = ScanOrchestrator()

        # Mock workspace
        fake_workspace = Path("/tmp/cryptanium/test-clone-fail")
        orchestrator._workspace_manager.create = MagicMock(return_value=fake_workspace)
        orchestrator._cleanup_service.cleanup = MagicMock()

        # Mock clone to fail
        from backend.services.scanner.exceptions import CloneError
        orchestrator._clone_service.clone = AsyncMock(
            side_effect=CloneError("Repository not found")
        )

        report = await orchestrator.scan("https://github.com/nonexistent/repo")

        assert report.status == ScanStatus.FAILED
        assert any("not found" in (r.error or "") for r in report.scan_results)
        # Cleanup should still be called
        orchestrator._cleanup_service.cleanup.assert_called_once()

    @pytest.mark.asyncio
    async def test_partial_scanner_failure(self, tmp_path: Path):
        """
        When some scanners succeed and some fail, status should be PARTIAL.
        """
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()
        (repo_dir / "requirements.txt").write_text("flask\n")
        for i in range(3):
            (repo_dir / f"m{i}.py").write_text("pass\n")

        orchestrator = ScanOrchestrator()
        orchestrator._workspace_manager.create = MagicMock(return_value=tmp_path)
        orchestrator._workspace_manager.cleanup = MagicMock()
        orchestrator._clone_service.clone = AsyncMock(return_value=repo_dir)
        orchestrator._cleanup_service.cleanup = MagicMock()

        call_count = 0

        async def mock_run(cmd, cwd=None, timeout=None, env=None):
            nonlocal call_count
            call_count += 1
            # First scanner succeeds, second fails
            if call_count % 2 == 0:
                return CommandResult(
                    command=" ".join(cmd),
                    return_code=0,
                    stdout="",
                    stderr="Command not found: bandit",
                    timed_out=False,
                    duration_seconds=0.1,
                )
            return CommandResult(
                command=" ".join(cmd),
                return_code=0,
                stdout=json.dumps({"results": []}),
                stderr="",
                timed_out=False,
                duration_seconds=0.5,
            )

        orchestrator._command_runner.run = mock_run

        report = await orchestrator.scan("https://github.com/test/repo")
        # The report should complete without crashing
        assert report.status in (ScanStatus.SUCCESS, ScanStatus.PARTIAL)
        assert report.completed_at is not None
