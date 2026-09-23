"""
Google Gemini LLM Provider implementation.

Model selection is handled by AIModelResolver — this provider accepts
an explicit model parameter and uses it directly without modification.
"""

from __future__ import annotations

from typing import Optional

import httpx

from app.config import get_settings
from app.core import get_logger
from app.providers.base import (
    LLMProvider,
    QuotaInfo,
    UsageEstimate,
)
from app.providers.request_target import resolve_request_target
from app.services.ai_routing import RouteTarget

logger = get_logger(__name__)
settings = get_settings()


def strip_gemini_model_prefix(model_name: Optional[str]) -> str:
    """
    Strip 'models/' prefix from Gemini model name.
    ONLY removes prefix — does NOT modify the actual model identifier.

    Example: 'models/gemini-2.5-flash' -> 'gemini-2.5-flash'
    """
    if not model_name:
        return ""
    m = str(model_name).strip()
    if m.startswith("models/"):
        m = m[len("models/"):]
    return m


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
            url = "https://generativelanguage.googleapis.com/v1beta/models"
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(url, headers={"x-goog-api-key": settings.GEMINI_API_KEY})
                return res.status_code == 200
        except Exception:
            logger.warning("Gemini validation failed")
            return False

    async def generate_text(self, prompt: str, system_prompt: str = "", model: Optional[str] = None,
                            *, route_target: RouteTarget | None = None, api_key: str | None = None) -> str:
        """
        Generate text using Gemini API.

        Args:
            prompt: The user prompt text.
            system_prompt: Optional system prompt.
            model: Model ID from AIModelResolver. If not provided, uses the first available model.
        """
        from app.core.pipeline_errors import classify_http_error, PipelineError

        model, request_key = resolve_request_target(
            route_target, api_key, provider_id="gemini", capabilities=("LLM", "TRANSLATION"),
            legacy_model=model, legacy_key=settings.GEMINI_API_KEY,
        )
        if not request_key:
            raise ValueError("GEMINI_API_KEY not set in .env")

        # Use explicitly provided model or attempt fallback resolution via AIModelResolver
        if not model:
            from app.services.model_resolver import AIModelResolver
            try:
                res_info = await AIModelResolver.resolve_model(capability="TRANSLATION", stage="LLM")
                model = res_info.model_id
            except Exception as res_err:
                logger.warning(f"Fallback resolution for Gemini LLM model failed: {res_err}")

        if not model:
            raise PipelineError(
                code="AI_CONFIGURATION_ERROR",
                stage="LLM",
                message="Không có model nào được chỉ định cho Gemini LLM. Vui lòng cấu hình model trong Settings.",
            )

        target_model = strip_gemini_model_prefix(model)

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

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{target_model}:generateContent"
        headers = {"x-goog-api-key": request_key}

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                res = await client.post(url, json=payload, headers=headers)
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
                                logger.warning(f"Gemini model '{target_model}' output truncated (finishReason=MAX_TOKENS).")
                                # If JSON response is obviously truncated, raise error to trigger sub-batching/retry
                                if not (text_content.endswith("]") or text_content.endswith("}")):
                                    raise RuntimeError(f"Gemini API output truncated due to MAX_TOKENS limit on model '{target_model}'.")
                            return text_content

                elif res.status_code == 400 and "responseMimeType" in payload.get("generationConfig", {}):
                    # Retry without responseMimeType for legacy compatibility
                    payload_fallback = dict(payload)
                    payload_fallback["generationConfig"] = {
                        "temperature": 0.2,
                        "maxOutputTokens": 8192,
                    }
                    fb_res = await client.post(url, json=payload_fallback, headers=headers)
                    if fb_res.status_code == 200:
                        fb_data = fb_res.json()
                        candidates = fb_data.get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            if parts:
                                return parts[0].get("text", "").strip()

                # Non-200 error — classify into structured error
                raise classify_http_error(
                    status_code=res.status_code,
                    response_text="",
                    provider="gemini",
                    model=target_model,
                    stage="LLM",
                )

            except PipelineError:
                raise
            except RuntimeError:
                raise
            except (httpx.TimeoutException, httpx.RequestError):
                from app.core.pipeline_errors import PipelineError, NETWORK_ERROR
                raise PipelineError(code=NETWORK_ERROR, stage="LLM", provider="gemini", model=target_model,
                                    message="Gemini request failed.") from None

        raise RuntimeError(f"Gemini API trả về kết quả rỗng cho model '{target_model}'.")

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
