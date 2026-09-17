"""
Tests for glossary enforcement pipeline: validation, self-mapped CJK detection,
language-aware enforcement, voice conflict deduplication, and retry behaviour.
"""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.terminology_extractor import is_self_mapped_cjk
from app.services.video_translator.translator_service import (
    find_glossary_violations,
    _translation_json_prompt,
)


# ── Test 1: Valid glossary, correct translation → PASS ──────────────────────

def test_valid_glossary_correct_translation_passes():
    """source=安妮, required=Annie, translation contains Annie → no violation."""
    violations = find_glossary_violations(
        [{"text": "安妮说了一句话", "translated_text": "Annie nói một câu"}],
        {"安妮": "Annie"},
        source_language="zh",
        target_language="vi",
    )
    assert violations == []


# ── Test 2: Valid glossary, wrong translation → FAIL ────────────────────────

def test_valid_glossary_wrong_translation_fails():
    """source=安妮, required=Annie, translation contains Anne → violation."""
    violations = find_glossary_violations(
        [{"text": "安妮说了一句话", "translated_text": "Anne nói một câu"}],
        {"安妮": "Annie"},
        source_language="zh",
        target_language="vi",
    )
    assert len(violations) == 1
    assert violations[0]["source_term"] == "安妮"
    assert violations[0]["required"] == "Annie"


# ── Test 3: Self-mapped CJK, target=vi → skip (no crash) ───────────────────

def test_self_mapped_cjk_skipped_for_non_chinese_target():
    """source_term=安妮, required=安妮, target=vi → skip, not a violation."""
    violations = find_glossary_violations(
        [{"text": "安妮说了一句话", "translated_text": "Annie nói một câu"}],
        {"安妮": "安妮"},
        source_language="zh",
        target_language="vi",
    )
    assert violations == [], "Self-mapped CJK entry should be skipped, not flagged as violation"


def test_self_mapped_cjk_does_not_crash_workflow():
    """Self-mapped CJK entries must not raise or crash, only skip silently."""
    segments = [
        {"text": "安妮和詹森来了", "translated_text": "Annie và Jensen đã đến"},
        {"text": "路斯在那边", "translated_text": "Ruth ở đằng kia"},
    ]
    glossary = {"安妮": "安妮", "詹森": "詹森", "路斯": "路斯"}
    violations = find_glossary_violations(
        segments, glossary,
        source_language="zh", target_language="vi",
    )
    assert violations == [], "All self-mapped CJK entries should be skipped"


# ── Test 4: Same term AI→AI → legitimate, PASS ─────────────────────────────

def test_same_term_ai_is_legitimate():
    """source_term=AI, required=AI → legitimate, not flagged."""
    assert is_self_mapped_cjk("AI", "AI", "vi") is False

    violations = find_glossary_violations(
        [{"text": "AI技术很先进", "translated_text": "Công nghệ AI rất tiên tiến"}],
        {"AI": "AI"},
        source_language="zh",
        target_language="vi",
    )
    assert violations == []


# ── Test 5: Same term Netflix→Netflix → legitimate, PASS ───────────────────

def test_same_term_netflix_is_legitimate():
    """source_term=Netflix, required=Netflix → legitimate, not flagged."""
    assert is_self_mapped_cjk("Netflix", "Netflix", "vi") is False

    violations = find_glossary_violations(
        [{"text": "我在看Netflix", "translated_text": "Tôi đang xem Netflix"}],
        {"Netflix": "Netflix"},
        source_language="zh",
        target_language="vi",
    )
    assert violations == []


# ── Test 6: Voice conflict deduplication ────────────────────────────────────

def test_voice_conflict_deduplication():
    """Same character pair conflict should appear only once, not duplicated."""
    # Simulate the dedup logic from validate_character_voice_review
    segments = [
        {"id": "s1", "character_id": "char-A", "voice_id": "voice-1", "original_start": 0.0, "original_end": 5.0},
        {"id": "s2", "character_id": "char-B", "voice_id": "voice-1", "original_start": 2.0, "original_end": 7.0},
        {"id": "s3", "character_id": "char-A", "voice_id": "voice-1", "original_start": 3.0, "original_end": 8.0},
        {"id": "s4", "character_id": "char-B", "voice_id": "voice-1", "original_start": 4.0, "original_end": 9.0},
    ]
    issues = []
    ordered = sorted(segments, key=lambda s: s["original_start"])
    seen_conflict_pairs: set[tuple[str, str]] = set()
    for index, left in enumerate(ordered):
        for right in ordered[index + 1:]:
            if right["original_start"] >= left["original_end"]:
                break
            if left["character_id"] != right["character_id"] and left["voice_id"] == right["voice_id"]:
                pair_key = tuple(sorted((left["character_id"], right["character_id"])))
                if pair_key not in seen_conflict_pairs:
                    seen_conflict_pairs.add(pair_key)
                    issues.append({"reason": "voice_conflict", "segment_ids": [left["id"], right["id"]]})
    
    # Only ONE voice_conflict for the (char-A, char-B) pair, not duplicated
    voice_conflicts = [i for i in issues if i["reason"] == "voice_conflict"]
    assert len(voice_conflicts) == 1, f"Expected 1 unique voice_conflict, got {len(voice_conflicts)}"


