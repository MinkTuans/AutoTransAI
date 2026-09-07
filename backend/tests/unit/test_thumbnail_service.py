"""
Unit tests for AI Auto Thumbnail Generation feature.
"""

import pytest
import asyncio
import uuid
import json
from pathlib import Path
from unittest.mock import AsyncMock, patch

from app.models.video_thumbnail import VideoThumbnail, ThumbnailStatus
from app.models.project import Project
from app.models.video_translator import VideoAsset, VideoTranslationJob, VideoTranslationSegment
from app.providers.base import GenerationResult
from app.providers.image.pollinations_provider import PollinationsImageProvider
from app.providers.image.fal_image_provider import FalImageProvider
from app.providers.image.openai_image_provider import OpenAIImageProvider
from app.providers.image.local_image_provider import LocalImageProvider
from app.providers.registry import get_registry
from app.services.thumbnail_service import ThumbnailService
from app.database import async_session_factory, init_db, engine as db_engine


@pytest.mark.asyncio
async def test_clean_and_chunk_transcript():
    raw_text = """
    Line 1: Frightened woman in abandoned house.
    
    Line 2: A shadow moves across the dark hallway.
    """
    cleaned = ThumbnailService.clean_transcript(raw_text)
    assert "Frightened woman" in cleaned
    assert "\n" not in cleaned

    chunks = ThumbnailService.chunk_transcript(cleaned, chunk_size=30)
    assert len(chunks) >= 2


@pytest.mark.asyncio
async def test_generate_image_prompt():
    analysis = {
        "title": "Haunted House Discovery",
        "main_subject": "Frightened young woman",
        "main_character": "Woman holding lantern",
        "main_event": "Sees mysterious shadow",
        "emotion": "Suspense and fear",
        "environment": "Dark abandoned hallway",
        "thumbnail_hook": "Shadow lurking behind woman",
    }

    # Test cinematic style
    prompt_cinematic = ThumbnailService.generate_image_prompt(analysis, selected_style="cinematic")
    assert "Frightened young woman" in prompt_cinematic
    assert "Dramatic cinematic lighting" in prompt_cinematic
    assert "16:9 aspect ratio" in prompt_cinematic
    assert "No text" in prompt_cinematic

    # Test horror style with custom instruction
    prompt_horror = ThumbnailService.generate_image_prompt(
        analysis,
        selected_style="horror",
        custom_instruction="Use intense red and dark blue lighting.",
    )
    assert "Dark eerie atmospheric horror scene" in prompt_horror
    assert "Use intense red and dark blue lighting" in prompt_horror


@pytest.mark.asyncio
async def test_image_provider_registry():
    reg = get_registry()
    pollinations = reg.get_image("pollinations")
    fal_img = reg.get_image("fal")
    openai_img = reg.get_image("openai")
    local_img = reg.get_image("local_image")

    assert pollinations is not None
    assert pollinations.provider_id == "pollinations"
    assert pollinations.is_free is True

    assert fal_img is not None
    assert fal_img.provider_id == "fal"

    assert openai_img is not None
    assert openai_img.provider_id == "openai"

    assert local_img is not None
    assert local_img.provider_id == "local_image"


@pytest.mark.asyncio
async def test_local_image_provider_generation():
    provider = LocalImageProvider()
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.content = b"x" * 6000
        mock_get.return_value = mock_response

        res = await provider.generate_image(
            prompt="Cinematic zombie scene",
            width=1280,
            height=720,
        )
        assert res.success is True
        assert res.metadata.get("image_bytes") is not None
        assert len(res.metadata["image_bytes"]) > 1000



@pytest.mark.asyncio
async def test_create_and_delete_thumbnail_db_flow():
    await init_db()

    async with async_session_factory() as session:
        project_id = f"test_thumb_p_{uuid.uuid4().hex[:8]}"
        proj = Project(id=project_id, title="Test Horror Movie", script_raw="A creepy shadow stalks a girl in a dark house.")
        session.add(proj)
        await session.commit()

        # Mock storage upload, image provider, and LLM analysis to avoid external network calls during unit test
        with patch("app.services.storage_service.storage_service.upload_file", new_callable=AsyncMock) as mock_upload, \
             patch("app.providers.image.pollinations_provider.PollinationsImageProvider.generate_image", new_callable=AsyncMock) as mock_gen, \
             patch("app.services.thumbnail_service.ThumbnailService.analyze_content_with_llm", new_callable=AsyncMock) as mock_analyze:

            mock_upload.return_value = (f"projects/{project_id}/thumbnails/test.webp", f"/api/storage/files/projects/{project_id}/thumbnails/test.webp")
            mock_analyze.return_value = {
                "title": "Test Horror Movie",
                "main_subject": "Girl in dark house",
                "main_character": "Girl",
                "main_event": "Shadow stalks girl",
                "emotion": "Fear",
                "environment": "Dark house",
                "important_visual_elements": ["Shadow"],
                "thumbnail_hook": "Creepy shadow stalking girl",
            }
            mock_gen.return_value = GenerationResult(
                success=True,
                provider_id="pollinations",
                metadata={
                    "image_bytes": b"mock_image_bytes_content_for_test",
                    "width": 1280,
                    "height": 720,
                    "aspect_ratio": "16:9",
                    "provider": "pollinations",
                    "model": "default",
                },
            )

            record = await ThumbnailService.create_thumbnail(
                db=session,
                project_id=project_id,
                selected_style="horror",
                custom_instruction="Make atmosphere gloomy",
            )



            assert record is not None
            assert record.project_id == project_id
            assert record.status == ThumbnailStatus.COMPLETED.value
            assert record.is_active is True
            assert record.thumbnail_url is not None
            assert "horror" in record.selected_style

            # Test deletion
            thumb_id = record.id
            deleted = await ThumbnailService.delete_thumbnail(session, thumb_id)
            assert deleted is True

    await db_engine.dispose()
