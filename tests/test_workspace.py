"""
Tests for WorkspaceManager and CleanupService.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from backend.services.clone.workspace import WorkspaceManager
from backend.services.clone.cleanup import CleanupService


class TestWorkspaceManager:
    def test_create_workspace(self):
        wm = WorkspaceManager()
        workspace = wm.create()
        try:
            assert workspace.exists()
            assert workspace.is_dir()
            assert "cryptanium" in str(workspace)
        finally:
            wm.cleanup(workspace)

    def test_create_with_custom_id(self):
        wm = WorkspaceManager()
        workspace = wm.create(scan_id="test-scan-123")
        try:
            assert workspace.exists()
            assert "test-scan-123" in str(workspace)
        finally:
            wm.cleanup(workspace)

    def test_unique_workspaces(self):
        wm = WorkspaceManager()
        ws1 = wm.create()
        ws2 = wm.create()
        try:
            assert ws1 != ws2
            assert ws1.exists()
            assert ws2.exists()
        finally:
            wm.cleanup(ws1)
            wm.cleanup(ws2)

    def test_cleanup_removes_directory(self):
        wm = WorkspaceManager()
        workspace = wm.create()
        # Create a file inside
        (workspace / "test.txt").write_text("hello")
        assert workspace.exists()

        wm.cleanup(workspace)
        assert not workspace.exists()

    def test_cleanup_debug_keeps_workspace(self):
        wm = WorkspaceManager()
        workspace = wm.create()
        try:
            wm.cleanup(workspace, debug=True)
            assert workspace.exists()  # Should still be there
        finally:
            wm.cleanup(workspace)  # Actually clean up

    def test_cleanup_nonexistent_workspace(self):
        wm = WorkspaceManager()
        fake_path = Path(tempfile.gettempdir()) / "cryptanium" / "nonexistent-12345"
        # Should not raise
        wm.cleanup(fake_path)


class TestCleanupService:
    def test_cleanup_succeeds(self):
        wm = WorkspaceManager()
        workspace = wm.create()
        (workspace / "data.json").write_text("{}")

        cs = CleanupService(workspace_manager=wm)
        cs.cleanup(workspace)
        assert not workspace.exists()

    def test_cleanup_debug_mode(self):
        wm = WorkspaceManager()
        workspace = wm.create()
        try:
            cs = CleanupService(workspace_manager=wm)
            cs.cleanup(workspace, debug=True)
            assert workspace.exists()
        finally:
            wm.cleanup(workspace)

    def test_cleanup_nonexistent_never_raises(self):
        cs = CleanupService()
        fake = Path(tempfile.gettempdir()) / "cryptanium" / "does-not-exist-xyz"
        # Must not raise
        cs.cleanup(fake)
