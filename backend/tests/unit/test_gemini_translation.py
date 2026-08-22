"""
Unit tests for Gemini Translation and Output Length Mismatch Recovery.
Tests exact match, missing segment targeted recovery, over-length rejection,
malformed JSON, MAX_TOKENS finish reason truncation, empty text, and ID mismatch.
"""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.video_translator.translator_service import (
    _safe_parse_json_translation,
    _safe_parse_json_list,
    translate_transcript_segments,
)
from app.providers.base import LLMProvider


class MockLLM(LLMProvider):
    def __init__(self, responses=None):
        self.responses = responses or []
        self.call_count = 0
        self.prompts = []

    @property
    def provider_id(self) -> str:
        return "mock_gemini"

    @property
    def provider_name(self) -> str:
        return "Mock Gemini Provider"

    @property
    def is_free(self) -> bool:
        return True

    @property
    def requires_api_key(self) -> bool:
        return False

    async def validate_configuration(self) -> bool:
        return True

    async def generate_text(self, prompt: str, system_prompt: str = "") -> str:
        self.prompts.append(prompt)
        if self.call_count < len(self.responses):
            resp = self.responses[self.call_count]
            self.call_count += 1
            if isinstance(resp, Exception):
                raise resp
            return resp
        self.call_count += 1
        return "[]"

    async def estimate_usage(self, input_text: str):
        return []

    async def get_quota(self):
        return []


@pytest.mark.asyncio
async def test_1_gemini_exact_match():
    """Test 1: Input 30 segments -> Gemini returns 30 translated segments -> SUCCESS."""
    segments = [{"id": f"seg_{i}", "text": f"Original sentence {i}"} for i in range(30)]
    mock_resp = json.dumps([{"id": i, "translation": f"Bản dịch {i}"} for i in range(30)])
    mock_llm = MockLLM(responses=[mock_resp])

    with patch("app.services.video_translator.translator_service.get_registry") as mock_reg:
        reg_instance = MagicMock()
        reg_instance.get_llm.return_value = mock_llm
        mock_reg.return_value = reg_instance

        results = await translate_transcript_segments(
            segments=segments,
            source_language="en",
            target_language="vi",
            job_id="TEST-JOB-1",
            llm_provider_id="mock_gemini",
            batch_size=30,
        )

        assert len(results) == 30
        assert results[0]["translated_text"] == "Bản dịch 0"
        assert results[29]["translated_text"] == "Bản dịch 29"


@pytest.mark.asyncio
async def test_2_gemini_fewer_items_targeted_recovery():
    """Test 2: Input 30 segments -> Gemini returns 20 items -> Detect mismatch -> Targeted recovery -> SUCCESS."""
    segments = [{"id": f"seg_{i}", "text": f"Sentence {i}"} for i in range(30)]
    
    # First response returns only IDs 0..19 (missing 20..29)
    resp_partial = json.dumps([{"id": i, "translation": f"Dịch {i}"} for i in range(20)])
    # Recovery response returns missing IDs 20..29
    resp_recovery = json.dumps([{"id": i, "translation": f"Dịch recovered {i}"} for i in range(20, 30)])

    mock_llm = MockLLM(responses=[resp_partial, resp_recovery])

    with patch("app.services.video_translator.translator_service.get_registry") as mock_reg:
        reg_instance = MagicMock()
        reg_instance.get_llm.return_value = mock_llm
        mock_reg.return_value = reg_instance

        results = await translate_transcript_segments(
            segments=segments,
            source_language="en",
            target_language="vi",
            job_id="TEST-JOB-2",
            llm_provider_id="mock_gemini",
            batch_size=30,
        )

        assert len(results) == 30
        assert results[0]["translated_text"] == "Dịch 0"
        assert results[19]["translated_text"] == "Dịch 19"
        assert results[20]["translated_text"] == "Dịch recovered 20"
        assert results[29]["translated_text"] == "Dịch recovered 29"


@pytest.mark.asyncio
async def test_3_gemini_extra_items_rejection():
    """Test 3: Gemini returns 31 items for 30 inputs -> Ignore extra unknown IDs / Sub-batch fallback."""
    segments = [{"id": f"seg_{i}", "text": f"Sentence {i}"} for i in range(5)]
    # Returns IDs 0..5 (6 items instead of 5)
    resp_extra = json.dumps([{"id": i, "translation": f"Dịch {i}"} for i in range(6)])
    # Sub-batch returns correct 5
    resp_correct = json.dumps([{"id": i, "translation": f"Dịch sub {i}"} for i in range(5)])

    mock_llm = MockLLM(responses=[resp_extra, resp_extra, resp_correct])

    with patch("app.services.video_translator.translator_service.get_registry") as mock_reg:
        reg_instance = MagicMock()
        reg_instance.get_llm.return_value = mock_llm
        mock_reg.return_value = reg_instance

        results = await translate_transcript_segments(
            segments=segments,
            source_language="en",
            target_language="vi",
            job_id="TEST-JOB-3",
            llm_provider_id="mock_gemini",
            batch_size=5,
        )

        assert len(results) == 5
        assert results[0]["translated_text"] == "Dịch 0"
        assert results[4]["translated_text"] == "Dịch 4"


def test_4_gemini_malformed_json_parsing():
    """Test 4: Gemini outputs markdown wrapped or dirty JSON -> Parser clean recovery."""
    raw_dirty = """
    ```json
    [
      {"id": 0, "translation": "Câu 1"},
      {"id": 1, "translation": "Câu 2"}
    ]
    ```
    """
    parsed = _safe_parse_json_translation(raw_dirty)
    assert parsed == {0: "Câu 1", 1: "Câu 2"}

    # Test plain list fallback
    raw_list = '["Dịch A", "Dịch B"]'
    parsed_list = _safe_parse_json_list(raw_list)
    assert parsed_list == ["Dịch A", "Dịch B"]


