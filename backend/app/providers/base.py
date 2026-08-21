"""
Base interfaces for all AI providers.

Every provider must implement the appropriate ABC.
This is the contract that keeps workflow code provider-independent.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class VoiceInfo:
    """Information about an available voice."""
    id: str
    name: str
    language: str
    gender: str | None = None
    style: str | None = None
    preview_url: str | None = None


@dataclass
class GenerationResult:
    """Result of a generation operation."""
    success: bool
    file_path: Path | None = None
    duration: float | None = None
    error_message: str | None = None
    error_code: str | None = None
    provider_id: str = ""
    metadata: dict = field(default_factory=dict)


@dataclass
class QuotaInfo:
    """Quota information from a provider."""
    resource_type: str  # characters, credits, tokens, etc.
    used: float | None = None
    limit: float | None = None
    remaining: float | None = None  # None = unknown
    unit: str = ""
    reset_period: str | None = None  # daily, monthly, etc.


@dataclass
class UsageEstimate:
    """Estimated resource usage for a task."""
    resource_type: str
    estimated_amount: float
    unit: str


class AudioProvider(ABC):
    """Abstract base class for Text-to-Speech providers."""

    @property
    @abstractmethod
    def provider_id(self) -> str:
        """Unique identifier for this provider."""
        ...

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Human-readable name."""
        ...

    @property
    @abstractmethod
    def is_free(self) -> bool:
        """Whether this provider has a free tier."""
        ...

    @property
    @abstractmethod
    def requires_api_key(self) -> bool:
        """Whether this provider needs an API key."""
        ...

    @abstractmethod
    async def validate_configuration(self) -> bool:
        """Check if the provider is properly configured and reachable."""
        ...

    @abstractmethod
    async def get_voices(self, language: str | None = None) -> list[VoiceInfo]:
        """List available voices, optionally filtered by language."""
        ...

    @abstractmethod
    async def generate_audio(
        self,
        text: str,
        voice_id: str,
        output_path: Path,
    ) -> GenerationResult:
        """
        Generate audio from text.

        Args:
            text: The text to convert to speech.
            voice_id: The voice identifier to use.
            output_path: Where to save the audio file.

        Returns:
            GenerationResult with success status and file info.
        """
        ...

    @abstractmethod
    async def estimate_usage(self, text: str) -> list[UsageEstimate]:
        """Estimate resource usage for generating audio from this text."""
        ...

    @abstractmethod
    async def get_quota(self) -> list[QuotaInfo]:
        """Get current quota information. Returns unknown if not available."""
        ...


class VideoProvider(ABC):
    """Abstract base class for Text-to-Video providers."""

    @property
    @abstractmethod
    def provider_id(self) -> str:
        ...

    @property
    @abstractmethod
    def provider_name(self) -> str:
        ...

    @property
    @abstractmethod
    def is_free(self) -> bool:
        ...

    @property
    @abstractmethod
    def requires_api_key(self) -> bool:
        ...

    @property
    @abstractmethod
    def max_duration_seconds(self) -> int:
        """Maximum video duration this provider supports in a single generation."""
        ...

    @property
    @abstractmethod
    def supported_durations(self) -> list[int]:
        """List of supported video durations in seconds."""
        ...

    @abstractmethod
    async def validate_configuration(self) -> bool:
        ...

    @abstractmethod
    async def generate_video(
        self,
        prompt: str,
        duration: int,
        output_path: Path,
    ) -> GenerationResult:
        """
        Generate a video from a text prompt.

        Args:
            prompt: Text description for the video.
            duration: Target duration in seconds.
            output_path: Where to save the video file.

        Returns:
            GenerationResult with success status and file info.
        """
        ...

    @abstractmethod
    async def estimate_usage(self, duration: int) -> list[UsageEstimate]:
        ...

    @abstractmethod
    async def get_quota(self) -> list[QuotaInfo]:
        ...


class LLMProvider(ABC):
    """Abstract base class for LLM providers (optional, for script enhancement)."""

    @property
    @abstractmethod
    def provider_id(self) -> str:
        ...

    @property
    @abstractmethod
    def provider_name(self) -> str:
        ...

    @abstractmethod
    async def validate_configuration(self) -> bool:
        ...

    @abstractmethod
    async def generate_text(self, prompt: str, system_prompt: str = "") -> str:
        ...

    @abstractmethod
    async def estimate_usage(self, input_text: str) -> list[UsageEstimate]:
        ...

    @abstractmethod
    async def get_quota(self) -> list[QuotaInfo]:
        ...
