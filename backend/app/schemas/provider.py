"""Provider-related Pydantic schemas."""

from __future__ import annotations

from pydantic import BaseModel


class QuotaInfo(BaseModel):
    """Quota information for a specific resource type."""
    resource_type: str  # characters, credits, tokens, seconds, etc.
    used: float | None = None
    limit: float | None = None
    remaining: float | None = None  # None means "unknown"
    unit: str = ""  # human-readable unit name


class ProviderResponse(BaseModel):
    """Provider details for frontend display."""
    id: str
    name: str
    provider_type: str  # audio, video, llm
    configured: bool
    api_key_set: bool
    quota: list[QuotaInfo] = []
    capabilities: dict | None = None
    free_tier: bool = False
    availability: str = "unknown"  # available, unavailable, unknown


class ProviderConfigureRequest(BaseModel):
    """Request to configure a provider's API key."""
    api_key: str
    api_secret: str | None = None  # Some providers need both


class ProviderListResponse(BaseModel):
    """Grouped provider list for frontend."""
    audio: list[ProviderResponse] = []
    video: list[ProviderResponse] = []
    llm: list[ProviderResponse] = []
