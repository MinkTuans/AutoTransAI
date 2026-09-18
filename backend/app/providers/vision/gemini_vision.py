"""
Google Gemini Vision Multimodal Provider.
Sends image + prompt to Google Gemini generateContent API endpoint.
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


class GeminiVisionProvider(VisionProvider):
    """Google Gemini Vision API Provider."""

    @property
    def provider_id(self) -> str:
        return "gemini"

    @property
    def provider_name(self) -> str:
        return "Google Gemini Vision"

    @property
    def is_free(self) -> bool:
        return True

    @property
    def requires_api_key(self) -> bool:
        return True

    async def validate_configuration(self) -> bool:
        return bool(settings.GEMINI_API_KEY)

    async def analyze_image(
        self,
        image_path: Path | str,
        prompt: str,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """Send image and prompt to Gemini Vision API."""
        key = api_key or settings.GEMINI_API_KEY
        if not key:
            raise ValueError("[Gemini Vision] Missing GEMINI_API_KEY")

        target_model = model or "gemini-2.0-flash"
        if target_model.startswith("models/"):
            target_model = target_model[len("models/"):]

        img_path = Path(image_path)
        if not img_path.is_file():
            raise FileNotFoundError(f"[Gemini Vision] Image file not found: {img_path}")

        image_bytes = img_path.read_bytes()
        base64_image = base64.b64encode(image_bytes).decode("utf-8")

        suffix = img_path.suffix.lower()
        mime_type = "image/png" if suffix == ".png" else "image/jpeg"

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{target_model}:generateContent?key={key}"
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": mime_type,
                                "data": base64_image,
                            }
                        },
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 20,
            },
        }

        timeout = float(kwargs.get("timeout", 45.0))
        async with httpx.AsyncClient(timeout=timeout) as client:
            res = await client.post(url, json=payload)
            if res.status_code == 200:
                data = res.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return parts[0].get("text", "").strip()
                return ""
            else:
                error_msg = f"Gemini Vision API returned HTTP {res.status_code}: {res.text[:300]}"
                logger.error(f"[Gemini Vision Error] {error_msg}")
                raise RuntimeError(error_msg)
