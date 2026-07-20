"""
Cryptanium Scanner Engine — Workspace Manager

Creates isolated temporary directories for each scan.
Every scan gets a unique folder under the system temp directory;
workspaces are never reused.
"""

from __future__ import annotations

import logging
import shutil
import tempfile
import uuid
from pathlib import Path

from backend.services.scanner.exceptions import WorkspaceError

logger = logging.getLogger("cryptanium.workspace")


class WorkspaceManager:
    """
    Manages temporary workspaces for repository scanning.

    Each workspace lives at ``<tempdir>/cryptanium/<scan_id>/``.
    On Linux this is ``/tmp/cryptanium/<id>``, on Windows
    ``%TEMP%\\cryptanium\\<id>``.
    """

    BASE_DIR_NAME = "cryptanium"

    def __init__(self) -> None:
        self._base_dir = Path(tempfile.gettempdir()) / self.BASE_DIR_NAME

    @property
    def base_dir(self) -> Path:
        return self._base_dir

    def create(self, scan_id: str | None = None) -> Path:
        """
        Create and return a new workspace directory.

        Parameters
        ----------
        scan_id:
            Optional identifier.  If omitted, a UUID4 hex is generated.

        Returns
        -------
        Path
            The created workspace directory (guaranteed to exist).

        Raises
        ------
        WorkspaceError
            If the directory cannot be created.
        """
        scan_id = scan_id or uuid.uuid4().hex
        workspace = self._base_dir / scan_id

        try:
            workspace.mkdir(parents=True, exist_ok=False)
        except FileExistsError:
            # Extremely unlikely with UUIDs, but handle it.
            logger.warning("Workspace already exists, regenerating: %s", workspace)
            scan_id = uuid.uuid4().hex
            workspace = self._base_dir / scan_id
            workspace.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise WorkspaceError(f"Failed to create workspace {workspace}: {exc}") from exc

        logger.info("Workspace created: %s", workspace)
        return workspace

    def cleanup(self, workspace: Path, debug: bool = False) -> None:
        """
        Delete a workspace directory.

        Parameters
        ----------
        workspace:
            The directory to remove.
        debug:
            If ``True``, the workspace is kept for manual inspection
            and a log message is emitted instead.
        """
        if debug:
            logger.info("Debug mode — keeping workspace: %s", workspace)
            return

        if not workspace.exists():
            logger.debug("Workspace already removed: %s", workspace)
            return

        logger.info("Cleanup started: %s", workspace)
        try:
            # On Windows, git files may be read-only.
            shutil.rmtree(workspace, onerror=self._handle_remove_error)
            logger.info("Cleanup finished: %s", workspace)
        except Exception as exc:
            logger.error("Cleanup failed for %s: %s", workspace, exc)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _handle_remove_error(func, path, exc_info) -> None:
        """
        Error handler for ``shutil.rmtree``.

        On Windows, ``.git`` objects are often read-only.  This handler
        makes them writable and retries the removal.
        """
        import os
        import stat

        try:
            os.chmod(path, stat.S_IWRITE)
            func(path)
        except Exception:
            logger.debug("Could not remove %s after chmod", path)
