"""
Cryptanium Scanner Engine — Cleanup Service

Thin wrapper around ``WorkspaceManager.cleanup()`` that adds
structured logging and graceful error handling.  Guarantees
that cleanup never raises, even on permission errors.
"""

from __future__ import annotations

import logging
from pathlib import Path

from backend.services.clone.workspace import WorkspaceManager

logger = logging.getLogger("cryptanium.cleanup")


class CleanupService:
    """
    Safely removes scan workspaces after a scan completes (or fails).

    Used in a ``finally`` block by the orchestrator so resources are
    always released regardless of scan outcome.
    """

    def __init__(self, workspace_manager: WorkspaceManager | None = None) -> None:
        self._wm = workspace_manager or WorkspaceManager()

    def cleanup(self, workspace: Path, debug: bool = False) -> None:
        """
        Remove *workspace* from disk.

        Parameters
        ----------
        workspace:
            The workspace directory created during the scan.
        debug:
            If ``True``, the directory is kept for post-mortem inspection.
        """
        try:
            logger.info("Cleanup started: %s (debug=%s)", workspace, debug)
            self._wm.cleanup(workspace, debug=debug)
            logger.info("Cleanup finished: %s", workspace)
        except Exception as exc:
            # Never propagate — cleanup failure must not mask scan results.
            logger.error("Cleanup error for %s: %s", workspace, exc)
