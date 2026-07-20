"""
Cryptanium Scanner Engine — Language Detector

Walks the repository file tree, counts files by extension, and
determines the primary and secondary languages.
"""

from __future__ import annotations

import logging
from collections import Counter
from pathlib import Path

from backend.services.scanner.models import LanguageInfo

logger = logging.getLogger("cryptanium.detector.language")

# Directories to skip when counting files
_SKIP_DIRS: set[str] = {
    ".git", "node_modules", "__pycache__", ".venv", "venv",
    "env", ".env", "dist", "build", ".next", ".tox",
    ".mypy_cache", ".pytest_cache", "vendor", "coverage",
    ".idea", ".vscode",
}

# Extension → language mapping
_EXT_LANGUAGE: dict[str, str] = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".html": "html",
    ".css": "css",
    ".scss": "scss",
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".md": "markdown",
    ".go": "go",
    ".rs": "rust",
    ".java": "java",
    ".rb": "ruby",
    ".php": "php",
    ".c": "c",
    ".cpp": "cpp",
    ".cs": "csharp",
    ".sh": "shell",
    ".sql": "sql",
}

# Only these are considered "code" languages for primary/secondary ranking
_CODE_LANGUAGES: set[str] = {
    "python", "javascript", "typescript", "go", "rust",
    "java", "ruby", "php", "c", "cpp", "csharp",
}


class LanguageDetector:
    """
    Detect programming languages used in a repository by extension counting.

    The language with the most code files is the *primary* language;
    any other code language with ≥ 5 % share is a *secondary* language.
    """

    SECONDARY_THRESHOLD = 0.05  # 5 %

    def detect(self, repo_path: Path) -> LanguageInfo:
        """
        Scan *repo_path* and return a ``LanguageInfo`` with primary /
        secondary languages and per-language file counts.
        """
        logger.info("Language detection started: %s", repo_path)

        ext_counter: Counter[str] = Counter()
        total = 0

        for file in self._walk(repo_path):
            ext = file.suffix.lower()
            lang = _EXT_LANGUAGE.get(ext)
            if lang:
                ext_counter[lang] += 1
                total += 1

        if not ext_counter:
            logger.info("Language detection completed: no recognised files")
            return LanguageInfo(primary_language="unknown", total_files=0)

        # Filter to code languages only for ranking
        code_counts = {
            lang: count
            for lang, count in ext_counter.items()
            if lang in _CODE_LANGUAGES
        }

        if not code_counts:
            # Fallback: use the most common overall language
            primary = ext_counter.most_common(1)[0][0]
            return LanguageInfo(
                primary_language=primary,
                file_counts=dict(ext_counter),
                total_files=total,
            )

        sorted_langs = sorted(code_counts.items(), key=lambda x: x[1], reverse=True)
        primary = sorted_langs[0][0]
        total_code = sum(code_counts.values())

        secondary: list[str] = []
        for lang, count in sorted_langs[1:]:
            if count / total_code >= self.SECONDARY_THRESHOLD:
                secondary.append(lang)

        info = LanguageInfo(
            primary_language=primary,
            secondary_languages=secondary,
            file_counts=dict(ext_counter),
            total_files=total,
        )

        logger.info(
            "Language detection completed: primary=%s, secondary=%s, files=%d",
            primary, secondary, total,
        )
        return info

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _walk(root: Path):
        """Yield files under *root*, skipping vendor / build dirs."""
        try:
            for entry in root.iterdir():
                if entry.is_dir():
                    if entry.name in _SKIP_DIRS:
                        continue
                    yield from LanguageDetector._walk(entry)
                elif entry.is_file():
                    yield entry
        except PermissionError:
            logger.debug("Permission denied: %s", root)