@pytest.mark.asyncio
async def test_5_gemini_max_tokens_truncation_recovery():
    """Test 5: Response truncated mid-JSON -> Triggers sub-batch fallback -> Complete success."""
    segments = [{"id": f"seg_{i}", "text": f"Sentence {i}"} for i in range(10)]
    
    truncated_resp = RuntimeError("Gemini API output truncated due to MAX_TOKENS limit on model 'gemini-3.5-flash'.")
    resp_part1 = json.dumps([{"id": i, "translation": f"Dịch p1-{i}"} for i in range(5)])
    resp_part2 = json.dumps([{"id": i, "translation": f"Dịch p2-{i}"} for i in range(5)])

    mock_llm = MockLLM(responses=[truncated_resp, truncated_resp, resp_part1, resp_part2])

    with patch("app.services.video_translator.translator_service.get_registry") as mock_reg:
        reg_instance = MagicMock()
        reg_instance.get_llm.return_value = mock_llm
        mock_reg.return_value = reg_instance

        results = await translate_transcript_segments(
            segments=segments,
            source_language="en",
            target_language="vi",
            job_id="TEST-JOB-5",
            llm_provider_id="mock_gemini",
            batch_size=10,
        )

        assert len(results) == 10
        assert results[0]["translated_text"] == "Dịch p1-0"
        assert results[5]["translated_text"] == "Dịch p2-0"


@pytest.mark.asyncio
async def test_6_empty_translation_preservation():
    """Test 6: Segment with empty/short text is preserved and not silently dropped."""
    segments = [
        {"id": "seg_0", "text": "Hello"},
        {"id": "seg_1", "text": ""},
        {"id": "seg_2", "text": "Goodbye"},
    ]
    resp = json.dumps([
        {"id": 0, "translation": "Xin chào"},
        {"id": 1, "translation": ""},
        {"id": 2, "translation": "Tạm biệt"},
    ])
    mock_llm = MockLLM(responses=[resp])

    with patch("app.services.video_translator.translator_service.get_registry") as mock_reg:
        reg_instance = MagicMock()
        reg_instance.get_llm.return_value = mock_llm
        mock_reg.return_value = reg_instance

        results = await translate_transcript_segments(
            segments=segments,
            source_language="en",
            target_language="vi",
            job_id="TEST-JOB-6",
            llm_provider_id="mock_gemini",
            batch_size=3,
        )

        assert len(results) == 3
        assert results[1]["translated_text"] == ""


@pytest.mark.asyncio
async def test_7_segment_id_mismatch_detection():
    """Test 7: Model returns wrong IDs -> Detected and recovered via targeted retry."""
    segments = [{"id": f"seg_{i}", "text": f"Sentence {i}"} for i in range(4)]
    # Returns IDs 0, 1, 99 (invalid), 3 (missing ID 2)
    resp_bad = json.dumps([
        {"id": 0, "translation": "Dịch 0"},
        {"id": 1, "translation": "Dịch 1"},
        {"id": 99, "translation": "Dịch 99"},
        {"id": 3, "translation": "Dịch 3"},
    ])
    # Recovery returns missing ID 2
    resp_rec = json.dumps([{"id": 2, "translation": "Dịch 2 recovered"}])

    mock_llm = MockLLM(responses=[resp_bad, resp_rec])

    with patch("app.services.video_translator.translator_service.get_registry") as mock_reg:
        reg_instance = MagicMock()
        reg_instance.get_llm.return_value = mock_llm
        mock_reg.return_value = reg_instance

        results = await translate_transcript_segments(
            segments=segments,
            source_language="en",
            target_language="vi",
            job_id="TEST-JOB-7",
            llm_provider_id="mock_gemini",
            batch_size=4,
        )

        assert len(results) == 4
        assert results[2]["translated_text"] == "Dịch 2 recovered"


@pytest.mark.asyncio
async def test_8_full_workflow_end_to_end_preservation():
    """Test 8: Full end-to-end 49-segment transcript dataset preservation."""
    segments = [
        {"id": f"s_{i}", "segment_number": i + 1, "start_time": float(i * 3), "end_time": float((i + 1) * 3), "text": f"Original dialogue segment {i+1}"}
        for i in range(49)
    ]
    # Batch 1 (30 items)
    batch1_resp = json.dumps([{"id": i, "translation": f"Bản dịch b1-{i+1}"} for i in range(30)])
    # Batch 2 (19 items)
    batch2_resp = json.dumps([{"id": i, "translation": f"Bản dịch b2-{i+1}"} for i in range(19)])

    mock_llm = MockLLM(responses=[batch1_resp, batch2_resp])

    with patch("app.services.video_translator.translator_service.get_registry") as mock_reg:
        reg_instance = MagicMock()
        reg_instance.get_llm.return_value = mock_llm
        mock_reg.return_value = reg_instance

        results = await translate_transcript_segments(
            segments=segments,
            source_language="en",
            target_language="vi",
            job_id="TEST-JOB-8",
            llm_provider_id="mock_gemini",
            batch_size=30,
        )

        assert len(results) == 49
        # Verify timestamps, IDs, and order remain completely unchanged
        for idx, seg in enumerate(results):
            assert seg["segment_number"] == idx + 1
            assert seg["start_time"] == float(idx * 3)
            assert seg["end_time"] == float((idx + 1) * 3)
            assert "translated_text" in seg
            assert seg["translated_text"] != ""
