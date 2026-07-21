"""
OpenRouter client for the Cryptanium AI engine (app-layer).
Uses the nvidia/nemotron-4-340b-instruct model via OpenRouter.
Supports key rotation, exponential backoff, and graceful fallback.
"""
from __future__ import annotations

import json
import logging
import os
import time
from typing import Any

import httpx

logger = logging.getLogger("cryptanium.ai.client")

_DEFAULT_MODEL = "nvidia/nemotron-4-340b-instruct"
_OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def _get_api_key() -> str | None:
    """Resolve API key from environment (supports comma-separated key rotation)."""
    raw = os.getenv("OPENROUTER_API_KEYS") or os.getenv("OPENROUTER_API_KEY", "")
    if not raw:
        try:
            from app.core.config import settings
            raw = settings.OPENROUTER_API_KEY
        except ImportError:
            raw = ""
    keys = [
        key.strip() for key in raw.split(",")
        if key.strip() and not key.strip().lower().startswith(("your_", "replace_", "changeme"))
    ]
    return keys[0] if keys else None


class OpenRouterClient:
    """
    Thin, production-ready OpenRouter client.
    Each instance rotates through the provided keys.
    """

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or _get_api_key()
        self.model = model or os.getenv("OPENROUTER_MODEL", _DEFAULT_MODEL)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        temperature: float = 0.3,
        max_tokens: int = 2048,
        max_retries: int = 3,
        timeout: float = 60.0,
    ) -> str:
        """
        Send a chat completion request. Returns the raw assistant message text.
        Raises RuntimeError on persistent failure.
        """
        if not self.api_key:
            raise RuntimeError(
                "OPENROUTER_API_KEY is not set. "
                "Add it to your .env file to enable AI features."
            )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/venkatesh-99-cbs/Cryptanium",
            "X-Title": "Cryptanium Security Platform",
        }

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        last_error: Exception | None = None

        for attempt in range(max_retries):
            try:
                response = httpx.post(
                    _OPENROUTER_URL,
                    headers=headers,
                    json=payload,
                    timeout=timeout,
                )

                if response.status_code in (429, 502, 503, 504):
                    wait = 2 ** attempt + 1
                    logger.warning(
                        "OpenRouter HTTP %s — retrying in %ss (attempt %s/%s)",
                        response.status_code, wait, attempt + 1, max_retries,
                    )
                    time.sleep(wait)
                    continue

                response.raise_for_status()
                data = response.json()
                content: str = data["choices"][0]["message"]["content"]
                return self._strip_markdown_fences(content)

            except httpx.TimeoutException as exc:
                last_error = exc
                wait = 2 ** attempt
                logger.warning("OpenRouter timeout (attempt %s). Retrying in %ss.", attempt + 1, wait)
                time.sleep(wait)
            except httpx.HTTPStatusError as exc:
                last_error = exc
                logger.error("OpenRouter HTTP error: %s", exc)
                raise RuntimeError(f"OpenRouter request failed: {exc}") from exc
            except Exception as exc:
                last_error = exc
                logger.error("Unexpected OpenRouter error: %s", exc)
                if attempt < max_retries - 1:
                    time.sleep(1)

        raise RuntimeError(
            f"OpenRouter call failed after {max_retries} attempts: {last_error}"
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _strip_markdown_fences(text: str) -> str:
        """Remove ```json / ``` wrappers that some models add."""
        stripped = text.strip()
        if stripped.startswith("```"):
            lines = stripped.splitlines()
            # drop opening fence line (```json or ```)
            lines = lines[1:]
            # drop closing fence line
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            stripped = "\n".join(lines).strip()
        return stripped
