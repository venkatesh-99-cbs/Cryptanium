"""
Tests for OutputParser and per-scanner parsing logic.

Each test uses realistic JSON output matching real CLI tool formats.
"""

from __future__ import annotations

import json

import pytest

from backend.services.scanner.parser import OutputParser
from backend.services.scanner.utils import strip_ansi, normalize_severity, validate_repo_url


# ── OutputParser ─────────────────────────────────────────────────────

class TestOutputParser:
    def test_parse_valid_json_object(self):
        result = OutputParser.safe_parse_json('{"key": "value"}')
        assert result == {"key": "value"}

    def test_parse_valid_json_array(self):
        result = OutputParser.safe_parse_json('[1, 2, 3]')
        assert result == [1, 2, 3]

    def test_parse_empty_string(self):
        assert OutputParser.safe_parse_json("") is None
        assert OutputParser.safe_parse_json("   ") is None

    def test_parse_with_preamble(self):
        raw = "Running scan...\nProgress: 100%\n{\"results\": []}"
        result = OutputParser.safe_parse_json(raw)
        assert result == {"results": []}

    def test_parse_with_ansi_codes(self):
        raw = '\x1b[32m{"status": "ok"}\x1b[0m'
        result = OutputParser.safe_parse_json(raw)
        assert result == {"status": "ok"}

    def test_parse_with_bom(self):
        raw = '\ufeff{"data": true}'
        result = OutputParser.safe_parse_json(raw)
        assert result == {"data": True}

    def test_parse_ndjson(self):
        raw = '{"a": 1}\n{"b": 2}\n{"c": 3}\n'
        result = OutputParser.safe_parse_json(raw)
        assert isinstance(result, list)
        assert len(result) == 3

    def test_parse_malformed_json(self):
        assert OutputParser.safe_parse_json("not json at all") is None

    def test_parse_semgrep_output(self):
        semgrep_output = json.dumps({
            "results": [
                {
                    "check_id": "python.lang.security.audit.dangerous-eval",
                    "path": "app.py",
                    "start": {"line": 10, "col": 5},
                    "extra": {
                        "severity": "ERROR",
                        "message": "Dangerous use of eval",
                        "metadata": {"category": "security"},
                    },
                }
            ],
            "errors": [],
        })
        result = OutputParser.safe_parse_json(semgrep_output)
        assert isinstance(result, dict)
        assert len(result["results"]) == 1

    def test_parse_bandit_output(self):
        bandit_output = json.dumps({
            "results": [
                {
                    "test_id": "B101",
                    "test_name": "assert_used",
                    "filename": "tests/test.py",
                    "line_number": 5,
                    "issue_severity": "LOW",
                    "issue_confidence": "HIGH",
                    "issue_text": "Use of assert detected.",
                }
            ]
        })
        result = OutputParser.safe_parse_json(bandit_output)
        assert isinstance(result, dict)
        assert result["results"][0]["test_id"] == "B101"

    def test_parse_gitleaks_output(self):
        gitleaks_output = json.dumps([
            {
                "RuleID": "generic-api-key",
                "Description": "Generic API Key",
                "File": "config.py",
                "StartLine": 15,
                "Entropy": 4.5,
            }
        ])
        result = OutputParser.safe_parse_json(gitleaks_output)
        assert isinstance(result, list)
        assert result[0]["RuleID"] == "generic-api-key"

    def test_parse_npm_audit_output(self):
        npm_output = json.dumps({
            "vulnerabilities": {
                "lodash": {
                    "severity": "high",
                    "via": [{"title": "Prototype Pollution"}],
                    "fixAvailable": True,
                }
            }
        })
        result = OutputParser.safe_parse_json(npm_output)
        assert isinstance(result, dict)
        assert "lodash" in result["vulnerabilities"]


# ── strip_ansi ───────────────────────────────────────────────────────

class TestStripAnsi:
    def test_no_ansi(self):
        assert strip_ansi("hello world") == "hello world"

    def test_with_colors(self):
        assert strip_ansi("\x1b[31mERROR\x1b[0m") == "ERROR"

    def test_empty(self):
        assert strip_ansi("") == ""


# ── normalize_severity ───────────────────────────────────────────────

class TestNormalizeSeverity:
    def test_standard_values(self):
        assert normalize_severity("CRITICAL") == "CRITICAL"
        assert normalize_severity("HIGH") == "HIGH"
        assert normalize_severity("MEDIUM") == "MEDIUM"
        assert normalize_severity("LOW") == "LOW"

    def test_semgrep_values(self):
        assert normalize_severity("ERROR") == "HIGH"
        assert normalize_severity("WARNING") == "MEDIUM"
        assert normalize_severity("INFO") == "INFO"

    def test_npm_values(self):
        assert normalize_severity("critical") == "CRITICAL"
        assert normalize_severity("moderate") == "MEDIUM"

    def test_empty(self):
        assert normalize_severity("") == "UNKNOWN"

    def test_unknown_value(self):
        assert normalize_severity("banana") == "UNKNOWN"


# ── validate_repo_url ────────────────────────────────────────────────

class TestValidateRepoUrl:
    def test_valid_https(self):
        assert validate_repo_url("https://github.com/user/repo") is True
        assert validate_repo_url("https://gitlab.com/user/repo.git") is True

    def test_valid_ssh(self):
        assert validate_repo_url("git@github.com:user/repo.git") is True

    def test_invalid(self):
        assert validate_repo_url("") is False
        assert validate_repo_url("not-a-url") is False
        assert validate_repo_url("ftp://example.com") is False

    def test_none(self):
        assert validate_repo_url(None) is False
