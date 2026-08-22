"""
Google Gemini LLM Provider implementation.

Calls official Google Gemini AI Studio API with automatic multi-model fallback
(gemini-flash-latest -> gemini-1.5-flash-latest -> gemini-2.0-flash -> gemini-pro-latest).
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

GEMINI_MODEL_CANDIDATES = [
    "gemini-3.5-flash-lite",
    "gemini-3.5-flash",
    "gemini-3.6-flash",
    "gemini-flash-latest",
    "gemini-flash-lite-latest",
    "gemini-2.5-flash",
    "gemini-pro-latest",
]




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

        full_text = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        payload = {
            "contents": [
                {
                    "parts": [{"text": full_text}]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 8192,
                "responseMimeType": "application/json",
            }
        }

        last_error = None
        async with httpx.AsyncClient(timeout=60.0) as client:
            for model in GEMINI_MODEL_CANDIDATES:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={settings.GEMINI_API_KEY}"
                try:
                    res = await client.post(url, json=payload)
                    if res.status_code == 200:
                        data = res.json()
                        candidates = data.get("candidates", [])
                        if candidates:
                            cand = candidates[0]
                            finish_reason = cand.get("finishReason") or cand.get("finish_reason")
                            parts = cand.get("content", {}).get("parts", [])
                            if parts:
                                text_content = parts[0].get("text", "").strip()
                                if finish_reason == "MAX_TOKENS":
                                    logger.warning(f"Gemini model '{model}' output truncated (finishReason=MAX_TOKENS).")
                                    # If JSON response is obviously truncated, raise error to trigger sub-batching/retry
                                    if not (text_content.endswith("]") or text_content.endswith("}")):
                                        raise RuntimeError(f"Gemini API output truncated due to MAX_TOKENS limit on model '{model}'.")
                                return text_content
                    elif res.status_code in (400, 404, 503, 429):
                        # Retry without responseMimeType if 400 bad request occurs (for legacy compatibility)
                        if res.status_code == 400 and "responseMimeType" in payload.get("generationConfig", {}):
                            payload_fallback = dict(payload)
                            payload_fallback["generationConfig"] = {
                                "temperature": 0.2,
                                "maxOutputTokens": 8192,
                            }
                            fb_res = await client.post(url, json=payload_fallback)
                            if fb_res.status_code == 200:
                                fb_data = fb_res.json()
                                candidates = fb_data.get("candidates", [])
                                if candidates:
                                    parts = candidates[0].get("content", {}).get("parts", [])
                                    if parts:
                                        return parts[0].get("text", "").strip()
                        logger.warning(f"Gemini model '{model}' returned HTTP {res.status_code}. Trying next fallback model...")
                        last_error = f"HTTP {res.status_code}: {res.text[:150]}"
                        continue
                    else:
                        raise RuntimeError(f"Gemini API error HTTP {res.status_code}: {res.text[:200]}")
                except RuntimeError:
                    raise
                except (httpx.TimeoutException, httpx.RequestError) as req_err:
                    logger.warning(f"Gemini request error on '{model}': {str(req_err)}")
                    last_error = str(req_err)
                    continue

        raise RuntimeError(f"Tất cả các model Gemini API đều không khả thi hoặc gặp lỗi: {last_error or 'Unknown error'}")

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
