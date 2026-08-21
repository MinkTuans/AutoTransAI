"""
Google Cloud Text-to-Speech Provider implementation.

Calls the official Google Cloud TTS REST API.
"""

from __future__ import annotations

import base64
from pathlib import Path
import httpx

from app.config import get_settings
from app.core import get_logger
from app.providers.base import (
    AudioProvider,
    GenerationResult,
    QuotaInfo,
    UsageEstimate,
    VoiceInfo,
)

logger = get_logger(__name__)
settings = get_settings()


class GoogleCloudTTSProvider(AudioProvider):
    """Google Cloud TTS Provider."""

    @property
    def provider_id(self) -> str:
        return "google_cloud_tts"

    @property
    def provider_name(self) -> str:
        return "Google Cloud TTS"

    @property
    def is_free(self) -> bool:
        return False

    @property
    def requires_api_key(self) -> bool:
        return True

    async def validate_configuration(self) -> bool:
        if not settings.GOOGLE_CLOUD_TTS_API_KEY:
            return False
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(
                    f"https://texttospeech.googleapis.com/v1/voices?key={settings.GOOGLE_CLOUD_TTS_API_KEY}"
                )
                return res.status_code == 200
        except Exception as e:
            logger.warning("Google Cloud TTS validation failed", error=str(e))
            return False

    async def get_voices(self, language: str | None = None) -> list[VoiceInfo]:
        if settings.GOOGLE_CLOUD_TTS_API_KEY:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    res = await client.get(
                        f"https://texttospeech.googleapis.com/v1/voices?key={settings.GOOGLE_CLOUD_TTS_API_KEY}"
                    )
                    if res.status_code == 200:
                        data = res.json()
                        voices = []
                        for v in data.get("voices", []):
                            v_name = v.get("name", "")
                            lang_codes = v.get("languageCodes", ["en-US"])
                            lang = lang_codes[0] if lang_codes else "en-US"
                            if language and not lang.lower().startswith(language.lower()):
                                continue
                            voices.append(
                                VoiceInfo(
                                    id=v_name,
                                    name=f"{v_name} ({v.get('ssmlGender', 'NEUTRAL')})",
                                    language=lang,
                                    gender=v.get("ssmlGender"),
                                )
                            )
                        if voices:
                            return voices[:50]  # Limit list size for UI performance
            except Exception as e:
                logger.warning("Failed to fetch Google Cloud TTS voices", error=str(e))

        # Fallback default voices
        return [
            VoiceInfo(id="vi-VN-Standard-A", name="Vietnamese Standard A", language="vi-VN"),
            VoiceInfo(id="vi-VN-Neural2-A", name="Vietnamese Neural2 A", language="vi-VN"),
            VoiceInfo(id="en-US-Neural2-F", name="English Neural2 F", language="en-US"),
        ]

    async def generate_audio(
        self,
        text: str,
        voice_id: str,
        output_path: Path,
    ) -> GenerationResult:
        if not settings.GOOGLE_CLOUD_TTS_API_KEY:
            return GenerationResult(
                success=False,
                error_message="GOOGLE_CLOUD_TTS_API_KEY not set in .env",
                error_code="API_KEY_MISSING",
                provider_id=self.provider_id,
            )

        v_id = voice_id or "vi-VN-Neural2-A"
        # Extract language code from voice_id (e.g. vi-VN-Neural2-A -> vi-VN)
        parts = v_id.split("-")
        lang_code = f"{parts[0]}-{parts[1]}" if len(parts) >= 2 else "vi-VN"

        url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={settings.GOOGLE_CLOUD_TTS_API_KEY}"
        payload = {
            "input": {"text": text},
            "voice": {
                "languageCode": lang_code,
                "name": v_id,
            },
            "audioConfig": {
                "audioEncoding": "LINEAR16",
            },
        }

        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, json=payload)

                if response.status_code != 200:
                    err_msg = f"Google Cloud TTS API error HTTP {response.status_code}: {response.text[:200]}"
                    logger.error(err_msg)
                    return GenerationResult(
                        success=False,
                        error_message=err_msg,
                        error_code=f"HTTP_{response.status_code}",
                        provider_id=self.provider_id,
                    )

                data = response.json()
                audio_b64 = data.get("audioContent")
                if not audio_b64:
                    return GenerationResult(
                        success=False,
                        error_message="Google Cloud TTS API response missing audioContent",
                        error_code="MISSING_AUDIO_CONTENT",
                        provider_id=self.provider_id,
                    )

                audio_data = base64.b64decode(audio_b64)
                if len(audio_data) == 0:
                    return GenerationResult(
                        success=False,
                        error_message="Decoded audio content is 0 bytes",
                        error_code="EMPTY_AUDIO",
                        provider_id=self.provider_id,
                    )

                output_path.write_bytes(audio_data)

                if not output_path.exists() or output_path.stat().st_size == 0:
                    return GenerationResult(
                        success=False,
                        error_message="Failed to write audio file to disk",
                        error_code="FILE_WRITE_ERROR",
                        provider_id=self.provider_id,
                    )

                logger.info(
                    "Google Cloud TTS audio generated",
                    voice_id=v_id,
                    size=len(audio_data),
                    output_path=str(output_path),
                )
                return GenerationResult(
                    success=True,
                    file_path=output_path,
                    provider_id=self.provider_id,
                    metadata={"voice_id": v_id, "char_count": len(text)},
                )

        except Exception as e:
            logger.error("Google Cloud TTS generation failed", error=str(e))
            return GenerationResult(
                success=False,
                error_message=str(e),
                error_code="GENERATION_EXCEPTION",
                provider_id=self.provider_id,
            )

    async def estimate_usage(self, text: str) -> list[UsageEstimate]:
        return [
            UsageEstimate(
                resource_type="characters",
                estimated_amount=float(len(text)),
                unit="characters",
            )
        ]

    async def get_quota(self) -> list[QuotaInfo]:
        return [
            QuotaInfo(
                resource_type="characters",
                used=None,
                limit=1000000.0,  # 1M free chars/month for Neural2
                remaining=None,
                unit="characters",
            )
        ]
