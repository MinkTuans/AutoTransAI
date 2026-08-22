# OpenAI Usage Audit Report

## 1. Executive Summary

Hệ thống **WorkflowVdAi** hiện đang gặp sự cố gián đoạn workflow xử lý video khi **OpenAI Whisper STT** hoặc **OpenAI ChatGPT** được gọi tự động ngoài ý muốn, gây ra lỗi HTTP 429 (`insufficient_quota`: *You have no credits remaining*).

Dù người dùng đã chọn **Google Gemini** làm AI/STT chính, hệ thống vẫn tự động kích hoạt fallback sang OpenAI do logic thiết kế fallback cứng (unconditional fallback) trong `translator_service.py`, kết hợp với giá trị mặc định `llm_provider_id = "openai"` ở các lớp Database, Backend Pydantic Schemas, và Frontend React state.

Báo cáo này cung cấp kết quả điều tra toàn bộ codebase, trace nguyên nhân gốc của Job `VT-99A45C` (tại chunk `g_chunk_010.wav`), thống kê toàn bộ điểm gọi OpenAI, và đề xuất kiến trúc mới đảm bảo **Gemini là primary STT/LLM độc lập, OpenAI hoàn toàn optional và không bao giờ tự động gọi ngầm khi bị disabled**.

---

## 2. Root Cause (Nguyên nhân gốc)

Khi xử lý job `VT-99A45C` (video dài 38 phút 7.5 giây), Gemini STT tiến hành cắt file audio thành 27 chunks (`g_chunk_000.wav` đến `g_chunk_026.wav`).

1. **Điểm thất bại ban đầu**: Tại chunk `g_chunk_010.wav`, hàm `probe_duration_async` gặp lỗi không thể đọc độ dài file audio (`Could not determine duration for media file ... g_chunk_010.wav`). Hàm `transcribe_audio_with_gemini` bắn exception `RuntimeError`.
2. **Kích hoạt Fallback tự động**: Lớp `speech_to_text_and_detect_language` trong `translator_service.py` bắt `Exception` của Gemini. Do phát hiện biến môi trường `OPENAI_API_KEY` tồn tại trong `.env`, code lập tức tự động chuyển sang hàm `transcribe_audio_with_whisper(audio_path, job_id)`.
3. **OpenAI API Thất bại**: OpenAI Whisper API trả về HTTP 429 với body `{"error": {"message": "You have no credits remaining...", "type": "insufficient_quota"}}`.
4. **Vòng lặp Smart Retry & Stalled Job**: Do lỗi HTTP 429 không được phân loại là **NON-RETRYABLE**, hệ thống hoặc người dùng kích hoạt `Smart Retry`, khiến toàn bộ chuỗi: *Extract Audio -> Slicing -> Gemini Failure -> Silent OpenAI Fallback -> 429 Quota Error* lặp lại.

**Kết luận nguyên nhân gốc**: Hệ thống gọi OpenAI không phải do cấu hình của người dùng, mà do:
- Logic fallback cứng `if settings.OPENAI_API_KEY and llm_provider_id != "openai"` trong `speech_to_text_and_detect_language`.
- Logic fallback chuỗi `fallback_ids = ["openai", "gemini"]` trong `translate_transcript_segments`.
- Cấu hình mặc định hệ thống ở Database Model, Backend Schema và Frontend UI là `"openai"` thay vì `"gemini"`.

---

## 3. Gemini STT Flow

Flow xử lý Gemini STT hiện tại trong `transcribe_audio_with_gemini`:

```text
Audio File (.wav)
 ↓
Kiểm tra dung lượng (>5MB hoặc >90s)
 ↓
FFmpeg Slicing -> các chunk audio 90s (ví dụ: g_chunk_000.wav ... g_chunk_026.wav)
 ↓
Đọc từng chunk -> probe_duration_async(chunk_path)
 ↓
Gửi base64 audio + Inline Prompt tới Gemini REST API (v1beta/models/{model}:generateContent)
  (Candidates: gemini-3.5-flash-lite, gemini-3.5-flash, gemini-3.6-flash, gemini-flash-latest,...)
 ↓
Parse JSON Response -> validate_and_clean_timeline_segments
 ↓
Trả về validated_segments + detected_lang
```

