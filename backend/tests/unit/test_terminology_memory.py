"""Tests for AI Auto Terminology Memory extraction and persistence helpers."""

from app.services.terminology_memory import heuristic_extract_terms, normalize_extracted_terms


def test_heuristic_extracts_repeated_cjk_names():
    text = "张三走进青云城。张三遇见李四。青云城很大。李四离开青云城。"
    terms = heuristic_extract_terms(text, target_lang="vi")
    sources = {t["source_term"] for t in terms}
    assert "张三" in sources
    assert "青云城" in sources
    assert "李四" in sources


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
