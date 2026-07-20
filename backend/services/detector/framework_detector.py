"""
Cryptanium Scanner Engine — Framework Detector

Inspects manifest files and import patterns to determine which
web frameworks / libraries a repository uses.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from backend.services.scanner.models import ProjectInfo

logger = logging.getLogger("cryptanium.detector.framework")

# Python frameworks detected by import name or pyproject dependency
_PYTHON_FRAMEWORKS: dict[str, str] = {
    "flask": "Flask",
    "fastapi": "FastAPI",
    "django": "Django",
    "starlette": "Starlette",
    "tornado": "Tornado",
    "sanic": "Sanic",
    "pyramid": "Pyramid",
    "bottle": "Bottle",
    "aiohttp": "aiohttp",
}

# Node.js frameworks detected via package.json dependencies
_NODE_FRAMEWORKS: dict[str, str] = {
    "react": "React",
    "next": "Next.js",
    "vue": "Vue",
    "nuxt": "Nuxt.js",
    "angular": "Angular",
    "@angular/core": "Angular",
    "express": "Express",
    "fastify": "Fastify",
    "svelte": "Svelte",
    "gatsby": "Gatsby",
    "remix": "Remix",
    "nestjs": "NestJS",
    "@nestjs/core": "NestJS",
}


class FrameworkDetector:
    """
    Detect frameworks used in a repository.

    Checks ``requirements.txt``, ``pyproject.toml``, and
    ``package.json`` for known framework dependencies.
    """

    def detect(self, repo_path: Path, project_info: ProjectInfo) -> list[str]:
        """
        Return a deduplicated list of framework names found in
        *repo_path*.
        """
        logger.info("Framework detection started: %s", repo_path)
        frameworks: list[str] = []

        # Python
        if project_info.has_requirements_txt:
            frameworks.extend(self._scan_requirements_txt(repo_path / "requirements.txt"))

        if project_info.has_pyproject_toml:
            frameworks.extend(self._scan_pyproject_toml(repo_path / "pyproject.toml"))

        # Node
        if project_info.has_package_json:
            frameworks.extend(self._scan_package_json(repo_path / "package.json"))

        # Deduplicate while preserving order
        seen: set[str] = set()
        unique: list[str] = []
        for fw in frameworks:
            if fw not in seen:
                seen.add(fw)
                unique.append(fw)

        logger.info("Framework detection completed: %s", unique or "none")
        return unique

    # ------------------------------------------------------------------
    # Python
    # ------------------------------------------------------------------

    def _scan_requirements_txt(self, path: Path) -> list[str]:
        """Parse ``requirements.txt`` for known Python frameworks."""
        found: list[str] = []
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
            for line in content.splitlines():
                line = line.strip().lower()
                if not line or line.startswith("#") or line.startswith("-"):
                    continue
                # Strip version specifiers
                pkg = line.split("==")[0].split(">=")[0].split("<=")[0].split("~=")[0].split("[")[0].strip()
                if pkg in _PYTHON_FRAMEWORKS:
                    found.append(_PYTHON_FRAMEWORKS[pkg])
        except Exception as exc:
            logger.debug("Error reading requirements.txt: %s", exc)
        return found

    def _scan_pyproject_toml(self, path: Path) -> list[str]:
        """Parse ``pyproject.toml`` for known Python frameworks."""
        found: list[str] = []
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
            lower = content.lower()
            for pkg, name in _PYTHON_FRAMEWORKS.items():
                if pkg in lower:
                    found.append(name)
        except Exception as exc:
            logger.debug("Error reading pyproject.toml: %s", exc)
        return found

    # ------------------------------------------------------------------
    # Node
    # ------------------------------------------------------------------

    def _scan_package_json(self, path: Path) -> list[str]:
        """Parse ``package.json`` for known Node frameworks."""
        found: list[str] = []
        try:
            data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
            all_deps: dict[str, str] = {}
            all_deps.update(data.get("dependencies", {}))
            all_deps.update(data.get("devDependencies", {}))

            for pkg, name in _NODE_FRAMEWORKS.items():
                if pkg in all_deps:
                    found.append(name)
        except Exception as exc:
            logger.debug("Error reading package.json: %s", exc)
        return found
