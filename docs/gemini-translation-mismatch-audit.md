# Gemini Translation — Output Length Mismatch Root Cause & Audit Report

**Date**: 2026-08-22  
**Project**: WorkflowVdAi  
**Issue**: `RuntimeError: TRANSLATION FAILED: [Google Gemini AI Studio (gemini)] LLM translation failed for batch 2/15 on Google Gemini AI Studio: Output length mismatch: expected 30, got 20`

---

## 1. Flow Trace & Component Mapping

The video transcript translation pipeline follows these exact steps across the codebase:

```text
Original Transcript
       ↓
STT & Segmentation (sync_service.py / translator_service.py)
       ↓
translate_transcript_segments() (translator_service.py:681)
       ↓
Batching Loop (batch_size = 30) (translator_service.py:764)
       ↓
Batch 2 Slicing (segments[30:60], len = 30)
       ↓
Prompt Construction (translator_service.py:770)
       ↓
GeminiLLMProvider.generate_text() (gemini_provider.py:67)
       ↓
Google Gemini API (https://generativelanguage.googleapis.com/v1beta/models/...)
       ↓
Raw API Response JSON
       ↓
Response Parsing: _safe_parse_json_list() (translator_service.py:649)
       ↓
Length & Verbatim Validation (translator_service.py:788, 801, 828)
       ↓
Translated Segments Mapping (seg["translated_text"] = trans)
```

### Component Code Mapping
- **Entry Point**: `translate_transcript_segments()` in [`translator_service.py`](file:///c:/Hack/WorkflowVdAi/backend/app/services/video_translator/translator_service.py#L681)
- **LLM Interface**: `LLMProvider` in [`base.py`](file:///c:/Hack/WorkflowVdAi/backend/app/providers/base.py#L193)
- **Gemini Implementation**: `GeminiLLMProvider` in [`gemini_provider.py`](file:///c:/Hack/WorkflowVdAi/backend/app/providers/llm/gemini_provider.py#L36)
- **JSON Parser**: `_safe_parse_json_list()` in [`translator_service.py`](file:///c:/Hack/WorkflowVdAi/backend/app/services/video_translator/translator_service.py#L649)
- **Audit Logger**: `log_job_event()` in [`job_logger.py`](file:///c:/Hack/WorkflowVdAi/backend/app/core/job_logger.py#L22)

---

## 2. Comprehensive Root Cause Audit Answers

### Q1: Input 30 segments nằm ở đâu?
- **Answer**: In `translate_transcript_segments()`, `segments` is sliced into batches: `batch_segments = segments[start_i:end_i]` where `batch_size = 30`. For Batch 2 (`batch_idx = 1`), `segments[30:60]` contains 30 segment objects (index 30 through 59).

### Q2: Gemini thực sự nhận bao nhiêu segment?
- **Answer**: Gemini receives all 30 string items serialized into a JSON array string `["text 1", "text 2", ..., "text 30"]` embedded inside the prompt string.

### Q3: Gemini thực sự trả bao nhiêu item?
- **Answer**: Gemini actually returned 20 translated string items in its output array when it combined contiguous character sentences or dropped empty/short lines.

### Q4: Raw response có bao nhiêu item?
- **Answer**: The raw response string produced by Gemini contained 20 JSON string elements.

### Q5: Parser có làm mất item không?
- **Answer**: In cases where JSON syntax was intact, the parser read the 20 elements correctly without dropping any of them. However, when regex fallback `re.findall(r'"((?:[^"\\]|\\.)*)"', json_str)` was triggered due to unescaped quotes or invalid formatting, parser regex was vulnerable to incorrectly splitting or dropping strings containing inner quotes or control characters.

### Q6: Có segment nào bị filter không?
- **Answer**: No segment was explicitly filtered out in Python code prior to validation. The reduction from 30 to 20 happened during LLM generation because the prompt lacked explicit segment ID keys.

### Q7: Có `MAX_TOKENS` không?
- **Answer**: Yes. In `gemini_provider.py`, payload requests were sent without setting `generationConfig.maxOutputTokens` or `responseMimeType="application/json"`. Furthermore, `candidates[0].get("finishReason")` was ignored by `gemini_provider.py`, so when Gemini hit output token limits (`MAX_TOKENS`), it returned an incomplete JSON array, leading to parsing failures or truncated lists.

### Q8: Prompt có vấn đề không?
- **Answer**: Yes. The original prompt sent `["line 1", "line 2", ...]` as a flat list of text strings without segment IDs (`id: 0, id: 1`). Without explicit ID tracking in the prompt, Gemini treated the prompt as a standard translation task and consolidated short/contiguous sentences, reducing 30 items to 20 items.

### Q9: Batch size có vấn đề không?
- **Answer**: Batch size 30 without structured output or token constraints increases the token output size significantly, triggering Gemini output token limits.

### Q10: ID mapping có vấn đề không?
- **Answer**: Yes. The system relied strictly on array index position (`translated_list[i]` for `batch_segments[i]`). When Gemini dropped or merged items, positional array matching collapsed, risking shift in subtitle timestamps across the entire timeline.

### Q11: Root cause chính xác là gì?
- **Answer**: **Root Cause Group B (Prompt Bug - Missing Segment IDs) + Group C (Gemini Output Truncation / `MAX_TOKENS` & Missing API JSON Schema Config) + Group G (Positional Array Mapping vs Structured ID Mapping)**:
  1. Passing an un-indexed array of strings in prompt allowed Gemini to merge/omit short dialogue segments.
  2. Lack of `generationConfig` (`responseMimeType="application/json"`, `maxOutputTokens=8192`) and `finishReason` check in `gemini_provider.py` allowed truncated/unformatted responses.
  3. Lack of targeted recovery logic for missing segment IDs in `translator_service.py`.

### Q12: File/function nào cần sửa?
- `backend/app/providers/llm/gemini_provider.py` (`generate_text`)
- `backend/app/services/video_translator/translator_service.py` (`translate_transcript_segments`, `_safe_parse_json_translation`, recovery logic)
- `backend/tests/unit/test_gemini_translation.py` (new test suite)

### Q13: Đã sửa những gì?
1. **Gemini API Configuration**: Added `generationConfig` with `responseMimeType="application/json"`, `maxOutputTokens=8192`, `temperature=0.2`.
2. **Finish Reason Validation**: Added explicit check for `candidates[0].get("finishReason") == "MAX_TOKENS"`.
3. **Structured ID Mapping**: Updated prompt payload to pass `[{"id": "0", "text": "..."}, ...]` and parse returned `[{"id": "0", "translation": "..."}, ...]`.
4. **Targeted Recovery Retry**: If `output_count < input_count`, calculate missing IDs `set(input_ids) - set(output_ids)` and retry ONLY missing segments with targeted warning prompt before merging.
5. **Dynamic Sub-batch Splitting**: Automatically split problematic batches into smaller sub-batches if retries fail.
6. **Detailed Audit Observability**: Added structured logging for `job_id`, `batch_index`, `input_count`, `output_count`, `missing_ids`, `finish_reason`, `parse_status`, `recovery_status`.

### Q14: Đã test những gì?
- Test 1: Full count match (30 inputs -> 30 outputs).
- Test 2: Mismatch recovery (30 inputs -> 20 outputs -> targeted retry recovers missing 10).
- Test 3: Over-length output / unknown IDs rejection.
- Test 4: Malformed JSON parser error recovery.
- Test 5: MAX_TOKENS truncation detection and sub-batch retry.
- Test 6: Empty translation segment preservation.
- Test 7: Segment ID mismatch detection.
- Test 8: End-to-end translation pipeline synchronization test with full transcript dataset.
