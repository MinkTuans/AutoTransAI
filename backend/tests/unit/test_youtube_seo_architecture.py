"""
Unit tests for YouTube & SEO Architecture — Default Templates, AI SEO Generator, Tag Merging Engine,
Episode Calculation, and Project Settings Normalization.
"""

import pytest
from app.api.routes.projects import normalize_project_settings, DEFAULT_PROJECT_SETTINGS
from app.services.video_editor.youtube_service import (
    merge_youtube_tags,
    render_title_template,
    calculate_project_video_episode,
    YouTubePublishingService,
)


def test_project_settings_youtube_defaults():
    """Verify DEFAULT_PROJECT_SETTINGS and normalize_project_settings include all YouTube SEO keys."""
    norm = normalize_project_settings({})
    assert norm["youtube_enabled"] is True
    assert norm["youtube_channel_name"] == "Xói Xám Content"
    assert norm["youtube_title_template"] == "Tập {episode} | {project_name} | {channel_name}"
    assert "Kênh Xói Xám Content" in norm["youtube_description_default"]
    assert "#xoiXamContent" in norm["youtube_default_tags"]
    assert norm["youtube_ai_seo_enabled"] is True
    assert norm["youtube_ai_allow_title"] is True
    assert norm["youtube_ai_allow_description"] is True
    assert norm["youtube_ai_allow_tags"] is True


def test_tag_merge_engine_case_insensitive_and_deduplication():
    """Test merge_youtube_tags for case-insensitivity, deduplication, and whitespace normalization."""
    default_tags = "#xoiXamContent, #ai, #dichvideo"
    ai_tags = ["#ai", "#AI", "#translation", "#dubbed", "#dichvideo"]

    merged = merge_youtube_tags(default_tags, ai_tags)
    
    # Must preserve default tags order
    assert merged[0] == "#xoiXamContent"
    assert merged[1] == "#ai"
    assert merged[2] == "#dichvideo"

    # Case-insensitive duplicate detection: '#AI' and '#ai' and '#dichvideo' should not duplicate
    lower_merged = [t.lower() for t in merged]
    assert len(lower_merged) == len(set(lower_merged))

    # Must contain AI additions
    assert "#translation" in merged
    assert "#dubbed" in merged


def test_tag_merge_engine_empty_or_malformed():
    """Test tag merge engine with empty AI tags or malformed inputs."""
    def_tags = "#channel, #tech"
    assert merge_youtube_tags(def_tags, []) == ["#channel", "#tech"]
    assert merge_youtube_tags(def_tags, None) == ["#channel", "#tech"]
    assert merge_youtube_tags("", ["#ai"]) == ["#ai"]


def test_render_title_template():
    """Test title template rendering with episode 2-digit padding and variable replacement."""
    template = "Tập {episode} | {project_name} | {channel_name}"
    rendered = render_title_template(
        template=template,
        episode_num=1,
        project_name="Dragon Travel",
        channel_name="Xói Xám Content",
    )
    assert rendered == "Tập 01 | Dragon Travel | Xói Xám Content"

    rendered_ep10 = render_title_template(
        template=template,
        episode_num=10,
        project_name="Dragon Travel",
        channel_name="Xói Xám Content",
    )
    assert rendered_ep10 == "Tập 10 | Dragon Travel | Xói Xám Content"


def test_render_title_template_custom_variables():
    """Test title template with video_name variable."""
    template = "{project_name} - {video_name} (Tập {episode})"
    rendered = render_title_template(
        template=template,
        episode_num=3,
        project_name="Phim Hành Động",
        channel_name="Kênh Phim",
        video_name="Trận Chiến Cuối",
    )
    assert rendered == "Phim Hành Động - Trận Chiến Cuối (Tập 03)"


@pytest.mark.asyncio
async def test_youtube_seo_metadata_merge_defaults():
    """Test generate_youtube_seo_metadata preserves project defaults and merges AI output."""
    project_settings = {
        "youtube_enabled": True,
        "youtube_channel_name": "TestChannel",
        "youtube_title_template": "Tập {episode} | {project_name} | {channel_name}",
        "youtube_description_default": "Mô tả mặc định của kênh TestChannel.",
        "youtube_default_tags": "#testChannel, #defaultTag",
        "youtube_ai_seo_enabled": True,
        "youtube_ai_allow_title": True,
        "youtube_ai_allow_description": True,
        "youtube_ai_allow_tags": True,
    }

    meta = await YouTubePublishingService.generate_youtube_seo_metadata(
        transcript_text="Đây là transcript thử nghiệm nội dung video.",
        target_language="vi",
        job_id="JOB-123",
        project_settings=project_settings,
        project_name="Dự Án Thử Nghiệm",
        video_name="Video 1",
        episode_num=1,
    )

    # Title must respect template
    assert meta["title"] == "Tập 01 | Dự Án Thử Nghiệm | TestChannel"
    
    # Description must retain default description
    assert "Mô tả mặc định của kênh TestChannel." in meta["description"]

    # Tags must retain default tags
    assert "#testChannel" in meta["tags"]
    assert "#defaultTag" in meta["tags"]
