"""
Cryptanium Scanner Engine — Output Parser

Utility class for safely parsing JSON output from CLI tools.
Handles malformed JSON, ANSI escape codes, BOM markers, and
other real-world quirks of scanner output.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from backend.services.scanner.utils import strip_ansi

logger = logging.getLogger("cryptanium.parser")


class OutputParser:
    """
    Safe JSON parser for scanner CLI output.

    Scanners often emit non-JSON preambles (progress bars, warnings)
    before the actual payload.  This parser attempts several strategies
    to extract valid JSON from noisy output.
    """

    @staticmethod
    def safe_parse_json(raw: str) -> dict[str, Any] | list[Any] | None:
        """
        Try to parse *raw* as JSON, applying progressively aggressive
        cleanup strategies.

        Returns the parsed object on success, or ``None`` on failure.
        """
        if not raw or not raw.strip():
            logger.debug("Empty output — nothing to parse")
            return None

        # Step 1: strip ANSI codes and BOM
        cleaned = strip_ansi(raw)
        cleaned = cleaned.lstrip("\ufeff")

        # Step 2: try direct parse
        result = OutputParser._try_parse(cleaned)
        if result is not None:
            return result

        # Step 3: find the first '{' or '[' and try from there
        result = OutputParser._try_parse_from_json_start(cleaned)
        if result is not None:
            return result

        # Step 4: try line-by-line (NDJSON / JSON Lines)
        result = OutputParser._try_parse_ndjson(cleaned)
        if result is not None:
            return result

        logger.warning("Failed to parse JSON output (length=%d)", len(raw))
        return None

    @staticmethod
    def _try_parse(text: str) -> dict[str, Any] | list[Any] | None:
        try:
            return json.loads(text)
        except (json.JSONDecodeError, ValueError):
            return None

    @staticmethod
    def _try_parse_from_json_start(text: str) -> dict[str, Any] | list[Any] | None:
        """Find the first JSON object / array boundary and parse."""
        for i, ch in enumerate(text):
            if ch in ("{", "["):
                result = OutputParser._try_parse(text[i:])
                if result is not None:
                    return result
                # Try to find matching closing bracket
                bracket = "}" if ch == "{" else "]"
                last = text.rfind(bracket)
                if last > i:
                    result = OutputParser._try_parse(text[i: last + 1])
                    if result is not None:
                        return result
                break  # only attempt once from the first opening bracket
        return None

    @staticmethod
    def _try_parse_ndjson(text: str) -> list[dict[str, Any]] | None:
        """Parse newline-delimited JSON (one JSON object per line)."""
        lines = text.strip().splitlines()
        if len(lines) < 2:
            return None

        objects: list[dict[str, Any]] = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            parsed = OutputParser._try_parse(line)
            if isinstance(parsed, dict):
                objects.append(parsed)

        return objects if objects else None
