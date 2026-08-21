"""
Provider registry — central lookup for all configured providers.

Providers register themselves here. The workflow engine and API routes
use this registry to get providers by ID, never importing them directly.
"""

from __future__ import annotations

from app.core import get_logger
from app.providers.base import AudioProvider, VideoProvider, LLMProvider

logger = get_logger(__name__)


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

    def get_audio(self, provider_id: str) -> AudioProvider | None:
        """Get an audio provider by ID."""
        return self._audio.get(provider_id)

    def get_video(self, provider_id: str) -> VideoProvider | None:
        """Get a video provider by ID."""
        return self._video.get(provider_id)

    def get_llm(self, provider_id: str) -> LLMProvider | None:
        """Get an LLM provider by ID."""
        return self._llm.get(provider_id)

    def list_audio(self) -> list[AudioProvider]:
        """List all registered audio providers."""
        return list(self._audio.values())

    def list_video(self) -> list[VideoProvider]:
        """List all registered video providers."""
        return list(self._video.values())

    def list_llm(self) -> list[LLMProvider]:
        """List all registered LLM providers."""
        return list(self._llm.values())

    def get_all_providers(self) -> dict[str, list]:
        """Get all providers grouped by type. Used by the /providers endpoint."""
        return {
            "audio": self.list_audio(),
            "video": self.list_video(),
            "llm": self.list_llm(),
        }


# Global singleton instance
_registry: ProviderRegistry | None = None


def get_registry() -> ProviderRegistry:
    """Get the global provider registry singleton."""
    global _registry
    if _registry is None:
        _registry = ProviderRegistry()
    return _registry
