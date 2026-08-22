"""
OpenAI ChatGPT LLM Provider implementation.

Calls official OpenAI API (https://api.openai.com/v1/chat/completions)
with automatic multi-model fallback (gpt-4o-mini -> gpt-4o -> gpt-3.5-turbo).
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

OPENAI_MODEL_CANDIDATES = [
    "gpt-4o-mini",
    "gpt-4o",
    "gpt-3.5-turbo",
]


class OpenAILLMProvider(LLMProvider):
    """OpenAI ChatGPT LLM Provider."""

    @property
    def provider_id(self) -> str:
        return "openai"

    @property
    def provider_name(self) -> str:
        return "OpenAI ChatGPT"

    @property
    def is_free(self) -> bool:
        return False

    @property
    def requires_api_key(self) -> bool:
        return True

    async def validate_configuration(self) -> bool:
        settings = get_settings()
        if not settings.OPENAI_API_KEY:
            return False
        try:
            url = "https://api.openai.com/v1/models"
            headers = {"Authorization": f"Bearer {settings.OPENAI_API_KEY}"}
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(url, headers=headers)
                return res.status_code == 200
        except Exception as e:
            logger.warning("OpenAI configuration validation failed", error=str(e))
            return False

    async def generate_text(self, prompt: str, system_prompt: str = "") -> str:
        settings = get_settings()
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY chưa được cấu hình trong .env")

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json",
        }

        last_error = None
        async with httpx.AsyncClient(timeout=60.0) as client:
            for model in OPENAI_MODEL_CANDIDATES:
                url = "https://api.openai.com/v1/chat/completions"
                payload = {
                    "model": model,
                    "messages": messages,
                    "temperature": 0.3,
                }
                try:
                    res = await client.post(url, json=payload, headers=headers)
                    if res.status_code == 200:
                        data = res.json()
                        choices = data.get("choices", [])
                        if choices:
                            msg = choices[0].get("message", {})
                            content = msg.get("content", "")
                            if content:
                                return content.strip()
                    elif res.status_code == 429:
                        res_text = res.text
                        if "insufficient_quota" in res_text or "no credits remaining" in res_text or "quota" in res_text.lower():
                            raise RuntimeError(f"OpenAI API Quota Exceeded (HTTP 429): Tài khoản OpenAI hết credit/quota. Vui lòng nạp thêm credit hoặc sử dụng Google Gemini.")
                        logger.warning(f"OpenAI rate limit reached on '{model}'. Trying next model candidate...")
                        last_error = f"HTTP 429 Rate Limit: {res_text[:150]}"
                        continue
                    elif res.status_code in (404, 500, 502, 503, 504):
                        logger.warning(f"OpenAI model '{model}' returned HTTP {res.status_code}. Trying next model candidate...")
                        last_error = f"HTTP {res.status_code}: {res.text[:150]}"
                        continue
                    else:
                        raise RuntimeError(f"OpenAI API error HTTP {res.status_code}: {res.text[:200]}")
                except RuntimeError:
                    raise
                except (httpx.TimeoutException, httpx.RequestError) as req_err:
                    logger.warning(f"OpenAI request error on '{model}': {str(req_err)}")
                    last_error = str(req_err)
                    continue

        raise RuntimeError(f"Tất cả các model OpenAI API đều không khả thi hoặc gặp lỗi: {last_error or 'Unknown error'}")

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
                limit=None,
                remaining=None,
                unit="tokens",
            )
        ]
