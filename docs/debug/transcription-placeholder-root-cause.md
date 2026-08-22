# Transcription Placeholder Root Cause Analysis

## Symptom

When processing a video translation job (e.g., job `VT-88DF0F` or `VT-CD1984`), the Speech-to-Text (STT) -> Transcript -> Segmentation -> Translation pipeline generates fake placeholder segments instead of actual transcript text from the audio:

```text
Phân đoạn #1 (00:00 → 00:08)
Gốc: "Phần phát biểu video #1 [0s - 8s]"
Bản dịch: "Phần phát biểu video #1 [0s - 8s]"

Phân đoạn #2 (00:08 → 00:16)
Gốc: "Phần phát biểu video #2 [8s - 16s]"
Bản dịch: "Phần phát biểu video #2 [8s - 16s]"
...
```

The system marks Phase 1 as completed (`SEGMENT_EDITING`), hiding the fact that STT actually failed or was bypassed.

---

## Expected Behavior

1. Audio track is extracted into 16kHz mono WAV format.
2. STT Provider (OpenAI Whisper or Gemini AI Studio) transcribes actual speech with exact word/sentence timestamps.
3. Transcript segments contain real spoken text in original language.
4. LLM translates real transcript text into target language (e.g. Vietnamese).
5. If STT fails or API key is missing or model fails, the job MUST immediately fail with status `FAILED` and an explicit error message `STT FAILED: <reason>`. No fake segments or mock fallback text may be produced or saved to DB.

---

## Actual Behavior

1. Audio extraction completes successfully (e.g. 2287.54s duration, 73.2 MB WAV file for a 38-minute video).
2. STT service `speech_to_text_and_detect_language` bypasses real STT or catches API errors silently.
3. Hardcoded fallback chunker executes, dividing total duration into fixed 8-second intervals and generating mock text:
   `"Phần phát biểu video #N [start - end]"`
4. Pipeline marks job as `TRANSLATED` and `SEGMENT_EDITING`.
5. Database stores 285 mock segments.
6. Frontend displays mock segments with success notification.

---

## Pipeline Trace & Empirical Evidence

From empirical database inspection of active jobs `VT-88DF0F` and `VT-CD1984`:

```text
[Job ID: VT-88DF0F]
- Asset: input_source.mp4 (Duration: 2287.54s, File Size: 108,691,820 bytes)
- Extracted Audio: 16kHz 16-bit mono WAV (~73.2 MB)
- Status: segment_editing
- Segments Count: 285
- Segment 1: original='Phần phát biểu video #1 [0s - 8s]', translated='Phần phát biểu video #1 [0s - 8s]'
- Segment 2: original='Phần phát biểu video #2 [8s - 16s]', translated='Phần phát biểu video #2 [8s - 16s]'
```

---

## Exact Source of Placeholder Text

- **File**: [`backend/app/services/video_translator/translator_service.py`](file:///c:/Hack/WorkflowVdAi/backend/app/services/video_translator/translator_service.py#L230-L247)
- **Function**: `speech_to_text_and_detect_language`
- **Lines**: 230 - 247

```python
    # Fallback STT segment generator based on total audio duration
    detected_lang = "English" if source_language == "auto" else source_language
    chunk_len = 8.0
    segment_count = max(1, int(total_duration / chunk_len))

    segments = []
    for i in range(segment_count):
        st = i * chunk_len
        et = min(total_duration, (i + 1) * chunk_len)
        segments.append({
            "number": i + 1,
            "start_time": round(st, 2),
            "end_time": round(et, 2),
            "text": f"Phần phát biểu video #{i+1} [{st:.0f}s - {et:.0f}s]",
        })

    log_job_event(job_id, "STT", f"Fallback STT created {len(segments)} segments.")
    return segments, detected_lang
```

---

## Root Causes Identified

### 1. Hardcoded Audio File Size Limit (< 15 MB)
In `translator_service.py` line 147:
```python
if gemini and settings.GEMINI_API_KEY and audio_path.stat().st_size < 15 * 1024 * 1024:
```
Extracting audio from any video longer than ~8 minutes produces a WAV file larger than 15 MB (e.g., 38-min video -> 73.2 MB WAV). This condition evaluates to `False`, forcing the service to skip STT entirely and directly trigger the fallback mock chunker.

### 2. Missing OpenAI Whisper STT Provider Implementation
Although `OPENAI_API_KEY` is present in `.env` and valid (verified via API test returning model `whisper-1`), `translator_service.py` had zero code to call OpenAI Whisper API (`https://api.openai.com/v1/audio/transcriptions`). It only attempted Gemini multi-modal STT.

### 3. Model Candidate Mismatch & HTTP Errors
`GEMINI_MODEL_CANDIDATES` in `gemini_provider.py` contained model names like `"gemini-3.5-flash-lite"`, which returned HTTP 404 or failed on audio multimodal payloads.

### 4. Silent Error Masking & Fallthrough Architecture
Instead of raising a `RuntimeError` or `TranscriptionError` when STT failed or was bypassed, lines 226-228 caught the exception with a warning log and allowed execution to continue to the fallback mock generator. The function returned `(segments, detected_lang)` with status `SUCCESS`.

### 5. Translation & Frontend Propagation
`translate_transcript_segments` in `translator_service.py` line 301 explicitly checked:
```python
if target_language == "vi" and "Phần phát biểu" in orig:
    s["translated_text"] = orig
```
This propagated the mock text into `translated_text`, and saved it into `VideoTranslationSegment` objects in MySQL database.

---

## Proposed Fix Strategy

1. **Delete Mock Fallback Generator**: Remove lines 230-247 that generate `Phần phát biểu video #N`. If STT fails, raise `RuntimeError("STT_FAILED: ...")`.
2. **Implement OpenAI Whisper Provider**:
   - Add `OpenAIWhisperProvider` or direct audio transcription client calling `https://api.openai.com/v1/audio/transcriptions` with model `whisper-1` and `response_format="verbose_json"`.
   - Add audio chunking for files >25MB (OpenAI Whisper file size limit is 25MB) using FFmpeg to slice long WAV files into 10-minute chunks and combine timestamped segments.
3. **Fix Gemini STT Provider**:
   - Support updated Gemini models (`gemini-2.0-flash`, `gemini-1.5-flash`) and handle audio files >15MB via chunking or File API.
4. **Strict Placeholder Validation**:
   - Add a validator in `translator_service.py` and `video_translator.py` route that checks generated segments for placeholder patterns (e.g. `Phần phát biểu video #`, `Video speech #`, `Segment #`).
   - If any placeholder string is detected, reject the output and fail the job immediately.
5. **Clear Error Reporting**:
   - Update job state to `FAILED` with explicit stage `"STT_FAILED"` and detailed log events whenever STT API returns error or missing key.

---

## Risk Assessment

- **Low Risk**: Removing mock fallback forces STT errors to be exposed immediately, preventing corrupt data from persisting to DB.
- **Dependency**: Requires active `OPENAI_API_KEY` or `GEMINI_API_KEY` for successful transcription.
