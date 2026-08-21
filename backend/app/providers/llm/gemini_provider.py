"""
Google Gemini LLM Provider implementation.

Calls the official Google Gemini AI Studio API.
"""

from __future__ import annotations

import httpx

from app.config import get_settings
from app.core import get_logger
from app.providers.base import (
    LLMProvider,
    QuotaInfo,
    UsageEstimate,
)

logger = get_logger(__name__)
settings = get_settings()


class GeminiLLMProvider(LLMProvider):
    """Google Gemini LLM Provider."""

    @property
    def provider_id(self) -> str:
        return "gemini"

    @property
    def provider_name(self) -> str:
        return "Google Gemini AI Studio"

    @property
    def is_free(self) -> bool:
        return True  # Free tier available

    @property
    def requires_api_key(self) -> bool:
        return True

    async def validate_configuration(self) -> bool:
        if not settings.GEMINI_API_KEY:
            return False
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models?key={settings.GEMINI_API_KEY}"
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(url)
                return res.status_code == 200
        except Exception as e:
            logger.warning("Gemini validation failed", error=str(e))
            return False

    async def generate_text(self, prompt: str, system_prompt: str = "") -> str:
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not set in .env")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
        full_text = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        payload = {
            "contents": [
                {
                    "parts": [{"text": full_text}]
                }
            ]
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code != 200:
                    raise RuntimeError(f"Gemini API error HTTP {res.status_code}: {res.text[:200]}")

                data = res.json()
                candidates = data.get("candidates", [])
                if not candidates:
                    raise RuntimeError("Gemini API returned no candidates")

                parts = candidates[0].get("content", {}).get("parts", [])
                if not parts:
                    raise RuntimeError("Gemini candidate content empty")

                return parts[0].get("text", "").strip()

        except Exception as e:
            logger.error("Gemini text generation failed", error=str(e))
            raise

    async def estimate_usage(self, input_text: str) -> list[UsageEstimate]:
        return [
            UsageEstimate(
                resource_type="input_tokens",
                estimated_amount=float(len(input_text) // 4),
                unit="tokens",
            )
        ]

    async def get_quota(self) -> list[QuotaInfo]:
        return [
            QuotaInfo(
                resource_type="tokens",
                used=None,
                limit=1500000.0,  # ~1.5M free tokens/day on AI Studio free tier
                remaining=None,
                unit="tokens",
            )
        ]
