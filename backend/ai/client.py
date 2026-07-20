"""
OpenRouter API Client for Cryptanium AI Engine.
Provides model interaction with Nemotron Flash, key rotation, retry logic, and fallback handling.
"""

import os
import json
import time
import logging
import urllib.request
import urllib.error
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class OpenRouterClient:
    """Production-ready OpenRouter API Client."""

    DEFAULT_MODEL = "nvidia/nemotron-4-340b-instruct"

    def __init__(self, api_keys: Optional[List[str]] = None, default_model: Optional[str] = None):
        env_keys = os.getenv("OPENROUTER_API_KEYS", os.getenv("OPENROUTER_API_KEY", os.getenv("OPENAI_API_KEY", "")))
        self.api_keys = api_keys or [k.strip() for k in env_keys.split(",") if k.strip()]
        self.model = default_model or os.getenv("OPENROUTER_MODEL", self.DEFAULT_MODEL)
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self._key_index = 0

    def _get_next_key(self) -> Optional[str]:
        if not self.api_keys:
            return None
        key = self.api_keys[self._key_index % len(self.api_keys)]
        self._key_index += 1
        return key

    def chat_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        json_mode: bool = True,
        max_retries: int = 3,
        timeout: int = 20,
    ) -> Dict[str, Any]:
        key = self._get_next_key()
        if not key:
            raise ValueError("No OpenRouter API key configured.")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
            "HTTP-Referer": "https://github.com/venkatesh-99-cbs/Cryptanium",
            "X-Title": "Cryptanium Security Engine",
        }

        body: Dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
        }

        payload_bytes = json.dumps(body).encode("utf-8")

        for attempt in range(max_retries):
            try:
                req = urllib.request.Request(self.base_url, data=payload_bytes, headers=headers, method="POST")
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    resp_data = json.loads(resp.read().decode("utf-8"))
                    content = resp_data["choices"][0]["message"]["content"]
                    
                    # Clean markdown codeblocks if LLM wraps JSON response
                    clean_content = content.strip()
                    if clean_content.startswith("```"):
                        lines = clean_content.splitlines()
                        if lines[0].startswith("```"):
                            lines = lines[1:]
                        if lines and lines[-1].startswith("```"):
                            lines = lines[:-1]
                        clean_content = "\n".join(lines).strip()

                    return json.loads(clean_content)
            except urllib.error.HTTPError as e:
                if e.code in (429, 502, 503, 504) and attempt < max_retries - 1:
                    sleep_time = (2 ** attempt) + 1
                    logger.warning(f"OpenRouter HTTP {e.code}. Retrying in {sleep_time}s...")
                    time.sleep(sleep_time)
                else:
                    logger.error(f"OpenRouter HTTP error {e.code}: {e.reason}")
                    raise
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(1)
                else:
                    logger.error(f"OpenRouter call failed: {e}")
                    raise