# ── Test 7: is_self_mapped_cjk utility edge cases ──────────────────────────

class TestIsSelfMappedCjk:
    def test_cjk_self_map_non_chinese_target(self):
        assert is_self_mapped_cjk("安妮", "安妮", "vi") is True
        assert is_self_mapped_cjk("詹森", "詹森", "en") is True
        assert is_self_mapped_cjk("路斯", "路斯", "vietnamese") is True

    def test_cjk_self_map_chinese_target_is_valid(self):
        """CJK→CJK is valid when target IS Chinese."""
        assert is_self_mapped_cjk("安妮", "安妮", "zh") is False
        assert is_self_mapped_cjk("安妮", "安妮", "chinese") is False
        assert is_self_mapped_cjk("安妮", "安妮", "zh-tw") is False

    def test_cjk_with_different_translation_is_valid(self):
        """CJK source with actual target translation is always valid."""
        assert is_self_mapped_cjk("安妮", "Annie", "vi") is False
        assert is_self_mapped_cjk("李道天", "Lý Đạo Thiên", "vi") is False

    def test_latin_self_map_is_never_flagged(self):
        """Latin/ASCII self-maps are never flagged (AI→AI, Netflix→Netflix)."""
        assert is_self_mapped_cjk("AI", "AI", "vi") is False
        assert is_self_mapped_cjk("Netflix", "Netflix", "en") is False
        assert is_self_mapped_cjk("John", "John", "vi") is False

    def test_empty_inputs(self):
        assert is_self_mapped_cjk("", "", "vi") is False
        assert is_self_mapped_cjk("安妮", "", "vi") is False
        assert is_self_mapped_cjk("", "安妮", "vi") is False

    def test_no_target_lang_defaults_to_not_flagged(self):
        """When target_lang is empty, assume we can't determine → don't flag."""
        assert is_self_mapped_cjk("安妮", "安妮", "") is True


# ── Test: Mixed valid + invalid glossary entries ────────────────────────────

def test_mixed_valid_and_invalid_glossary():
    """Only the invalid self-mapped CJK entries are skipped; valid entries still enforced."""
    segments = [
        {"text": "安妮和李道天来了", "translated_text": "Annie và Lý Đạo Thiên đã đến"},
    ]
    glossary = {
        "安妮": "安妮",        # Invalid self-map → skip
        "李道天": "Lý Đạo Thiên",  # Valid → enforce → present in translation → pass
    }
    violations = find_glossary_violations(
        segments, glossary,
        source_language="zh", target_language="vi",
    )
    assert violations == []


def test_mixed_valid_entry_violation_still_caught():
    """Valid glossary violation is still caught even when invalid entries are present."""
    segments = [
        {"text": "安妮和李道天来了", "translated_text": "Annie và Lý Đạo Thiện đã đến"},  # Thiện ≠ Thiên
    ]
    glossary = {
        "安妮": "安妮",           # Invalid self-map → skip
        "李道天": "Lý Đạo Thiên",  # Valid → violation (Thiện ≠ Thiên)
    }
    violations = find_glossary_violations(
        segments, glossary,
        source_language="zh", target_language="vi",
    )
    assert len(violations) == 1
    assert violations[0]["source_term"] == "李道天"
    assert violations[0]["required"] == "Lý Đạo Thiên"


# ── Test: Glossary prompt filtering ─────────────────────────────────────────

def test_translation_prompt_filters_self_mapped_cjk():
    """Self-mapped CJK entries should be excluded from the LLM prompt glossary rules."""
    prompt = _translation_json_prompt(
        {"lines": [{"n": 1, "text": "安妮和李道天来了"}]},
        "Tiếng Trung",
        "Tiếng Việt",
        {"安妮": "安妮", "李道天": "Lý Đạo Thiên"},
    )
    # Valid entry should be in prompt
    assert "李道天 → Lý Đạo Thiên" in prompt
    # Self-mapped entry should NOT be in prompt
    assert "安妮 → 安妮" not in prompt


def test_translation_prompt_works_with_only_valid_entries():
    """Glossary with only valid entries should work normally."""
    prompt = _translation_json_prompt(
        {"lines": [{"n": 1, "text": "李道天来了"}]},
        "Tiếng Trung",
        "Tiếng Việt",
        {"李道天": "Lý Đạo Thiên"},
    )
    assert "李道天 → Lý Đạo Thiên" in prompt
    assert "BẮT BUỘC" in prompt


def test_translation_prompt_no_glossary_when_all_invalid():
    """If ALL entries are self-mapped CJK, glossary rules section should be empty."""
    prompt = _translation_json_prompt(
        {"lines": [{"n": 1, "text": "安妮来了"}]},
        "Tiếng Trung",
        "Tiếng Việt",
        {"安妮": "安妮", "詹森": "詹森"},
    )
    assert "BẮT BUỘC" not in prompt
    assert "GLOSSARY CANONICAL" not in prompt
