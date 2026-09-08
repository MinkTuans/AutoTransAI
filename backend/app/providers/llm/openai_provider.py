"""
OpenAI ChatGPT LLM Provider implementation.

Calls official OpenAI API (https://api.openai.com/v1/chat/completions).
Model selection is handled by AIModelResolver — this provider accepts
an explicit model parameter and uses it directly.
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

logger = get_logger(__name__)
settings = get_settings()


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

    async def generate_text(self, prompt: str, system_prompt: str = "", model: Optional[str] = None) -> str:
        """
        Generate text using OpenAI API.

        Args:
            prompt: The user prompt text.
            system_prompt: Optional system prompt.
            model: Model ID from AIModelResolver. If not provided, raises error.
        """
        from app.core.pipeline_errors import classify_http_error, classify_exception, PipelineError

        settings = get_settings()
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY chưa được cấu hình trong .env")

        if not model:
            raise PipelineError(
                code="AI_CONFIGURATION_ERROR",
                stage="LLM",
                message="Không có model nào được chỉ định cho OpenAI LLM. Vui lòng cấu hình model trong Settings.",
            )

        target_model = model

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json",
        }

        url = "https://api.openai.com/v1/chat/completions"
        payload = {
            "model": target_model,
            "messages": messages,
            "temperature": 0.3,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
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

                # Non-200 — classify into structured error
                raise classify_http_error(
                    status_code=res.status_code,
                    response_text=res.text[:500],
                    provider="openai",
                    model=target_model,
                    stage="LLM",
                )

            except PipelineError:
                raise
            except RuntimeError:
                raise
            except (httpx.TimeoutException, httpx.RequestError) as req_err:
                raise classify_exception(req_err, provider="openai", model=target_model, stage="LLM")

        raise RuntimeError(f"OpenAI API trả về kết quả rỗng cho model '{target_model}'.")

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
