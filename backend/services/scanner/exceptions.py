"""
Cryptanium Scanner Engine — Custom Exceptions

Defines a hierarchy of domain-specific exceptions so the engine
never raises raw Python exceptions to callers.  Every exception
carries a human-readable message and, optionally, the original
cause for chained tracebacks.
"""

from __future__ import annotations


class ScannerEngineError(Exception):
    """Base exception for all Scanner Engine errors."""

    def __init__(self, message: str = "Scanner engine encountered an error") -> None:
        self.message = message
        super().__init__(self.message)


class CloneError(ScannerEngineError):
    """Raised when git clone fails (network, auth, invalid URL, etc.)."""

    def __init__(self, message: str = "Failed to clone repository") -> None:
        super().__init__(message)


class InvalidRepositoryError(ScannerEngineError):
    """Raised when the provided repository URL is malformed or unreachable."""

    def __init__(self, message: str = "Invalid repository URL") -> None:
        super().__init__(message)


class ScannerNotInstalledError(ScannerEngineError):
    """Raised when a required CLI tool (e.g. semgrep, bandit) is not on PATH."""

    def __init__(self, scanner_name: str) -> None:
        self.scanner_name = scanner_name
        super().__init__(f"Scanner '{scanner_name}' is not installed or not found on PATH")


class ScannerTimeoutError(ScannerEngineError):
    """Raised when a scanner exceeds its allowed execution time."""

    def __init__(self, scanner_name: str, timeout_seconds: int) -> None:
        self.scanner_name = scanner_name
        self.timeout_seconds = timeout_seconds
        super().__init__(
            f"Scanner '{scanner_name}' timed out after {timeout_seconds}s"
        )


class ParseError(ScannerEngineError):
    """Raised when scanner output cannot be parsed (invalid JSON, etc.)."""

    def __init__(self, scanner_name: str, detail: str = "") -> None:
        self.scanner_name = scanner_name
        msg = f"Failed to parse output from '{scanner_name}'"
        if detail:
            msg += f": {detail}"
        super().__init__(msg)


class WorkspaceError(ScannerEngineError):
    """Raised for workspace creation / cleanup failures."""

    def __init__(self, message: str = "Workspace operation failed") -> None:
        super().__init__(message)
