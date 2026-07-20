"""
Cryptanium Scanner Engine — Project Detector

Scans a cloned repository for marker files that indicate project type,
CI configuration, and containerisation.
"""

from __future__ import annotations

import logging
from pathlib import Path

from backend.services.scanner.models import ProjectInfo

logger = logging.getLogger("cryptanium.detector.project")


class ProjectDetector:
    """
    Detect project markers (manifest files, CI configs, Docker files).

    The result feeds into ``ScannerFactory`` to decide which scanners
    should run against this repository.
    """

    # (relative path, ProjectInfo attribute)
    _MARKER_MAP: list[tuple[str, str]] = [
        ("requirements.txt", "has_requirements_txt"),
        ("pyproject.toml", "has_pyproject_toml"),
        ("setup.py", "has_setup_py"),
        ("package.json", "has_package_json"),
        ("package-lock.json", "has_package_lock_json"),
        ("yarn.lock", "has_yarn_lock"),
        ("pnpm-lock.yaml", "has_pnpm_lock"),
        ("Dockerfile", "has_dockerfile"),
        ("docker-compose.yml", "has_docker_compose"),
        ("docker-compose.yaml", "has_docker_compose"),
    ]

    def detect(self, repo_path: Path) -> ProjectInfo:
        """
        Walk *repo_path* and return a ``ProjectInfo`` populated with
        all detected marker files.
        """
        logger.info("Project detection started: %s", repo_path)

        info = ProjectInfo()
        found_markers: list[str] = []

        for relative, attr in self._MARKER_MAP:
            if (repo_path / relative).exists():
                setattr(info, attr, True)
                found_markers.append(relative)

        # GitHub Actions / workflows
        workflows_dir = repo_path / ".github" / "workflows"
        if workflows_dir.is_dir() and any(workflows_dir.iterdir()):
            info.has_github_workflows = True
            found_markers.append(".github/workflows")

        info.marker_files = found_markers
        logger.info(
            "Project detection completed: %d markers found (%s)",
            len(found_markers),
            ", ".join(found_markers) or "none",
        )
        return info