### Các điểm yếu phát hiện trong Gemini Flow:
- Khi 1 chunk thất bại (chẳng hạn `g_chunk_010.wav` do `probe_duration_async` hoặc mạng bận), toàn bộ hàm `transcribe_audio_with_gemini` bị fail ngay lập tức thay vì retry chunk đó.
- Nếu Gemini trả về response rỗng hoặc JSON parse lỗi, ngoại lệ sẽ được ném ra và làm bùng nổ sang fallback chain sang OpenAI.

---

## 4. OpenAI Invocation Flow

Execution flow thực tế dẫn đến lỗi:

```text
Video Source
 ↓
FFmpeg Audio Extraction (extracted_audio.wav)
 ↓
speech_to_text_and_detect_language(llm_provider_id="gemini")
 ↓
Priority 2: transcribe_audio_with_gemini()
 ↓
Chunk g_chunk_010.wav probe duration failed (RuntimeError)
 ↓
Catch Exception -> stt_errors.append("Gemini STT failed: ...")
 ↓
Check condition: settings.OPENAI_API_KEY (TRUE) && llm_provider_id != "openai" (TRUE)
 ↓
AUTOMATIC FALLBACK: transcribe_audio_with_whisper()
 ↓
httpx POST https://api.openai.com/v1/audio/transcriptions (model: whisper-1)
 ↓
OpenAI API response: HTTP 429 insufficient_quota
 ↓
Exception: "Whisper STT fallback failed: OpenAI Whisper API HTTP 429: ..."
 ↓
Pipeline Crash: STT FAILED
```

---

## 5. Fallback Architecture (Kiến trúc Fallback hiện tại)

### STT Provider Priority (Hiện tại)
1. Neu `llm_provider_id == "openai"` hoac khong co `GEMINI_API_KEY` -> OpenAI Whisper (`transcribe_audio_with_whisper`)
2. Neu co `GEMINI_API_KEY` -> Gemini STT (`transcribe_audio_with_gemini`)
3. Neu Gemini STT fail VA co `OPENAI_API_KEY` -> Silent Fallback sang OpenAI Whisper

### LLM Translation Provider Priority (Hiện tại)
1. Primary Provider: `llm_provider_id` (mac dinh: `"openai"`)
2. Fallback Provider: Neu Primary is `"gemini"`, Fallback is `["openai", "gemini"]` -> Unconditional OpenAI Fallback.

---

## 6. All OpenAI Usage (Bảng thống kê toàn bộ điểm sử dụng OpenAI)

