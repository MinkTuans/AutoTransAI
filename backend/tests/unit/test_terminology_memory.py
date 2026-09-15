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


def test_heuristic_drops_cjk_sentence_fragments_not_proper_names():
    """Studio screenshot: Auto Memory filled with Other 60% clauses, not names."""
    text = (
        "做异度。看来今天。我先走了。贪主努。都最佳状。"
        "开始融合。涌出了无。只是想给。和我还。你叫什麼。"
        "姜男来了。姜男走了。"
    )
    terms = heuristic_extract_terms(text, target_lang="vi")
    sources = {t["source_term"] for t in terms}
    assert "姜男" in sources
    junk = {
        "做异度", "看来今天", "我先走了", "贪主努", "都最佳状",
        "开始融合", "涌出了无", "只是想给", "和我还", "你叫什麼",
    }
    assert sources.isdisjoint(junk)
    assert all(t["term_type"] in {"character", "location", "organization"} for t in terms)


def test_filter_proper_names_keeps_khương_nam_drops_other_phrases():
    from app.services.terminology_memory import filter_proper_names

    kept = filter_proper_names(
        [
            {"source_term": "姜男", "suggested_term": "Khương Nam", "term_type": "character", "confidence": 0.9},
            {"source_term": "看来今天", "suggested_term": "看来今天", "term_type": "other", "confidence": 0.6},
            {"source_term": "我先走了", "suggested_term": "我先走了", "term_type": "other", "confidence": 0.6},
            {"source_term": "青云城", "suggested_term": "Thanh Vân Thành", "term_type": "location", "confidence": 0.88},
        ]
    )
    sources = {t["source_term"] for t in kept}
    assert sources == {"姜男", "青云城"}


def test_filter_keeps_ly_phi_vu_drops_verbs_and_common_nouns():
    """Second Studio screenshot: 李飞羽 is a name; 爬上/弟子/哥哥/而且門派 are not."""
    from app.services.terminology_memory import filter_proper_names

    kept = filter_proper_names(
        [
            {"source_term": "李飞羽", "suggested_term": "Lý Phi Vũ", "term_type": "character", "confidence": 0.9},
            {"source_term": "基途河", "suggested_term": "基途河", "term_type": "location", "confidence": 0.75},
            {"source_term": "Hàn Lực", "suggested_term": "Hàn Lực", "term_type": "character", "confidence": 0.75},
            {"source_term": "冰發", "suggested_term": "冰發", "term_type": "character", "confidence": 0.65},
            {"source_term": "而且門派", "suggested_term": "而且門派", "term_type": "location", "confidence": 0.75},
            {"source_term": "爬上", "suggested_term": "爬上", "term_type": "character", "confidence": 0.65},
            {"source_term": "弟子", "suggested_term": "弟子", "term_type": "character", "confidence": 0.65},
            {"source_term": "山门", "suggested_term": "山门", "term_type": "location", "confidence": 0.75},
            {"source_term": "哥哥", "suggested_term": "哥哥", "term_type": "character", "confidence": 0.7},
            {"source_term": "人心", "suggested_term": "人心", "term_type": "character", "confidence": 0.65},
            {"source_term": "究冰", "suggested_term": "究冰", "term_type": "character", "confidence": 0.65},
            {"source_term": "上车", "suggested_term": "上车", "term_type": "character", "confidence": 0.65},
        ]
    )
    sources = {t["source_term"] for t in kept}
    assert "李飞羽" in sources
    assert "基途河" in sources
    assert "Hàn Lực" in sources
    junk = {"冰發", "而且門派", "爬上", "弟子", "山门", "哥哥", "人心", "究冰", "上车"}
    assert sources.isdisjoint(junk)


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


def test_segments_transcript_blob_includes_translated_text_even_when_source_exists():
    from app.services.terminology_memory import segments_transcript_blob

    blob = segments_transcript_blob(
        [
            {
                "text": "李逍遥走进青云城。",
                "translated_text": "Lý Tiêu Dao bước vào Thanh Vân Thành.",
            }
        ]
    )
    assert "李逍遥" in blob
    assert "Lý Tiêu Dao" in blob
    assert "Thanh Vân Thành" in blob


def test_heuristic_extracts_vietnamese_proper_names_once():
    text = "Lý Tiêu Dao bước vào Thanh Vân Thành. Hắn gặp Lâm Nguyệt Như."
    terms = heuristic_extract_terms(text, target_lang="vi")
    sources = {t["source_term"] for t in terms}
    assert "Lý Tiêu Dao" in sources
    assert "Thanh Vân Thành" in sources
    assert "Lâm Nguyệt Như" in sources
    assert "Hắn" not in sources


def test_heuristic_extracts_single_latin_full_name():
    terms = heuristic_extract_terms("John Smith entered the hall.", target_lang="en")
    sources = {t["source_term"] for t in terms}
    assert "John Smith" in sources


@pytest.mark.asyncio
async def test_extract_persists_names_from_translation_when_llm_empty(monkeypatch):
    saved = []

    async def fake_llm(*_a, **_k):
        return []

    async def fake_persist(_db, project_id, terms):
        saved.extend(terms)
        return len(terms)

    monkeypatch.setattr("app.services.terminology_memory.llm_extract_terms", fake_llm)
    monkeypatch.setattr("app.services.terminology_memory.persist_terminology_memory", fake_persist)

    n = await extract_and_persist_from_segments(
        object(),
        "proj-1",
        [
            {
                "text": "李逍遥走进青云城。",
                "translated_text": "Lý Tiêu Dao bước vào Thanh Vân Thành.",
            }
        ],
        "vi",
    )
    assert n >= 1
    sources = {t["source_term"] for t in saved}
    suggested = {t["suggested_term"] for t in saved}
    assert "Lý Tiêu Dao" in sources or "Lý Tiêu Dao" in suggested
    assert "Thanh Vân Thành" in sources or "Thanh Vân Thành" in suggested


def test_normalize_accepts_llm_name_translation_aliases():
    terms = normalize_extracted_terms(
        [
            {"name": "李逍遥", "translation": "Lý Tiêu Dao", "term_type": "character"},
        ]
    )
    assert len(terms) == 1
    assert terms[0]["source_term"] == "李逍遥"
    assert terms[0]["suggested_term"] == "Lý Tiêu Dao"


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
