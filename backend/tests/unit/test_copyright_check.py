"""Unit tests for INGEST copyright risk scoring (no LLM)."""

import pytest

from app.services.video_translator.copyright_check import (
    merge_copyright_report,
    parse_acoustid_payload,
    run_copyright_check,
    score_metadata,
)


def test_youtube_licensed_content_is_red():
    report = score_metadata(
        {
            "title": "Official clip",
            "duration": 180,
            "licensedContent": True,
            "domain": "www.youtube.com",
        }
    )
    assert report["level"] == "red"
    assert report["reasons"]


def test_bilibili_repost_short_clip_is_yellow():
    report = score_metadata(
        {
            "title": "日常vlog",
            "duration": 240,
            "copyright": 2,
            "domain": "www.bilibili.com",
        }
    )
    assert report["level"] == "yellow"
    assert any("转载" in r or "chuyển tải" in r.lower() or "repost" in r.lower() for r in report["reasons"])


def test_full_movie_title_and_long_duration_is_red():
    report = score_metadata({"title": "某某电影完整版", "duration": 5400})
    assert report["level"] == "red"


def test_tv_full_episode_keywords_is_red():
    report = score_metadata({"title": "电视剧第12集全集", "duration": 2700, "tname": "电视剧"})
    assert report["level"] == "red"


def test_original_short_upload_is_green():
    report = score_metadata(
        {
            "title": "今天做饭",
            "duration": 300,
            "copyright": 1,
            "licensedContent": False,
        }
    )
    assert report["level"] == "green"
    assert report["reasons"] == []


def test_creative_commons_youtube_is_not_red():
    report = score_metadata(
        {
            "title": "My lecture",
            "duration": 600,
            "license": "creativeCommon",
            "licensedContent": False,
        }
    )
    assert report["level"] != "red"


def test_parse_acoustid_high_score_recording():
    hits = parse_acoustid_payload(
        {
            "status": "ok",
            "results": [
                {
                    "score": 0.92,
                    "recordings": [
                        {"title": "Canon in D", "artists": [{"name": "Pachelbel"}]}
                    ],
                }
            ],
        }
    )
    assert hits
    assert hits[0]["title"] == "Canon in D"
    assert hits[0]["artist"] == "Pachelbel"
    assert hits[0]["score"] == pytest.approx(0.92)


def test_acoustid_hit_raises_merged_report_to_red():
    meta = score_metadata({"title": "vlog", "duration": 120, "copyright": 1})
    hits = parse_acoustid_payload(
        {
            "status": "ok",
            "results": [
                {
                    "score": 0.88,
                    "recordings": [{"title": "Theme", "artists": [{"name": "Studio"}]}],
                }
            ],
        }
    )
    report = merge_copyright_report(meta, hits)
    assert report["level"] == "red"
    assert any("Theme" in r for r in report["reasons"])


def test_low_acoustid_score_ignored():
    hits = parse_acoustid_payload(
        {"status": "ok", "results": [{"score": 0.2, "recordings": [{"title": "Noise"}]}]}
    )
    assert hits == []


@pytest.mark.asyncio
async def test_run_copyright_check_disabled_is_skipped():
    report = await run_copyright_check(
        metadata={"title": "电影完整版", "duration": 5400},
        audio_path=None,
        enabled=False,
    )
    assert report["level"] == "skipped"
    assert report["enabled"] is False