| Component | File | Function / Location | OpenAI usage | Khi nào được gọi | Có thể disable hiện tại? |
| --------- | ---- | ------------------- | ------------ | ---------------- | ------------------------- |
| **STT Fallback** | [translator_service.py](file:///C:/Hack/WorkflowVdAi/backend/app/services/video_translator/translator_service.py#L607) | `speech_to_text_and_detect_language()` | OpenAI Whisper API (`v1/audio/transcriptions`) | Khi Gemini STT gặp lỗi và `OPENAI_API_KEY` có giá trị | ❌ KHÔNG (Fallback cứng trong code) |
| **STT Primary** | [translator_service.py](file:///C:/Hack/WorkflowVdAi/backend/app/services/video_translator/translator_service.py#L589) | `speech_to_text_and_detect_language()` | OpenAI Whisper API (`v1/audio/transcriptions`) | Khi `llm_provider_id == "openai"` | ⚠️ Có (nếu chọn provider khác trong UI) |
| **LLM Provider** | [openai_provider.py](file:///C:/Hack/WorkflowVdAi/backend/app/providers/llm/openai_provider.py#L81) | `OpenAILLMProvider.generate_text()` | Chat Completions (`v1/chat/completions`) | Khi dịch thuật thoại và provider chọn/fallback là OpenAI | ⚠️ Có (nếu không có trong fallback list) |
| **LLM Provider Validation** | [openai_provider.py](file:///C:/Hack/WorkflowVdAi/backend/app/providers/llm/openai_provider.py#L54) | `OpenAILLMProvider.validate_configuration()` | Models list (`v1/models`) | Khi ứng dụng khởi tạo / kiểm tra provider | ⚠️ Có |
| **Database Schema Default** | [video_translator.py](file:///C:/Hack/WorkflowVdAi/backend/app/models/video_translator.py#L93) | Column `llm_provider_id` | Server default value `"openai"` | Khi tạo job mới trong DB mà không truyền provider | ❌ KHÔNG (Mặc định DB) |
| **API Request Schema Default** | [video_translator.py](file:///C:/Hack/WorkflowVdAi/backend/app/api/routes/video_translator.py#L106) | `CreateJobRequest` Pydantic Schema | Default field `"openai"` | Khi Frontend tạo job không chỉ định `llm_provider_id` | ❌ KHÔNG (Mặc định API) |
| **Frontend Initial State** | [VideoTranslator.jsx](file:///C:/Hack/WorkflowVdAi/frontend/src/pages/VideoTranslator.jsx#L17) | `useState('openai')` | UI state default | Khi mở trang Video Translator | ❌ KHÔNG (Mặc định Frontend UI) |

---

## 7. Environment Variables (Kiểm tra biến môi trường)

- `OPENAI_API_KEY`: **Configured** trong `.env` (`sk-proj-u4VtU...`) nhưng **HẾT QUOTA / 0 CREDITS**.
- `GEMINI_API_KEY`: **Configured** trong `.env` (`AQ.Ab8RN6J...`), hoạt động bình thường.
- `ENABLE_OPENAI_FALLBACK`: **Missing** (Chưa có flag cấu hình bật/tắt OpenAI fallback).

---

## 8. Dependencies (Kiểm tra gói phụ thuộc)

- `requirements.txt`: **Không cài đặt** package `openai` hoặc `openai-whisper`.
- `package.json`: **Không cài đặt** package `openai`.
- Cả backend sử dụng thư viện HTTP chuẩn `httpx` để tự gọi trực tiếp REST APIs của OpenAI (`https://api.openai.com/...`).

---

## 9. Retry Logic Audit

- **Model Retry Loop**: Trong `OpenAILLMProvider.generate_text()`, code duyệt qua mảng `OPENAI_MODEL_CANDIDATES` (`gpt-4o-mini`, `gpt-4o`, `gpt-3.5-turbo`). Nếu gặp lỗi HTTP 429 hoặc 500, nó lặp lại request với model tiếp theo.
- **Lỗi Quota 429**: HTTP 429 với thông điệp `insufficient_quota` hiện đang bị xử lý chung như lỗi thông thường (try next model / throw exception cho retry loop ngoài), dẫn đến việc thử lại vô ích và làm treo job.

---

## 10. Job VT-99A45C Analysis

Log thực tế tại `data/translator/jobs/VT-99A45C/job.log`:
1. `[2026-08-22 00:27:37]` [STT] Starting Speech-to-Text (Audio duration: 2287.5s, Primary Provider: gemini)
2. `[2026-08-22 00:27:37]` [Gemini] Slicing audio into 90.0s chunks...
3. Gemini gặp lỗi đọc duration của chunk `g_chunk_010.wav`.
4. Code ném ngoại lệ `Gemini STT failed: Could not determine duration for media file... g_chunk_010.wav`.
5. Code nhảy sang fallback OpenAI Whisper: `[STT] [Whisper] Large audio file...`.
6. OpenAI Whisper trả về HTTP 429 `insufficient_quota`.
7. Pipeline dừng với lỗi `STT FAILED: Gemini STT failed... | Whisper STT fallback failed: OpenAI Whisper API HTTP 429...`.

---

## 11. Files Requiring Changes (Danh sách file cần chỉnh sửa)

1. `backend/app/config.py`: Thêm biến cấu hình `ENABLE_OPENAI_FALLBACK: bool = False` và `DEFAULT_LLM_PROVIDER: str = "gemini"`.
2. `backend/app/services/video_translator/translator_service.py`:
   - Loại bỏ silent fallback OpenAI trong `speech_to_text_and_detect_language`. Chỉ dùng Gemini khi provider được chọn là Gemini (hoặc khi OpenAI fallback được bật rõ ràng via config).
   - Loại bỏ fallback cứng OpenAI trong `translate_transcript_segments`.
   - Bổ sung retry per-chunk cho Gemini STT trước khi kết luận chunk hỏng.
   - Thêm xử lý phân loại `NON-RETRYABLE` đối với các lỗi HTTP 429 `insufficient_quota` / `invalid_api_key`.
3. `backend/app/models/video_translator.py`: Đổi default DB column `llm_provider_id` thành `"gemini"`.
4. `backend/app/api/routes/video_translator.py`: Đổi default Pydantic schema `llm_provider_id` thành `"gemini"`.
5. `frontend/src/pages/VideoTranslator.jsx`: Đổi UI default state `llmProviderId` từ `'openai'` thành `'gemini'`.
6. `.env.example` & `.env`: Cập nhật cấu hình mặc định Gemini làm ưu tiên số 1, bổ sung `ENABLE_OPENAI_FALLBACK=false`.

---

## 12. Recommended Architecture (Kiến trúc đề xuất)

```text
               STT / LLM Request
                       │
             Check Selected Provider
                       │
        ┌──────────────┴──────────────┐
        ▼                             ▼
  [ Gemini ]                     [ OpenAI ]
 (Primary Default)            (Optional Opt-In)
        │                             │
  STT / Translate               STT / Translate
        │                             │
    Success                       Success
        │                             │
     Return                        Return
        │                             │
     Failure                       Failure
        │                             │
 Check ENABLE_OPENAI_FALLBACK     Check Non-retryable (429 Quota)
 (Default: False)                     │
        │                       Fail Immediately
  ┌─────┴─────┐                 No Infinite Retry
  ▼           ▼
[True]     [False]
  │           │
Fallback   RAISE ERROR:
to OpenAI  "Gemini STT Failed.
           No fallback enabled."
```

---

## 13. Risk Assessment (Đánh giá rủi ro)

- **Rủi ro rò rỉ fallback**: Thấp. Khi đặt `ENABLE_OPENAI_FALLBACK=False`, hệ thống cắt đứt hoàn toàn việc gọi sang `api.openai.com` khi Gemini gặp sự cố.
- **Tương thích ngược**: Các job cũ đã lưu `llm_provider_id="openai"` vẫn có thể chạy nếu OpenAI có credit, nhưng nếu hết credit sẽ fail ngay lập tức với thông báo lỗi quota rõ ràng thay vì treo job.
- **Workflow video/audio**: Giữ nguyên toàn bộ logic đồng bộ timeline, chunking FFmpeg và TTS.

---

## 14. Test Plan (Kịch bản kiểm thử)

1. **Test 1: Gemini STT Thành công**: Chạy job STT với Gemini -> Xác nhận 0 request gửi tới OpenAI API.
2. **Test 2: Gemini STT Thất bại & OpenAI Disabled**: Simulate Gemini STT failure -> Hệ thống ném lỗi *"Gemini STT failed. Fallback disabled."* và KHÔNG gọi OpenAI Whisper API.
3. **Test 3: Thiếu OPENAI_API_KEY**: Xóa hoặc để trống `OPENAI_API_KEY` trong `.env` -> Backend khởi động bình thường, workflow Gemini chạy 100% không bị ảnh hưởng.
4. **Test 4: OpenAI 429 Quota Non-retryable**: Gọi OpenAI direct khi hết quota -> Nhận lỗi ngay lập tức, không retry lặp đi lặp lại.
5. **Test 5: Full Pipeline**: Upload video -> Extraction -> Gemini STT -> Gemini Translate -> EdgeTTS -> Synchronization -> Video final thành công.
