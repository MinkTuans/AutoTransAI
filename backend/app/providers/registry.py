"""
Provider registry — central lookup for all configured providers.

Providers register themselves here. The workflow engine and API routes
use this registry to get providers by ID, never importing them directly.
"""

from __future__ import annotations

from app.core import get_logger
from app.providers.base import AudioProvider, VideoProvider, LLMProvider, ImageProvider, VisionProvider

logger = get_logger(__name__)

_registry: ProviderRegistry | None = None


class ProviderRegistry:
    """
    Singleton registry for all AI providers.

    Usage:
        registry = ProviderRegistry()
        registry.register_audio(edge_tts_provider)
        provider = registry.get_audio("edge_tts")
    """

    def __init__(self) -> None:
        self._audio: dict[str, AudioProvider] = {}
        self._video: dict[str, VideoProvider] = {}
        self._llm: dict[str, LLMProvider] = {}
        self._image: dict[str, ImageProvider] = {}
        self._vision: dict[str, VisionProvider] = {}

    def register_audio(self, provider: AudioProvider) -> None:
        """Register an audio provider."""
        self._audio[provider.provider_id] = provider
        logger.info("Registered audio provider", provider_id=provider.provider_id)

    def register_video(self, provider: VideoProvider) -> None:
        """Register a video provider."""
        self._video[provider.provider_id] = provider
        logger.info("Registered video provider", provider_id=provider.provider_id)

    def register_llm(self, provider: LLMProvider) -> None:
        """Register an LLM provider."""
        self._llm[provider.provider_id] = provider
        logger.info("Registered LLM provider", provider_id=provider.provider_id)

    def register_image(self, provider: ImageProvider) -> None:
        """Register an Image provider."""
        self._image[provider.provider_id] = provider
        logger.info("Registered image provider", provider_id=provider.provider_id)

    def register_vision(self, provider: VisionProvider) -> None:
        """Register a Vision multimodal provider."""
        self._vision[provider.provider_id] = provider
        logger.info("Registered vision provider", provider_id=provider.provider_id)

    def get_audio(self, provider_id: str) -> AudioProvider | None:
        """Get an audio provider by ID."""
        return self._audio.get(provider_id)

    def get_video(self, provider_id: str) -> VideoProvider | None:
        """Get a video provider by ID."""
        return self._video.get(provider_id)

    def get_llm(self, provider_id: str) -> LLMProvider | None:
        """Get an LLM provider by ID."""
        return self._llm.get(provider_id)

    def get_image(self, provider_id: str) -> ImageProvider | None:
        """Get an image provider by ID."""
        return self._image.get(provider_id)

    def get_vision(self, provider_id: str) -> VisionProvider | None:
        """Get a vision provider by ID."""
        return self._vision.get(provider_id)

    def list_audio(self) -> list[AudioProvider]:
        """List all registered audio providers."""
        return list(self._audio.values())

    def list_video(self) -> list[VideoProvider]:
        """List all registered video providers."""
        return list(self._video.values())

    def list_llm(self) -> list[LLMProvider]:
        """List all registered LLM providers."""
        return list(self._llm.values())

    def list_image(self) -> list[ImageProvider]:
        """List all registered image providers."""
        return list(self._image.values())

    def list_vision(self) -> list[VisionProvider]:
        """List all registered vision providers."""
        return list(self._vision.values())

    def get_all_providers(self) -> dict[str, list]:
        """Get all providers grouped by type. Used by the /providers endpoint."""
        return {
            "audio": self.list_audio(),
            "video": self.list_video(),
            "llm": self.list_llm(),
            "image": self.list_image(),
            "vision": self.list_vision(),
        }


def _register_defaults(reg: ProviderRegistry) -> None:
    try:
        from app.providers.audio.edge_tts_provider import EdgeTTSProvider
        reg.register_audio(EdgeTTSProvider())
    except Exception as e:
        logger.warning("Failed to register EdgeTTSProvider", error=str(e))

    try:
        from app.providers.audio.google_tts_provider import GoogleCloudTTSProvider
        reg.register_audio(GoogleCloudTTSProvider())
    except Exception as e:
        logger.warning("Failed to register GoogleCloudTTSProvider", error=str(e))

    try:
        from app.providers.audio.elevenlabs_provider import ElevenLabsAudioProvider
        reg.register_audio(ElevenLabsAudioProvider())
    except Exception as e:
        logger.warning("Failed to register ElevenLabsAudioProvider", error=str(e))

    try:
        from app.providers.video.local_provider import LocalVideoProvider
        from app.providers.video.kling_provider import KlingVideoProvider
        from app.providers.video.fal_provider import FalVideoProvider
        reg.register_video(LocalVideoProvider())
        reg.register_video(KlingVideoProvider())
        reg.register_video(FalVideoProvider())
    except Exception:
        pass

    try:
        from app.providers.llm.openai_provider import OpenAILLMProvider
        from app.providers.llm.gemini_provider import GeminiLLMProvider
        reg.register_llm(OpenAILLMProvider())
        reg.register_llm(GeminiLLMProvider())
    except Exception as e:
        logger.warning("Failed to register LLM providers", error=str(e))

    try:
        from app.providers.vision.gemini_vision import GeminiVisionProvider
        from app.providers.vision.openai_vision import OpenAIVisionProvider
        reg.register_vision(GeminiVisionProvider())
        reg.register_vision(OpenAIVisionProvider())
    except Exception as e:
        logger.warning("Failed to register Vision providers", error=str(e))

    try:
        from app.providers.image.pollinations_provider import PollinationsImageProvider
        from app.providers.image.fal_image_provider import FalImageProvider
        from app.providers.image.openai_image_provider import OpenAIImageProvider
        from app.providers.image.local_image_provider import LocalImageProvider
        reg.register_image(PollinationsImageProvider())
        reg.register_image(FalImageProvider())
        reg.register_image(OpenAIImageProvider())
        reg.register_image(LocalImageProvider())
    except Exception as e:
        logger.warning("Failed to register image providers", error=str(e))

    try:
        from app.providers.openrouter_provider import (
            OpenRouterAudioProvider, OpenRouterImageProvider, OpenRouterLLMProvider,
            OpenRouterVideoProvider, OpenRouterVisionProvider,
        )
        reg.register_audio(OpenRouterAudioProvider())
        reg.register_video(OpenRouterVideoProvider())
        reg.register_llm(OpenRouterLLMProvider())
        reg.register_image(OpenRouterImageProvider())
        reg.register_vision(OpenRouterVisionProvider())
    except Exception as e:
        logger.warning("Failed to register OpenRouter providers", error=str(e))


def get_registry() -> ProviderRegistry:
    """Get the global provider registry singleton."""
    global _registry
    if _registry is None:
        _registry = ProviderRegistry()
        _register_defaults(_registry)
    return _registry
