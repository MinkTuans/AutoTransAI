"""
Edge TTS provider — free, no API key, high quality Microsoft neural voices.

Uses the edge-tts library which emulates the Edge browser's Read Aloud feature.
No API key required. Sends text to Microsoft's servers for processing.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import edge_tts

from app.core import get_logger
from app.providers.base import (
    AudioProvider,
    GenerationResult,
    QuotaInfo,
    UsageEstimate,
    VoiceInfo,
)
from app.services.ai_routing import RouteTarget

logger = get_logger(__name__)

# Cache voices to avoid repeated network calls
_voices_cache: list[dict] | None = None
_voices_cache_lock = asyncio.Lock()

# One hung Microsoft request used to freeze DUB at e.g. 31/193 forever.
TTS_SEGMENT_TIMEOUT_SEC = 45.0
TTS_MAX_ATTEMPTS = 3


_FALLBACK_EDGE_VOICES = [
    {"ShortName": "vi-VN-HoaiMyNeural", "FriendlyName": "Microsoft HoaiMy Online (Natural) - Vietnamese (Vietnam)", "Locale": "vi-VN", "Gender": "Female"},
    {"ShortName": "vi-VN-NamMinhNeural", "FriendlyName": "Microsoft NamMinh Online (Natural) - Vietnamese (Vietnam)", "Locale": "vi-VN", "Gender": "Male"},
    {"ShortName": "en-US-AriaNeural", "FriendlyName": "Microsoft Aria Online (Natural) - English (United States)", "Locale": "en-US", "Gender": "Female"},
    {"ShortName": "en-US-GuyNeural", "FriendlyName": "Microsoft Guy Online (Natural) - English (United States)", "Locale": "en-US", "Gender": "Male"},
    {"ShortName": "en-US-JennyNeural", "FriendlyName": "Microsoft Jenny Online (Natural) - English (United States)", "Locale": "en-US", "Gender": "Female"},
    {"ShortName": "en-US-ChristopherNeural", "FriendlyName": "Microsoft Christopher Online (Natural) - English (United States)", "Locale": "en-US", "Gender": "Male"},
    {"ShortName": "zh-CN-XiaoxiaoNeural", "FriendlyName": "Microsoft Xiaoxiao Online (Natural) - Chinese (Mainland)", "Locale": "zh-CN", "Gender": "Female"},
    {"ShortName": "zh-CN-YunxiNeural", "FriendlyName": "Microsoft Yunxi Online (Natural) - Chinese (Mainland)", "Locale": "zh-CN", "Gender": "Male"},
    {"ShortName": "zh-CN-YunjianNeural", "FriendlyName": "Microsoft Yunjian Online (Natural) - Chinese (Mainland)", "Locale": "zh-CN", "Gender": "Male"},
    {"ShortName": "zh-CN-XiaoyiNeural", "FriendlyName": "Microsoft Xiaoyi Online (Natural) - Chinese (Mainland)", "Locale": "zh-CN", "Gender": "Female"},
]


class EdgeTTSProvider(AudioProvider):
    """
    Microsoft Edge TTS provider.

    Free, no API key, 200+ neural voices, 40+ languages.
    Unofficial interface — could break if Microsoft changes their backend.
    """

    @property
    def provider_id(self) -> str:
        return "edge_tts"

    @property
    def provider_name(self) -> str:
        return "Edge TTS (Microsoft)"

    @property
    def is_free(self) -> bool:
        return True

    @property
    def requires_api_key(self) -> bool:
        return False

    async def validate_configuration(self) -> bool:
        """Validate by attempting to list voices (requires internet) or fallback availability."""
        return True

    async def get_voices(self, language: str | None = None) -> list[VoiceInfo]:
        """List available voices, optionally filtered by language code."""
        global _voices_cache

        async with _voices_cache_lock:
            if _voices_cache is None:
                try:
                    _voices_cache = await edge_tts.list_voices()
                except Exception as e:
                    logger.warning("Failed to list live Edge TTS voices, using fallback catalog", error=str(e))
                    _voices_cache = None

        voices = _voices_cache if _voices_cache else _FALLBACK_EDGE_VOICES

        result = []
        norm_lang = language.lower().split("-")[0] if language else None
        for v in voices:
            locale = v.get("Locale", "")
            if norm_lang and not (locale.lower().startswith(norm_lang) or locale.lower() == language.lower()):
                continue

            result.append(VoiceInfo(
                id=v.get("ShortName", ""),
                name=v.get("FriendlyName", v.get("ShortName", "")),
                language=locale,
                gender=v.get("Gender", None),
            ))

        return result

    async def generate_audio(
        self,
        text: str,
        voice_id: str,
        output_path: Path,
        *,
        route_target: RouteTarget | None = None,
        api_key: str | None = None,
    ) -> GenerationResult:
        """
        Generate audio using Edge TTS.

        Args:
            text: Text to speak.
            voice_id: Voice ShortName (e.g., "en-US-AriaNeural").
            output_path: Where to save the output file.

        Returns:
            GenerationResult with the saved audio file path.
        """
        if api_key is not None or (route_target is not None and (
            route_target.provider_id != self.provider_id or route_target.capability != "TTS"
            or not route_target.remote_model_id or route_target.key_id is not None
        )):
            raise ValueError("Edge TTS requires a keyless TTS route target.")
        spoken = (text or "").strip()
        if not spoken:
            return GenerationResult(
                success=False,
                error_message="Empty text",
                error_code="EMPTY_TEXT",
                provider_id=self.provider_id,
            )

        try:
            last_err: Exception | None = None
            for attempt in range(1, TTS_MAX_ATTEMPTS + 1):
                try:
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    if output_path.exists():
                        output_path.unlink()

                    communicate = edge_tts.Communicate(spoken, voice_id)
                    await asyncio.wait_for(
                        communicate.save(str(output_path)),
                        timeout=TTS_SEGMENT_TIMEOUT_SEC,
                    )

                    if output_path.exists() and output_path.stat().st_size > 0:
                        last_err = None
                        break
                except asyncio.TimeoutError as timeout_err:
                    last_err = timeout_err
                    logger.warning(
                        "Edge TTS timed out",
                        attempt=attempt,
                        timeout_sec=TTS_SEGMENT_TIMEOUT_SEC,
                        voice=voice_id,
                    )
                    if attempt == TTS_MAX_ATTEMPTS:
                        return GenerationResult(
                            success=False,
                            error_message=f"Edge TTS timeout after {TTS_SEGMENT_TIMEOUT_SEC:.0f}s",
                            error_code="TTS_TIMEOUT",
                            provider_id=self.provider_id,
                        )
                    await asyncio.sleep(attempt * 1.0)
                except Exception as attempt_err:
                    last_err = attempt_err
                    if attempt == TTS_MAX_ATTEMPTS:
                        raise attempt_err
                    await asyncio.sleep(attempt * 1.0)

            if not output_path.exists():
                return GenerationResult(
                    success=False,
                    error_message="Audio file was not created",
                    error_code="FILE_NOT_CREATED",
                    provider_id=self.provider_id,
                )

            file_size = output_path.stat().st_size
            if file_size == 0:
                output_path.unlink(missing_ok=True)
                return GenerationResult(
                    success=False,
                    error_message="Audio file is empty",
                    error_code="EMPTY_FILE",
                    provider_id=self.provider_id,
                )

            logger.info(
                "Audio generated",
                provider_id=self.provider_id,
                voice=voice_id,
                chars=len(text),
                file_size=file_size,
                output=str(output_path),
            )

            return GenerationResult(
                success=True,
                file_path=output_path,
                provider_id=self.provider_id,
                metadata={"voice_id": voice_id, "char_count": len(text)},
            )

        except Exception as e:
            logger.error(
                "Edge TTS generation failed",
                error=str(e),
                voice=voice_id,
                text_length=len(text),
            )
            return GenerationResult(
                success=False,
                error_message=str(e),
                error_code="GENERATION_ERROR",
                provider_id=self.provider_id,
            )

    async def estimate_usage(self, text: str) -> list[UsageEstimate]:
        """Edge TTS is free — no usage to estimate."""
        return [
            UsageEstimate(
                resource_type="characters",
                estimated_amount=float(len(text)),
                unit="characters",
            )
        ]

    async def get_quota(self) -> list[QuotaInfo]:
        """Edge TTS has no quota — it's free and unlimited (unofficial)."""
        return [
            QuotaInfo(
                resource_type="characters",
                used=None,
                limit=None,
                remaining=None,  # Unknown / unlimited
                unit="characters",
                reset_period=None,
            )
        ]
