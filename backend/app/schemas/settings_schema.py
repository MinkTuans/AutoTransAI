"""
Pydantic Schemas for Settings and AI Provider Management endpoints.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SystemSettingsUpdateRequest(BaseModel):
    settings: Dict[str, Any] = Field(..., description="Key-value dictionary of settings to update")


class AIFunctionConfigUpdateRequest(BaseModel):
    primary_provider_id: Optional[str] = None
    model_id: Optional[str] = None
    fallback_enabled: Optional[bool] = None
    fallback_provider_id: Optional[str] = None


class AddCustomModelRequest(BaseModel):
    id: Optional[str] = None
    provider_id: str
    model_name: str
    capabilities: List[str] = Field(default_factory=lambda: ["LLM"])
    is_default: bool = False
    description: Optional[str] = None


class UpdateAIModelRequest(BaseModel):
    provider_id: Optional[str] = None
    model_name: Optional[str] = None
    capabilities: Optional[List[str]] = None
    is_default: Optional[bool] = None
    enabled: Optional[bool] = None
    description: Optional[str] = None



class AddCustomProviderRequest(BaseModel):
    id: str
    name: str
    provider_type: str = "llm"  # llm, audio, video
    website_url: Optional[str] = None
    doc_url: Optional[str] = None
    base_url: Optional[str] = None
    capabilities: List[str] = Field(default_factory=lambda: ["LLM"])
    api_key: Optional[str] = None


class AddSocialAccountRequest(BaseModel):
    platform: str  # youtube, tiktok, facebook, instagram
    account_name: str
    channel_id: Optional[str] = None
    channel_name: Optional[str] = None
    priority: int = 1


class TestStorageRequest(BaseModel):
    storage_provider: str = "supabase"
    supabase_url: Optional[str] = None
    supabase_service_role_key: Optional[str] = None
    supabase_bucket_private: str = "autotransai-private"
    supabase_bucket_public: str = "autotransai-public"
