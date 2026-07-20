"""
Tests for all four detectors: Project, Language, Framework, Package.

Each test creates a minimal mock file tree in a temp directory and
runs the detector against it.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from backend.services.detector.project_detector import ProjectDetector
from backend.services.detector.language_detector import LanguageDetector
from backend.services.detector.framework_detector import FrameworkDetector
from backend.services.detector.package_detector import PackageDetector
from backend.services.scanner.models import ProjectInfo


@pytest.fixture
def temp_repo(tmp_path: Path):
    """Provide a clean temp directory as a fake repo root."""
    return tmp_path


# ── ProjectDetector ──────────────────────────────────────────────────

class TestProjectDetector:
    def test_empty_repo(self, temp_repo: Path):
        detector = ProjectDetector()
        info = detector.detect(temp_repo)
        assert info.has_requirements_txt is False
        assert info.has_package_json is False
        assert info.marker_files == []

    def test_python_repo(self, temp_repo: Path):
        (temp_repo / "requirements.txt").write_text("flask==2.0\n")
        (temp_repo / "pyproject.toml").write_text("[project]\n")

        detector = ProjectDetector()
        info = detector.detect(temp_repo)
        assert info.has_requirements_txt is True
        assert info.has_pyproject_toml is True
        assert "requirements.txt" in info.marker_files
        assert "pyproject.toml" in info.marker_files

    def test_node_repo(self, temp_repo: Path):
        (temp_repo / "package.json").write_text('{"name": "test"}\n')
        (temp_repo / "package-lock.json").write_text("{}\n")

        detector = ProjectDetector()
        info = detector.detect(temp_repo)
        assert info.has_package_json is True
        assert info.has_package_lock_json is True

    def test_docker_repo(self, temp_repo: Path):
        (temp_repo / "Dockerfile").write_text("FROM python:3.12\n")
        (temp_repo / "docker-compose.yml").write_text("version: '3'\n")

        detector = ProjectDetector()
        info = detector.detect(temp_repo)
        assert info.has_dockerfile is True
        assert info.has_docker_compose is True

    def test_github_workflows(self, temp_repo: Path):
        workflows = temp_repo / ".github" / "workflows"
        workflows.mkdir(parents=True)
        (workflows / "ci.yml").write_text("name: CI\n")

        detector = ProjectDetector()
        info = detector.detect(temp_repo)
        assert info.has_github_workflows is True

    def test_mixed_repo(self, temp_repo: Path):
        (temp_repo / "requirements.txt").write_text("django\n")
        (temp_repo / "package.json").write_text('{"name": "frontend"}\n')
        (temp_repo / "Dockerfile").write_text("FROM node:18\n")

        detector = ProjectDetector()
        info = detector.detect(temp_repo)
        assert info.has_requirements_txt is True
        assert info.has_package_json is True
        assert info.has_dockerfile is True
        assert len(info.marker_files) == 3


# ── LanguageDetector ─────────────────────────────────────────────────

class TestLanguageDetector:
    def test_empty_repo(self, temp_repo: Path):
        detector = LanguageDetector()
        info = detector.detect(temp_repo)
        assert info.primary_language == "unknown"
        assert info.total_files == 0

    def test_python_repo(self, temp_repo: Path):
        for i in range(10):
            (temp_repo / f"module_{i}.py").write_text("pass\n")

        detector = LanguageDetector()
        info = detector.detect(temp_repo)
        assert info.primary_language == "python"
        assert info.file_counts["python"] == 10

    def test_node_repo(self, temp_repo: Path):
        for i in range(8):
            (temp_repo / f"component_{i}.js").write_text("// js\n")
        for i in range(5):
            (temp_repo / f"type_{i}.ts").write_text("// ts\n")

        detector = LanguageDetector()
        info = detector.detect(temp_repo)
        assert info.primary_language == "javascript"
        assert "typescript" in info.secondary_languages

    def test_mixed_repo(self, temp_repo: Path):
        for i in range(15):
            (temp_repo / f"app_{i}.py").write_text("pass\n")
        for i in range(5):
            (temp_repo / f"script_{i}.js").write_text("// js\n")

        detector = LanguageDetector()
        info = detector.detect(temp_repo)
        assert info.primary_language == "python"
        assert "javascript" in info.secondary_languages

    def test_skips_node_modules(self, temp_repo: Path):
        nm = temp_repo / "node_modules" / "pkg"
        nm.mkdir(parents=True)
        for i in range(100):
            (nm / f"file_{i}.js").write_text("// vendor\n")
        (temp_repo / "app.py").write_text("pass\n")

        detector = LanguageDetector()
        info = detector.detect(temp_repo)
        assert info.primary_language == "python"


# ── FrameworkDetector ────────────────────────────────────────────────

class TestFrameworkDetector:
    def test_flask(self, temp_repo: Path):
        (temp_repo / "requirements.txt").write_text("flask==2.3.0\nrequests\n")
        project_info = ProjectInfo(has_requirements_txt=True)

        detector = FrameworkDetector()
        frameworks = detector.detect(temp_repo, project_info)
        assert "Flask" in frameworks

    def test_react_nextjs(self, temp_repo: Path):
        pkg = {"dependencies": {"react": "^18.0.0", "next": "^14.0.0"}}
        (temp_repo / "package.json").write_text(json.dumps(pkg))
        project_info = ProjectInfo(has_package_json=True)

        detector = FrameworkDetector()
        frameworks = detector.detect(temp_repo, project_info)
        assert "React" in frameworks
        assert "Next.js" in frameworks

    def test_django(self, temp_repo: Path):
        (temp_repo / "requirements.txt").write_text("django>=4.0\n")
        project_info = ProjectInfo(has_requirements_txt=True)

        detector = FrameworkDetector()
        frameworks = detector.detect(temp_repo, project_info)
        assert "Django" in frameworks

    def test_no_frameworks(self, temp_repo: Path):
        (temp_repo / "requirements.txt").write_text("requests\nbeautifulsoup4\n")
        project_info = ProjectInfo(has_requirements_txt=True)

        detector = FrameworkDetector()
        frameworks = detector.detect(temp_repo, project_info)
        assert frameworks == []

    def test_fastapi(self, temp_repo: Path):
        (temp_repo / "requirements.txt").write_text("fastapi==0.100.0\nuvicorn\n")
        project_info = ProjectInfo(has_requirements_txt=True)

        detector = FrameworkDetector()
        frameworks = detector.detect(temp_repo, project_info)
        assert "FastAPI" in frameworks


# ── PackageDetector ──────────────────────────────────────────────────

class TestPackageDetector:
    def test_pip(self, temp_repo: Path):
        (temp_repo / "requirements.txt").write_text("flask\n")
        detector = PackageDetector()
        managers = detector.detect(temp_repo)
        assert "pip" in managers

    def test_npm(self, temp_repo: Path):
        (temp_repo / "package.json").write_text("{}\n")
        (temp_repo / "package-lock.json").write_text("{}\n")
        detector = PackageDetector()
        managers = detector.detect(temp_repo)
        assert "npm" in managers

    def test_yarn(self, temp_repo: Path):
        (temp_repo / "package.json").write_text("{}\n")
        (temp_repo / "yarn.lock").write_text("")
        detector = PackageDetector()
        managers = detector.detect(temp_repo)
        assert "yarn" in managers

    def test_pnpm(self, temp_repo: Path):
        (temp_repo / "package.json").write_text("{}\n")
        (temp_repo / "pnpm-lock.yaml").write_text("")
        detector = PackageDetector()
        managers = detector.detect(temp_repo)
        assert "pnpm" in managers

    def test_mixed(self, temp_repo: Path):
        (temp_repo / "requirements.txt").write_text("django\n")
        (temp_repo / "package.json").write_text("{}\n")
        (temp_repo / "package-lock.json").write_text("{}\n")
        detector = PackageDetector()
        managers = detector.detect(temp_repo)
        assert "pip" in managers
        assert "npm" in managers

    def test_from_project_info(self):
        info = ProjectInfo(
            has_requirements_txt=True,
            has_package_json=True,
            has_package_lock_json=True,
        )
        detector = PackageDetector()
        managers = detector.detect(Path("/fake"), project_info=info)
        assert "pip" in managers
        assert "npm" in managers
