"""
Unit tests for OpenAILLMProvider.
"""

import pytest
from app.providers.llm.openai_provider import OpenAILLMProvider
from app.providers.registry import get_registry


def test_openai_provider_registration():
    registry = get_registry()
    provider = registry.get_llm("openai")
    assert provider is not None
    assert provider.provider_id == "openai"
    assert provider.provider_name == "OpenAI ChatGPT"
    assert provider.requires_api_key is True
    assert provider.is_free is False


@pytest.mark.asyncio
async def test_openai_provider_validation_without_key(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "")
    from app.config import get_settings
    monkeypatch.setattr(get_settings(), "OPENAI_API_KEY", "")

    provider = OpenAILLMProvider()
    is_valid = await provider.validate_configuration()
    assert is_valid is False


@pytest.mark.asyncio
async def test_openai_generate_text_without_key(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "")
    from app.config import get_settings
    monkeypatch.setattr(get_settings(), "OPENAI_API_KEY", "")

    provider = OpenAILLMProvider()
    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        await provider.generate_text("Hello")
