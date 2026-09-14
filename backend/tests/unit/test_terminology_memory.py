"""Tests for AI Auto Terminology Memory extraction and persistence helpers."""

import pytest

from app.services.terminology_memory import (
    extract_and_persist_from_segments,
    heuristic_extract_terms,
    normalize_extracted_terms,
)


@pytest.mark.asyncio
async def test_extract_and_persist_from_segments_saves_heuristic_terms(monkeypatch):
    saved = []

    async def fake_llm(*_a, **_k):
        return []

    async def fake_persist(_db, project_id, terms):
        assert project_id == "proj-1"
        saved.extend(terms)
        return len(terms)

    monkeypatch.setattr(
        "app.services.terminology_memory.llm_extract_terms",
        fake_llm,
    )
    monkeypatch.setattr(
        "app.services.terminology_memory.persist_terminology_memory",
        fake_persist,
    )
    n = await extract_and_persist_from_segments(
        object(),
        "proj-1",
        [{"text": "张三来了。张三走了。青云城很大。青云城。"}],
        "vi",
    )
    assert n >= 1
    sources = {t["source_term"] for t in saved}
    assert "张三" in sources
    assert "青云城" in sources


def test_heuristic_extracts_repeated_cjk_names():
    text = "张三走进青云城。张三遇见李四。青云城很大。李四离开青云城。"
    terms = heuristic_extract_terms(text, target_lang="vi")
    sources = {t["source_term"] for t in terms}
    assert "张三" in sources
    assert "青云城" in sources
    assert "李四" in sources


def test_heuristic_keeps_long_cjk_name_even_once():
    terms = heuristic_extract_terms("青云城很大。", target_lang="vi")
    sources = {t["source_term"] for t in terms}
    assert "青云城" in sources


def test_segments_transcript_blob_joins_original_and_text():
    from app.services.terminology_memory import segments_transcript_blob

    blob = segments_transcript_blob(
        [
            {"text": "张三来了。"},
            {"original_text": "张三走了。青云城。"},
        ]
    )
    assert "张三来了" in blob
    assert "青云城" in blob


def test_normalize_extracted_terms_dedupes_and_drops_short():
    terms = normalize_extracted_terms(
        [
            {"source_term": "张三", "suggested_term": "Trương Tam", "term_type": "character"},
            {"source_term": " 张三 ", "suggested_term": "Trương Tam", "term_type": "character"},
            {"source_term": "a", "suggested_term": "a"},
        ]
    )
    assert len(terms) == 1
    assert terms[0]["source_term"] == "张三"
    assert terms[0]["suggested_term"] == "Trương Tam"
