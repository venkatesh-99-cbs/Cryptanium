"""
Cryptanium Scanner Engine — Clone Service

Clones a Git repository into a workspace directory via ``git clone``.
Validates the URL, performs a shallow clone for speed, and provides
clear error messages on failure.
"""

from __future__ import annotations

import logging
from pathlib import Path

from backend.services.scanner.command_runner import CommandRunner
from backend.services.scanner.exceptions import CloneError, InvalidRepositoryError
from backend.services.scanner.utils import validate_repo_url

logger = logging.getLogger("cryptanium.clone")


class CloneService:
    """
    Clone Git repositories into temporary workspaces.

    Uses ``git clone --depth 1`` for shallow clones (faster, less disk).
    """

    def __init__(self, command_runner: CommandRunner | None = None) -> None:
        self._runner = command_runner or CommandRunner(default_timeout=120)

    async def clone(self, repo_url: str, workspace: Path) -> Path:
        """
        Clone *repo_url* into *workspace*.

        Parameters
        ----------
        repo_url:
            HTTPS or SSH Git URL.
        workspace:
            Target directory (must already exist).

        Returns
        -------
        Path
            The root of the cloned repository.

        Raises
        ------
        InvalidRepositoryError
            If the URL is malformed.
        CloneError
            If ``git clone`` fails.
        """
        if not validate_repo_url(repo_url):
            raise InvalidRepositoryError(f"Invalid repository URL: {repo_url}")

        logger.info("Clone started: %s → %s", repo_url, workspace)

        cmd = [
            "git", "clone",
            "--depth", "1",
            "--single-branch",
            repo_url,
            str(workspace / "repo"),
        ]

        result = await self._runner.run(cmd, cwd=workspace, timeout=120)

        if result.timed_out:
            raise CloneError(f"Clone timed out for {repo_url}")

        if result.return_code != 0:
            stderr = result.stderr.strip()
            # Provide meaningful error messages
            if "Authentication" in stderr or "403" in stderr or "401" in stderr:
                raise CloneError(f"Authentication failed for {repo_url}")
            if "not found" in stderr.lower() or "404" in stderr:
                raise CloneError(f"Repository not found: {repo_url}")
            if "Permission denied" in stderr:
                raise CloneError(f"Permission denied for {repo_url}")
            raise CloneError(f"Clone failed (rc={result.return_code}): {stderr[:300]}")

        cloned_path = workspace / "repo"
        if not cloned_path.exists():
            raise CloneError(f"Clone appeared to succeed but directory not found: {cloned_path}")

        logger.info("Clone completed: %s", cloned_path)
        return cloned_path
