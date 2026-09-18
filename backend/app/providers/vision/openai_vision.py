"""
OpenAI Vision Multimodal Provider.
Sends image + prompt to OpenAI Chat Completions API with image_url.
"""

from __future__ import annotations

import base64
import logging
from pathlib import Path
from typing import Any, Optional

import httpx

from app.config import get_settings
from app.providers.base import VisionProvider

logger = logging.getLogger(__name__)
settings = get_settings()


class OpenAIVisionProvider(VisionProvider):
    """OpenAI Vision API Provider (GPT-4o, GPT-4o-mini)."""

    @property
    def provider_id(self) -> str:
        return "openai"

    @property
    def provider_name(self) -> str:
        return "OpenAI Vision"

    @property
    def is_free(self) -> bool:
        return False

    @property
    def requires_api_key(self) -> bool:
        return True

    async def validate_configuration(self) -> bool:
        return bool(settings.OPENAI_API_KEY)

    async def analyze_image(
        self,
        image_path: Path | str,
        prompt: str,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """Send image and prompt to OpenAI Vision API."""
        key = api_key or settings.OPENAI_API_KEY
        if not key:
            raise ValueError("[OpenAI Vision] Missing OPENAI_API_KEY")

        target_model = model or "gpt-4o-mini"
        img_path = Path(image_path)
        if not img_path.is_file():
            raise FileNotFoundError(f"[OpenAI Vision] Image file not found: {img_path}")

        image_bytes = img_path.read_bytes()
        base64_image = base64.b64encode(image_bytes).decode("utf-8")

        suffix = img_path.suffix.lower()
        mime_type = "image/png" if suffix == ".png" else "image/jpeg"

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": target_model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{base64_image}",
                                "detail": "low",
                            },
                        },
                    ],
                }
            ],
            "max_tokens": 20,
            "temperature": 0.1,
        }

        timeout = float(kwargs.get("timeout", 45.0))
        async with httpx.AsyncClient(timeout=timeout) as client:
            res = await client.post(url, json=payload, headers=headers)
            if res.status_code == 200:
                data = res.json()
                choices = data.get("choices", [])
                if choices:
                    return choices[0].get("message", {}).get("content", "").strip()
                return ""
            else:
                error_msg = f"OpenAI Vision API returned HTTP {res.status_code}: {res.text[:300]}"
                logger.error(f"[OpenAI Vision Error] {error_msg}")
                raise RuntimeError(error_msg)
