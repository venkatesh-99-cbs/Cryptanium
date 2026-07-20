"""
Cryptanium Scanner Engine — Package Manager Detector

Determines which package managers a repository uses based on
lock files and manifest files.
"""

from __future__ import annotations

import logging
from pathlib import Path

from backend.services.scanner.models import ProjectInfo

logger = logging.getLogger("cryptanium.detector.package")


class PackageDetector:
    """
    Detect package managers used in a repository.

    Returns a list of strings such as ``["pip", "npm"]``.
    """

    def detect(self, repo_path: Path, project_info: ProjectInfo | None = None) -> list[str]:
        """
        Return package manager names detected from *repo_path*.

        If *project_info* is provided, uses its cached flags.
        Otherwise, checks the filesystem directly.
        """
        logger.info("Package manager detection started: %s", repo_path)

        if project_info is None:
            managers = self._detect_from_fs(repo_path)
        else:
            managers = self._detect_from_info(project_info)

        logger.info("Package manager detection completed: %s", managers or "none")
        return managers

    # ------------------------------------------------------------------
    # Detection strategies
    # ------------------------------------------------------------------

    @staticmethod
    def _detect_from_info(info: ProjectInfo) -> list[str]:
        managers: list[str] = []

        # Python
        if info.has_requirements_txt or info.has_setup_py:
            managers.append("pip")
        if info.has_pyproject_toml:
            # Could be poetry or pip
            if "pip" not in managers:
                managers.append("pip")
            managers.append("poetry")

        # Node
        if info.has_pnpm_lock:
            managers.append("pnpm")
        elif info.has_yarn_lock:
            managers.append("yarn")
        elif info.has_package_lock_json or info.has_package_json:
            managers.append("npm")

        return managers

    @staticmethod
    def _detect_from_fs(repo_path: Path) -> list[str]:
        managers: list[str] = []

        # Python
        if (repo_path / "requirements.txt").exists() or (repo_path / "setup.py").exists():
            managers.append("pip")
        if (repo_path / "pyproject.toml").exists():
            if "pip" not in managers:
                managers.append("pip")
            managers.append("poetry")

        # Node
        if (repo_path / "pnpm-lock.yaml").exists():
            managers.append("pnpm")
        elif (repo_path / "yarn.lock").exists():
            managers.append("yarn")
        elif (repo_path / "package-lock.json").exists() or (repo_path / "package.json").exists():
            managers.append("npm")

        return managers
