"""
Cryptanium Scanner Engine — Async Command Runner

A reusable subprocess wrapper that every scanner delegates to.
Handles timeouts, exit codes, stdout/stderr capture, logging,
and structured result objects.
"""

from __future__ import annotations

import asyncio
import logging
import time
from pathlib import Path
from typing import Any

from backend.services.scanner.models import CommandResult

logger = logging.getLogger("cryptanium.command_runner")


class CommandRunner:
    """
    Execute external CLI tools asynchronously.

    Usage::

        runner = CommandRunner()
        result = await runner.run(["semgrep", "scan", "--json", "."], cwd=repo_path)
        if result.return_code == 0:
            process(result.stdout)
    """

    def __init__(self, default_timeout: int = 300) -> None:
        self._default_timeout = default_timeout

    async def run(
        self,
        cmd: list[str],
        cwd: Path | None = None,
        timeout: int | None = None,
        env: dict[str, str] | None = None,
    ) -> CommandResult:
        """
        Run *cmd* as an async subprocess and return a ``CommandResult``.

        Parameters
        ----------
        cmd:
            The command and arguments (e.g. ``["bandit", "-r", ".", "-f", "json"]``).
        cwd:
            Working directory for the process.
        timeout:
            Maximum seconds to wait.  Falls back to ``default_timeout``.
        env:
            Extra environment variables merged on top of the inherited env.
        """
        effective_timeout = timeout or self._default_timeout
        cmd_str = " ".join(cmd)
        logger.info("Running command: %s (cwd=%s, timeout=%ss)", cmd_str, cwd, effective_timeout)

        start = time.monotonic()
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(cwd) if cwd else None,
                env=self._build_env(env),
            )

            try:
                stdout_bytes, stderr_bytes = await asyncio.wait_for(
                    process.communicate(),
                    timeout=effective_timeout,
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                elapsed = time.monotonic() - start
                logger.warning("Command timed out after %.1fs: %s", elapsed, cmd_str)
                return CommandResult(
                    command=cmd_str,
                    return_code=-1,
                    stdout="",
                    stderr=f"Process timed out after {effective_timeout}s",
                    timed_out=True,
                    duration_seconds=round(elapsed, 3),
                )

            elapsed = time.monotonic() - start
            stdout = self._decode(stdout_bytes)
            stderr = self._decode(stderr_bytes)
            return_code = process.returncode or 0

            logger.info(
                "Command finished: %s (rc=%d, %.1fs)",
                cmd_str, return_code, elapsed,
            )
            if return_code != 0 and stderr:
                logger.debug("stderr: %s", stderr[:500])

            return CommandResult(
                command=cmd_str,
                return_code=return_code,
                stdout=stdout,
                stderr=stderr,
                timed_out=False,
                duration_seconds=round(elapsed, 3),
            )

        except FileNotFoundError:
            elapsed = time.monotonic() - start
            logger.error("Command not found: %s", cmd[0])
            return CommandResult(
                command=cmd_str,
                return_code=-1,
                stdout="",
                stderr=f"Command not found: {cmd[0]}",
                timed_out=False,
                duration_seconds=round(elapsed, 3),
            )
        except OSError as exc:
            elapsed = time.monotonic() - start
            logger.error("OS error running %s: %s", cmd_str, exc)
            return CommandResult(
                command=cmd_str,
                return_code=-1,
                stdout="",
                stderr=str(exc),
                timed_out=False,
                duration_seconds=round(elapsed, 3),
            )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_env(extra: dict[str, str] | None) -> dict[str, str] | None:
        """Merge *extra* into a copy of the current environment."""
        if not extra:
            return None  # inherit parent env
        import os
        merged = os.environ.copy()
        merged.update(extra)
        return merged

    @staticmethod
    def _decode(data: bytes | None) -> str:
        """Safely decode subprocess output."""
        if not data:
            return ""
        try:
            return data.decode("utf-8", errors="replace")
        except Exception:
            return ""
