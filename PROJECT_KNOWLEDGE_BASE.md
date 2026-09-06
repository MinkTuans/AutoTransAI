# PROJECT KNOWLEDGE BASE

**Project Name:** AutoTransAI (AutoTransAi Studio / WorkflowVdAi)  
**Description:** Local-First Script-to-Video & AI Video Translation & Dubbing Pipeline with 6-Stage Unified Workflow Engine.  
**Primary Repository Path:** `c:\Hack\AutoTransAI`  

---

## # 1 PROJECT OVERVIEW

AutoTransAI (còn được gọi là **AutoTransAi Studio** hoặc **WorkflowVdAi**) là một ứng dụng Desktop/Web local-first nâng cao, tích hợp 2 đường ống xử lý video tự động hóa hoàn chỉnh:
1. **Script-to-Video Pipeline:** Chuyển đổi kịch bản văn bản thành video clip minh họa có giọng đọc AI, đồng bộ âm thanh và tự động ghép nối.
2. **AI Video Translation & Dubbing Pipeline:** Dịch thuật và lồng tiếng video từ URL (YouTube, TikTok, Bilibili, direct MP4) hoặc File Upload local. Tự động bóc tách âm thanh, chạy STT (Gemini / Whisper), dịch thuật ngữ cảnh kèm bộ nhớ thuật ngữ Glossaries & trích xuất thực thể, lồng tiếng TTS đa nhân vật (Edge TTS, Google Cloud TTS, ElevenLabs), đồng bộ kéo giãn thời lượng âm thanh PCM 44.1kHz sample-accurate, chèn phụ đề ASS/SRT/VTT, biên tập reframing 9:16/16:9, thêm watermark logo, ducking nhạc nền BGM, kiểm định chất lượng LUFS, và tự động đăng video lên YouTube.

- **Source Reference:** [main.py](file:///c:/Hack/AutoTransAI/backend/app/main.py), [config.py](file:///c:/Hack/AutoTransAI/backend/app/config.py)
- **Relevant Classes/Functions:** [FastAPI app](file:///c:/Hack/AutoTransAI/backend/app/main.py#L101), [Settings](file:///c:/Hack/AutoTransAI/backend/app/config.py#L30)

---

## # 2 TECHNOLOGY STACK

Toàn bộ công nghệ được kiểm tra và xác nhận từ các file dependency gốc:

### Frontend
- **Framework:** React 18.3.1 (SPA)
- **Build Tool:** Vite 5.4.0 (Dev Server port 5173, production build bundle)
- **Styling:** Vanilla CSS (`App.css`), Glassmorphism UI
- **HTTP Client:** Axios 1.19.0
- **Real-time Streaming:** SSE (Server-Sent Events) EventSource
- **Source Reference:** [package.json](file:///c:/Hack/AutoTransAI/frontend/package.json), [App.jsx](file:///c:/Hack/AutoTransAI/frontend/src/App.jsx), [api.js](file:///c:/Hack/AutoTransAI/frontend/src/api.js)

### Backend
- **Framework:** FastAPI 0.115.0 (Python 3.12, async/await)
- **ASGI Server:** Uvicorn (standard) 0.30.0
- **Data Validation:** Pydantic 2.8.0, Pydantic-Settings 2.4.0
- **Logging:** structlog 24.1.0
- **Real-time Streaming:** sse-starlette 2.0.0
- **Testing:** pytest 8.0.0, pytest-asyncio 0.23.0 (114 passed, 6 skipped)
- **Source Reference:** [requirements.txt](file:///c:/Hack/AutoTransAI/backend/requirements.txt), [main.py](file:///c:/Hack/AutoTransAI/backend/app/main.py)

### Database & ORM
- **Engine:** Supabase PostgreSQL (`postgresql+asyncpg` driver) for both Local Development and Production environments (`db.qcxlljiewguxumtlucfc.supabase.co:5432/postgres`). Automatic SQLite fallback is completely disabled in runtime logic.
- **ORM:** SQLAlchemy 2.0.30 (Async Engine `create_async_engine`), `asyncpg` 0.31.0, `aiosqlite` 0.20.0 (retained for offline export utilities & test fixtures).
- **Migration:** Automated Supabase Migration script (`scripts/migrate_to_supabase.py`), Alembic 1.13.0 + Dynamic DDL Schema inspector listener (`_sync_schema_sync`).
- **Source Reference:** [database.py](file:///c:/Hack/AutoTransAI/backend/app/database.py#L35), [migrate_to_supabase.py](file:///c:/Hack/AutoTransAI/backend/scripts/migrate_to_supabase.py)

### AI Providers & Models
- **LLM:** Google Gemini (`gemini-2.5-flash`, `gemini-1.5-pro` via `google-genai`), OpenAI (`gpt-4o`, `gpt-4o-mini` via `openai`)
- **STT:** Gemini Audio STT, OpenAI Whisper (`whisper-1`)
- **TTS:** Edge TTS (`edge-tts` 6.1.0, miễn phí), Google Cloud TTS (`google_cloud_tts_api`), ElevenLabs API (`elevenlabs`)
- **Video Generation:** Kling AI (`api.klingai.com`), fal.ai (`fal-ai/hunyuan-video`), Local Provider (Mock)
- **Source Reference:** [registry.py](file:///c:/Hack/AutoTransAI/backend/app/providers/registry.py), [key_manager.py](file:///c:/Hack/AutoTransAI/backend/app/services/key_manager.py)

### Storage & Media Processing
- **Storage:** Supabase Storage (`supabase` Python SDK, `autotransai-private` private bucket, `autotransai-public` public bucket), Local Storage Fallback (`data/projects/`, `data/translator/assets/`, `data/supabase_storage/`). Cloudflare R2 is 100% decommissioned.
- **Media Engine:** System FFmpeg & FFprobe (async subprocess execution, libx264, aac, filtergraphs, atempo, volume ducking, ebur128 LUFS, scale/crop, overlay).
- **Source Reference:** [storage_service.py](file:///c:/Hack/AutoTransAI/backend/app/services/storage_service.py), [ffmpeg_process.py](file:///c:/Hack/AutoTransAI/backend/app/media/ffmpeg_process.py)

---

## # 3 PROJECT ARCHITECTURE

Sơ đồ tổng quan luồng tương tác kiến trúc hệ thống:

```text
+-----------------------------------------------------------------------------------+
|                               USER / BROWSER (Vite React UI)                       |
+-----------------------------------------------------------------------------------+
                                         │
                         HTTP REST / SSE Event Streams
                                         │
                                         ▼
+-----------------------------------------------------------------------------------+
|                             FASTAPI BACKEND SERVER                                |
|  - Routers: projects.py, video_translator.py, providers.py, video_editor.py        |
|  - Middleware: CORS, Exception Handlers, Security SSRF Validator                   |
+-----------------------------------------------------------------------------------+
                                         │
                                         ▼
+-----------------------------------------------------------------------------------+
|                   UNIFIED STAGE-BASED WORKFLOW ENGINE                             |
|  [STAGE 1: INGEST] -> [STAGE 2: ANALYZE] -> [STAGE 3: TRANSLATE]                  |
|  [STAGE 4: DUB]    -> [STAGE 5: PRODUCE] -> [STAGE 6: PUBLISH]                    |
+-----------------------------------------------------------------------------------+
       │                         │                        │                    │
       ▼                         ▼                        ▼                    ▼
+---------------+       +------------------+     +-----------------+   +---------------+
| DATABASE ORM  |       | KEY MANAGER      |     | MEDIA SERVICES  |   | AI PROVIDERS  |
| SQLAlchemy    |       | Multi-Key Pool   |     | FFmpeg/FFprobe  |   | Gemini, OpenAI|
| SQLite (WAL)  |       | Cooldown & Fail  |     | Audio Sync      |   | Edge/ElevenLabs|
| Mysql Support |       | .env / JSON sync |     | Reframing/Sub   |   | Kling / FAL   |
+---------------+       +------------------+     +-----------------+   +---------------+
       │                         │                        │                    │
       ▼                         ▼                        ▼                    ▼
+-----------------------------------------------------------------------------------+
|                         PERSISTENT STORAGE LAYER                                  |
| Local Storage (data/projects, data/translator) | Cloudflare R2 Persistent Storage  |
+-----------------------------------------------------------------------------------+
```

- **Source Reference:** [UNIFIED_WORKFLOW_IMPLEMENTATION_REPORT.md](file:///c:/Hack/AutoTransAI/UNIFIED_WORKFLOW_IMPLEMENTATION_REPORT.md), [workflow_engine.py](file:///c:/Hack/AutoTransAI/backend/app/workflow/workflow_engine.py)

---

## # 4 FOLDER STRUCTURE

| Thư mục / File | Chức năng chính | Source Reference |
|---|---|---|
| `backend/app/api/routes` | REST Routers & SSE Stream Endpoints | [routes/](file:///c:/Hack/AutoTransAI/backend/app/api/routes) |
| `backend/app/core` | Logging, SSRF Security, Exceptions, Retry Logic | [core/](file:///c:/Hack/AutoTransAI/backend/app/core) |
| `backend/app/database.py` | SQLAlchemy Async Engine, Dynamic DDL Schema Listener | [database.py](file:///c:/Hack/AutoTransAI/backend/app/database.py) |
| `backend/app/models` | SQLAlchemy ORM Models cho 19 bảng database | [models/](file:///c:/Hack/AutoTransAI/backend/app/models) |
| `backend/app/providers` | AI Provider Interfaces, Registry, Audio/LLM/Video implementations | [providers/](file:///c:/Hack/AutoTransAI/backend/app/providers) |
| `backend/app/schemas` | Pydantic Request/Response validation schemas | [schemas/](file:///c:/Hack/AutoTransAI/backend/app/schemas) |
| `backend/app/services` | Business Logic (KeyManager, Storage, Cleanup, VideoTranslator, VideoEditor) | [services/](file:///c:/Hack/AutoTransAI/backend/app/services) |
| `backend/app/workflow` | Unified Stage-Based Workflow Engine (Orchestrator, Stages 1-6) | [workflow/](file:///c:/Hack/AutoTransAI/backend/app/workflow) |
| `backend/app/media` | FFmpeg / FFprobe Async Subprocess Executable Wrappers | [media/](file:///c:/Hack/AutoTransAI/backend/app/media) |
| `frontend/src/pages` | Các màn hình chính (VideoTranslator, Dashboard, CreateProject, ProjectDetail, Settings) | [pages/](file:///c:/Hack/AutoTransAI/frontend/src/pages) |
| `frontend/src/components` | UI Components (WorkflowTimeline, ProjectGlossaryManager, VideoEditorStudio, AIQCScorecard, YouTubePublisherModal) | [components/](file:///c:/Hack/AutoTransAI/frontend/src/components) |
| `shared` | Configuration loader dùng chung (`load_root_env()`) | [config.py](file:///c:/Hack/AutoTransAI/shared/config.py) |
| `data` | Nơi chứa SQLite DB (`workflow.db`), API Keys JSON (`api_keys.json`), assets, projects | [data/](file:///c:/Hack/AutoTransAI/data) |

---

## # 5 FRONTEND ARCHITECTURE

Frontend là ứng dụng Single Page Application (SPA) viết bằng React 18 & Vite:
- **Routing:** Quản lý bằng state `activePage` trong [App.jsx](file:///c:/Hack/AutoTransAI/frontend/src/App.jsx#L11) với các route: `'translator'`, `'dashboard'`, `'create'`, `'detail'`, `'settings'`.
- **API Wrapper:** Module [api.js](file:///c:/Hack/AutoTransAI/frontend/src/api.js) đóng gói các đối tượng `projectsApi`, `providersApi`, `systemApi`, `videoTranslatorApi`, `videoEditorApi`.
- **Real-time Monitoring:** Kết nối SSE qua `EventSource` tới `/api/video-translator/jobs/{job_id}/progress` để vẽ timeline 6 Stage và log console.

- **Source Reference:** [App.jsx](file:///c:/Hack/AutoTransAI/frontend/src/App.jsx), [api.js](file:///c:/Hack/AutoTransAI/frontend/src/api.js), [VideoTranslator.jsx](file:///c:/Hack/AutoTransAI/frontend/src/pages/VideoTranslator.jsx)

---

## # 6 BACKEND ARCHITECTURE

Backend được xây dựng bằng FastAPI với mô hình bất đồng bộ hoàn toàn:
- **Lifespan Manager:** Khởi tạo logging, tự động tạo thư mục `data/`, gọi `init_db()` để tạo bảng & chạy dynamic migration, tự động đăng ký tất cả AI Providers vào Registry.
- **Dynamic DDL Migration:** Hàm `_sync_schema_sync` trong [database.py](file:///c:/Hack/AutoTransAI/backend/app/database.py#L59) sử dụng SQLAlchemy Inspector phát lệnh `ALTER TABLE ADD COLUMN` tự động khi ORM model có cột mới.
- **Global Exception Handler:** Bắt ngoại lệ server error 500, trả về JSON cấu trúc chuẩn `{ success: false, detail, error_type, path }`.

- **Source Reference:** [main.py](file:///c:/Hack/AutoTransAI/backend/app/main.py), [database.py](file:///c:/Hack/AutoTransAI/backend/app/database.py)

---

## # 7 DATABASE ARCHITECTURE

Danh sách 23 bảng ORM SQLAlchemy trong [backend/app/models/](file:///c:/Hack/AutoTransAI/backend/app/models):

1. **`projects`:** Dự án Script-to-Video. PK: `id` (String(36)). [project.py](file:///c:/Hack/AutoTransAI/backend/app/models/project.py#L40)
2. **`segments`:** Đoạn kịch bản. PK: `id` (Integer Auto), FK: `project_id -> projects.id`. [segment.py](file:///c:/Hack/AutoTransAI/backend/app/models/segment.py#L24)
3. **`jobs`:** Tác vụ sinh audio/video/sync. PK: `id` (String(36)), FK: `project_id`, `segment_id`. [job.py](file:///c:/Hack/AutoTransAI/backend/app/models/job.py#L31)
4. **`assets`:** File phương tiện sinh ra. PK: `id` (String(36)), FK: `project_id`, `segment_id`. [asset.py](file:///c:/Hack/AutoTransAI/backend/app/models/asset.py#L11)
5. **`providers`:** Cấu hình & Quota của Provider. PK: `id` (String(50)). [provider.py](file:///c:/Hack/AutoTransAI/backend/app/models/provider.py#L11)
6. **`usage_snapshots`:** Lịch sử tiêu thụ tài nguyên AI. PK: `id` (Integer Auto), FK: `provider_id`. [usage_snapshot.py](file:///c:/Hack/AutoTransAI/backend/app/models/usage_snapshot.py#L11)
7. **`errors`:** Log vết lỗi & traceback. PK: `id` (Integer Auto), FK: `job_id`. [error.py](file:///c:/Hack/AutoTransAI/backend/app/models/error.py#L11)
8. **`video_assets`:** Video nhập từ URL/Upload. PK: `id` (String(36)). [video_translator.py](file:///c:/Hack/AutoTransAI/backend/app/models/video_translator.py#L47)
9. **`video_translation_jobs`:** Job dịch & lồng tiếng video. PK: `id` (String(36)), FK: `asset_id`. [video_translator.py](file:///c:/Hack/AutoTransAI/backend/app/models/video_translator.py#L82)
10. **`video_translation_segments`:** Đoạn transcript & bản dịch lồng tiếng. PK: `id` (Integer Auto), FK: `job_id`. [video_translator.py](file:///c:/Hack/AutoTransAI/backend/app/models/video_translator.py#L132)
11. **`video_edit_configs`:** Cấu hình Ratio, Logo, BGM, Subtitles. PK: `id` (String(36)). [video_editor.py](file:///c:/Hack/AutoTransAI/backend/app/models/video_editor.py#L50)
12. **`qc_reports`:** Báo cáo điểm số QC LUFS & Sync. PK: `id` (String(36)). [video_editor.py](file:///c:/Hack/AutoTransAI/backend/app/models/video_editor.py#L88)
13. **`youtube_channels`:** Kênh YouTube & OAuth Token. PK: `id` (String(36)). [video_editor.py](file:///c:/Hack/AutoTransAI/backend/app/models/video_editor.py#L112)
14. **`youtube_publications`:** Thông tin video đã đăng YouTube. PK: `id` (String(36)), FK: `channel_id`. [video_editor.py](file:///c:/Hack/AutoTransAI/backend/app/models/video_editor.py#L126)
15. **`project_glossaries`:** Từ điển thuật ngữ dự án. PK: `id` (String(36)), FK: `project_id`. [workflow_engine.py](file:///c:/Hack/AutoTransAI/backend/app/models/workflow_engine.py#L46)
16. **`speaker_voice_mappings`:** Ánh xạ giọng nhân vật. PK: `id` (String(36)), FK: `project_id`. [workflow_engine.py](file:///c:/Hack/AutoTransAI/backend/app/models/workflow_engine.py#L71)
17. **`workflow_executions`:** Vết chạy 6-Stage Workflow Engine. PK: `id` (String(36)), FK: `project_id`. [workflow_engine.py](file:///c:/Hack/AutoTransAI/backend/app/models/workflow_engine.py#L94)
18. **`workflow_stage_executions`:** Trạng thái từng Stage. PK: `id` (String(36)), FK: `workflow_execution_id`. [workflow_engine.py](file:///c:/Hack/AutoTransAI/backend/app/models/workflow_engine.py#L124)
19. **`workflow_step_executions`:** Kết quả từng Step trong Stage. PK: `id` (String(36)), FK: `stage_execution_id`. [workflow_engine.py](file:///c:/Hack/AutoTransAI/backend/app/models/workflow_engine.py#L154)
20. **`system_settings`:** Cấu hình hệ thống key-value (Storage, Processing, Workflow Defaults). [settings.py](file:///c:/Hack/AutoTransAI/backend/app/models/settings.py#L14)
21. **`ai_function_configs`:** Ánh xạ cấu hình AI Functions (STT, Translation, TTS, Video Gen). [settings.py](file:///c:/Hack/AutoTransAI/backend/app/models/settings.py#L27)
22. **`ai_models`:** Danh mục mô hình AI mặc định và custom models. [settings.py](file:///c:/Hack/AutoTransAI/backend/app/models/settings.py#L42)
23. **`social_accounts`:** Danh sách kênh truyền thông xã hội (YouTube, TikTok, FB, IG). [settings.py](file:///c:/Hack/AutoTransAI/backend/app/models/settings.py#L57)

- **Source Reference:** [database.py](file:///c:/Hack/AutoTransAI/backend/app/database.py), [models/__init__.py](file:///c:/Hack/AutoTransAI/backend/app/models/__init__.py)


---

## # 8 COMPLETE FEATURE INVENTORY

| Module | Feature | Frontend | Backend | Database | AI / Service | Status |
|---|---|---|---|---|---|---|
| Video Translator | Import URL (YouTube/TikTok) | VideoTranslator.jsx | video_translator.py | video_assets | VideoSourceService | CODE EXISTS - VERIFIED |
| Video Translator | File Upload Local | VideoTranslator.jsx | video_translator.py | video_assets | StorageService | CODE EXISTS - VERIFIED |
| Video Translator | Speech-to-Text (STT) | VideoTranslator.jsx | analyze_stage.py | video_translation_segments | Gemini STT (No auto-fallback to Whisper) | CODE EXISTS - VERIFIED |
| Video Translator | Translation & Glossary | ProjectGlossaryManager.jsx | translate_stage.py | project_glossaries | Gemini LLM | CODE EXISTS - VERIFIED |
| Video Translator | TTS Dubbing | VideoTranslator.jsx | dub_stage.py | video_translation_segments | Edge / Google / ElevenLabs | CODE EXISTS - VERIFIED |
| Video Translator | Audio Sync & atempo | N/A (Auto) | sync_service.py | N/A | FFmpeg atempo | CODE EXISTS - VERIFIED |
| Video Studio | Reframing (9:16 / 16:9 / 1:1) | VideoEditorStudio.jsx | edit_service.py | video_edit_configs | FFmpeg crop/scale | CODE EXISTS - VERIFIED |
| Video Studio | Watermark Logo Overlay | VideoEditorStudio.jsx | edit_service.py | video_edit_configs | FFmpeg overlay | CODE EXISTS - VERIFIED |
| Video Studio | BGM Music & Ducking | VideoEditorStudio.jsx | edit_service.py | video_edit_configs | FFmpeg sidechain | CODE EXISTS - VERIFIED |
| Video Studio | LUFS & Black Frame QC | AIQCScorecard.jsx | qc_service.py | qc_reports | FFmpeg ebur128 | CODE EXISTS - VERIFIED |
| Publishing | Gemini SEO Generation | YouTubePublisherModal.jsx | youtube_service.py | youtube_publications | Gemini LLM | CODE EXISTS - VERIFIED |
| Publishing | YouTube OAuth Upload | YouTubePublisherModal.jsx | youtube_service.py | youtube_publications | YouTube API v3 | PARTIAL (Cần OAuth Key) |
| Settings & AI System | Settings & AI Management Studio | Settings.jsx | settings.py / providers.py | system_settings / providers / ai_models | SettingsService & KeyManager | CODE EXISTS - VERIFIED |

- **Source Reference:** [UNIFIED_WORKFLOW_IMPLEMENTATION_REPORT.md](file:///c:/Hack/AutoTransAI/UNIFIED_WORKFLOW_IMPLEMENTATION_REPORT.md)

---

## # 9 AI SYSTEM ARCHITECTURE

Kiến trúc AI Provider được thiết kế theo Provider Pattern kết hợp KeyManager Failover:
1. **Provider Registry:** Subsystem Singleton [registry.py](file:///c:/Hack/AutoTransAI/backend/app/providers/registry.py#L12) lưu trữ danh sách các Provider.
2. **KeyManager Failover System:** Class Singleton [KeyManager](file:///c:/Hack/AutoTransAI/backend/app/services/key_manager.py#L111) quản lý danh sách nhiều API Keys per Provider với thứ tự ưu tiên (priority).
   - Tự động reset key bị 429 sau 60 giây cooldown (`cooldown_until`).
   - Đánh dấu key `INVALID` nếu nhận HTTP 401/403.
   - Đánh dấu key `EXHAUSTED` nếu hết số dư/ngân sách.

- **Source Reference:** [registry.py](file:///c:/Hack/AutoTransAI/backend/app/providers/registry.py), [key_manager.py](file:///c:/Hack/AutoTransAI/backend/app/services/key_manager.py)

---

## # 10 AI PROVIDERS

1. **`EdgeTTSProvider` (Audio):** Miễn phí hoàn toàn qua `edge-tts` package. [edge_tts_provider.py](file:///c:/Hack/AutoTransAI/backend/app/providers/audio/edge_tts_provider.py#L22)
2. **`GoogleCloudTTSProvider` (Audio):** Sử dụng `GOOGLE_CLOUD_TTS_API_KEY`. [google_tts_provider.py](file:///c:/Hack/AutoTransAI/backend/app/providers/audio/google_tts_provider.py#L22)
3. **`ElevenLabsAudioProvider` (Audio):** Sử dụng `ELEVENLABS_API_KEY`. [elevenlabs_provider.py](file:///c:/Hack/AutoTransAI/backend/app/providers/audio/elevenlabs_provider.py#L20)
4. **`GeminiLLMProvider` (LLM & STT):** Sử dụng `GEMINI_API_KEY` với SDK `google-genai`. [gemini_provider.py](file:///c:/Hack/AutoTransAI/backend/app/providers/llm/gemini_provider.py#L19)
5. **`OpenAILLMProvider` (LLM & STT):** Sử dụng `OPENAI_API_KEY` với SDK `openai`. [openai_provider.py](file:///c:/Hack/AutoTransAI/backend/app/providers/llm/openai_provider.py#L19)
6. **`KlingVideoProvider` (Video):** Gọi `https://api.klingai.com/v1/videos/text2video`. [kling_provider.py](file:///c:/Hack/AutoTransAI/backend/app/providers/video/kling_provider.py#L23)
7. **`FalVideoProvider` (Video):** Gọi `fal-ai/hunyuan-video`. [fal_provider.py](file:///c:/Hack/AutoTransAI/backend/app/providers/video/fal_provider.py#L23)
8. **`LocalVideoProvider` (Video):** Mock local provider. [local_provider.py](file:///c:/Hack/AutoTransAI/backend/app/providers/video/local_provider.py#L19)

- **Source Reference:** [backend/app/providers/](file:///c:/Hack/AutoTransAI/backend/app/providers)

---

## # 11 AI MODELS

- **Gemini:** `gemini-2.5-flash` (Dịch thuật nhanh & Audio STT), `gemini-1.5-pro` (Dịch thuật ngữ cảnh sâu).
- **OpenAI:** `gpt-4o`, `gpt-4o-mini`, `whisper-1` (Speech-to-Text).
- **Video:** `kling-v1`, `fal-ai/hunyuan-video`.

- **Source Reference:** [gemini_provider.py](file:///c:/Hack/AutoTransAI/backend/app/providers/llm/gemini_provider.py), [openai_provider.py](file:///c:/Hack/AutoTransAI/backend/app/providers/llm/openai_provider.py)

---

## # 12 API KEY MANAGEMENT

- **Lưu trữ:** Key khởi tạo từ `.env`, sau đó duy trì trạng thái trong `data/api_keys.json`. Đồng bộ 2 chiều khi chỉnh sửa trên UI.
- **Bảo mật:** Hàm `masked_key` ([key_manager.py](file:///c:/Hack/AutoTransAI/backend/app/services/key_manager.py#L68)) ẩn bớt ký tự trước khi trả về Frontend (VD: `AIza-***-8x9Y`).

- **Source Reference:** [key_manager.py](file:///c:/Hack/AutoTransAI/backend/app/services/key_manager.py)

---

## # 13 VIDEO / MEDIA PROCESSING PIPELINE

Workflow 6 Stage điều khiển bởi `WorkflowEngine`:
1. **`IngestStage`:** Download URL / Import file -> Trích xuất audio track 16kHz WAV. [ingest_stage.py](file:///c:/Hack/AutoTransAI/backend/app/workflow/stages/ingest_stage.py)
2. **`AnalyzeStage`:** Chạy Gemini STT / Whisper -> Tạo danh sách video_translation_segments. [analyze_stage.py](file:///c:/Hack/AutoTransAI/backend/app/workflow/stages/analyze_stage.py)
3. **`TranslateStage`:** Áp dụng Glossaries -> Dịch thuật ngữ cảnh bằng Gemini. [translate_stage.py](file:///c:/Hack/AutoTransAI/backend/app/workflow/stages/translate_stage.py)
4. **`DubStage`:** Áp dụng SpeakerVoiceMapping -> Sinh file TTS audio -> Kéo giãn `atempo` -> Ghép timeline PCM 44.1kHz stereo. [dub_stage.py](file:///c:/Hack/AutoTransAI/backend/app/workflow/stages/dub_stage.py)
5. **`ProduceStage`:** Reframing (9:16/16:9) -> Thêm Logo/Subtitles ASS -> Mix BGM ducking -> Render video lồng tiếng final -> QC LUFS. [produce_stage.py](file:///c:/Hack/AutoTransAI/backend/app/workflow/stages/produce_stage.py)
6. **`PublishStage`:** Sinh SEO Title/Tags -> Kiểm tra OAuth -> Upload YouTube. [publish_stage.py](file:///c:/Hack/AutoTransAI/backend/app/workflow/stages/publish_stage.py)

- **Source Reference:** [backend/app/workflow/stages/](file:///c:/Hack/AutoTransAI/backend/app/workflow/stages)

---

## # 14 API ARCHITECTURE

Danh sách các nhóm REST Endpoints chính:
- **Video Translator:** `/api/video-translator/check-url`, `/import`, `/jobs`, `/jobs/{id}/start`, `/jobs/{id}/render`, `/jobs/{id}/cancel`, `/jobs/{id}/retry`. [video_translator.py](file:///c:/Hack/AutoTransAI/backend/app/api/routes/video_translator.py)
- **Providers & Keys:** `/api/providers`, `/api/providers/{id}/config`, `/api/providers/{id}/keys`, `/api/providers/{id}/keys/{k_id}/test`. [providers.py](file:///c:/Hack/AutoTransAI/backend/app/api/routes/providers.py)
- **Projects:** `/api/projects`, `/api/projects/batch-delete`, `/api/projects/{id}/estimate`, `/api/projects/{id}/precheck`, `/api/projects/{id}/run`. [projects.py](file:///c:/Hack/AutoTransAI/backend/app/api/routes/projects.py)
- **Video Editor & Publishing:** `/api/video-editor/config`, `/upload-logo`, `/jobs/{id}/run-qc`, `/jobs/{id}/publish-youtube`. [video_editor.py](file:///c:/Hack/AutoTransAI/backend/app/api/routes/video_editor.py)
- **System & Storage:** `/api/system/health`, `/api/system/interrupted`, `/api/storage/files/{file_path:path}`. [system.py](file:///c:/Hack/AutoTransAI/backend/app/api/routes/system.py), [storage.py](file:///c:/Hack/AutoTransAI/backend/app/api/routes/storage.py)

- **Source Reference:** [backend/app/api/routes/](file:///c:/Hack/AutoTransAI/backend/app/api/routes)

---

## # 15 STORAGE ARCHITECTURE

- **Local Storage:** `data/projects/{project_id}/` và `data/translator/assets/` & `data/translator/jobs/{job_id}/`.
- **Cloud Storage:** Cloudflare R2 bucket `workflowvdai` qua boto3 client trong [storage_service.py](file:///c:/Hack/AutoTransAI/backend/app/services/storage_service.py#L25).
- **Cleanup:** Class `FileCleanupService` ([cleanup_service.py](file:///c:/Hack/AutoTransAI/backend/app/services/cleanup_service.py#L20)) tự động xóa sạch file local, record DB, và R2 object khi xóa dự án.

- **Source Reference:** [storage_service.py](file:///c:/Hack/AutoTransAI/backend/app/services/storage_service.py), [cleanup_service.py](file:///c:/Hack/AutoTransAI/backend/app/services/cleanup_service.py)

---

## # 16 SETTINGS SYSTEM & AI PROVIDER MANAGEMENT

Màn hình [Settings.jsx](file:///c:/Hack/AutoTransAI/frontend/src/pages/Settings.jsx) là một **Settings Studio** đa tab hoàn chỉnh (Glassmorphism Dark UI) kết nối với REST API `/api/settings` và `/api/providers`:

1. **🤖 AI & API Providers:** Quản lý Multi-Key Pool cho tất cả provider (Gemini, OpenAI, ElevenLabs, Google Cloud TTS, Edge TTS, Kling, fal.ai, Custom Providers). Hỗ trợ xem key mờ (`AIza****XXXX`), thêm key, đổi priority, bật/tắt status, test connection, quota info, và thêm Custom Provider. Key Rotation chỉ kích hoạt khi bị lỗi `429 Rate Limit` hoặc `Quota Exceeded`.
2. **⚡ AI Function Configuration:** Ánh xạ chức năng AI (`STT`, `Translation`, `TTS`, `Video Generation`, `Image Generation`) tới Provider & Model tương thích. Dropdown lọc các provider **Supported + Enabled + Key Configured + Capable**. STT mặc định dùng **Google Gemini**; khi Fallback bị tắt, lỗi Gemini sẽ dừng pipeline ngay mà không tự động gọi OpenAI/Whisper.
3. **🧠 AI Models Catalog:** Danh mục mô hình AI hệ thống và custom models. Cho phép thêm Custom Model, quản lý model mặc định per capability.
4. **📱 Social Accounts Manager:** Quản lý danh sách tài khoản/kênh YouTube, TikTok, Facebook, Instagram.
5. **☁️ Storage Settings:** Cấu hình Local Storage vs Cloudflare R2 Persistent Storage (S3 API). Hỗ trợ nút **Test Storage Connection**.
6. **⚙️ Processing Settings:** Concurrency max, Retries, Retry Backoff, Target Video Clip Duration, Audio Format/Sample Rate, Sync Strategy (`trim_video`, `loop_video`, `pad_video`, `speed_video`), Sync Tolerance.
7. **🎯 Workflow Defaults:** Ngôn ngữ nguồn/đích mặc định, giọng đọc TTS mặc định, video provider mặc định.
8. **🛠️ Advanced:** Trạng thái Database (SQLite WAL mode), dynamic DDL inspector listener (`_sync_schema_sync`), và kiểm tra System Health.

- **Source Reference:** [Settings.jsx](file:///c:/Hack/AutoTransAI/frontend/src/pages/Settings.jsx), [settings.py](file:///c:/Hack/AutoTransAI/backend/app/api/routes/settings.py), [settings_service.py](file:///c:/Hack/AutoTransAI/backend/app/services/settings_service.py), [key_manager.py](file:///c:/Hack/AutoTransAI/backend/app/services/key_manager.py)


---

## # 17 ENVIRONMENT VARIABLES

Các biến môi trường cấu hình trong [.env](file:///c:/Hack/AutoTransAI/.env):
- `GEMINI_API_KEY`: Key cho Google Gemini LLM & Audio STT.
- `OPENAI_API_KEY`: Key cho OpenAI (GPT-4o, Whisper).
- `GOOGLE_CLOUD_TTS_API_KEY`: Key cho Google Cloud TTS.
- `ELEVENLABS_API_KEY`: Key cho ElevenLabs.
- `KLING_API_KEY`: Key cho Kling AI Video.
- `FAL_API_KEY`: Key cho fal.ai Video.
- `DEFAULT_LLM_PROVIDER`: Provider LLM mặc định (`gemini`).
- `DATABASE_URL`: URL kết nối SQLite (`sqlite+aiosqlite:///data/workflow.db`).
- `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET_NAME`: Cấu hình Cloudflare R2 Storage.

- **Source Reference:** [.env.example](file:///c:/Hack/AutoTransAI/.env.example), [config.py](file:///c:/Hack/AutoTransAI/backend/app/config.py#L30)

---

## # 18 IMPORTANT DATA FLOWS

1. **Video Translation Flow:** Import Video -> Audio Extraction (16kHz WAV) -> Gemini STT -> Glossary Translation -> Multi-voice TTS Synthesis -> Audio `atempo` sync -> PCM 44.1kHz timeline assembly -> FFmpeg render video lồng tiếng -> Local/R2 storage.
2. **Key Rotation Flow on HTTP 429:** Request AI Provider -> Nhận 429 -> KeyManager chuyển status key sang `RATE_LIMITED` (cooldown 60s) -> KeyManager chọn key `READY` có priority cao nhất tiếp theo -> Tái thực hiện Request thành công.

- **Source Reference:** [translator_service.py](file:///c:/Hack/AutoTransAI/backend/app/services/video_translator/translator_service.py), [key_manager.py](file:///c:/Hack/AutoTransAI/backend/app/services/key_manager.py#L283)

---

## # 19 IMPORTANT SERVICES

- `KeyManager`: [key_manager.py](file:///c:/Hack/AutoTransAI/backend/app/services/key_manager.py#L111)
- `StorageService`: [storage_service.py](file:///c:/Hack/AutoTransAI/backend/app/services/storage_service.py#L25)
- `FileCleanupService`: [cleanup_service.py](file:///c:/Hack/AutoTransAI/backend/app/services/cleanup_service.py#L20)
- `VideoSourceService`: [service.py](file:///c:/Hack/AutoTransAI/backend/app/services/video_source/service.py#L22)
- `VideoTranslatorService`: [translator_service.py](file:///c:/Hack/AutoTransAI/backend/app/services/video_translator/translator_service.py)
- `VideoEditorService`: [edit_service.py](file:///c:/Hack/AutoTransAI/backend/app/services/video_editor/edit_service.py#L17)
- `QCService`: [qc_service.py](file:///c:/Hack/AutoTransAI/backend/app/services/video_editor/qc_service.py#L18)
- `YouTubePublisherService`: [youtube_service.py](file:///c:/Hack/AutoTransAI/backend/app/services/video_editor/youtube_service.py#L19)

---

## # 20 TECHNICAL DEBT

1. **Task Queue:** Hiện dùng `asyncio.create_task` và `BackgroundTasks`. Khi cần mở rộng ngang đa nút (horizontal scaling), nên thay thế bằng Celery/Redis queue.
2. **SQLite Concurrent Writes:** Đã bật WAL mode nhưng ghi đồng thời quá lớn vẫn cần chuyển sang PostgreSQL/MySQL.

---

## # 21 SECURITY NOTES

1. **Plain Text API Keys:** Key được lưu trong `.env` và `data/api_keys.json` dưới dạng plain text. Cần phân quyền truy cập file trên OS.
2. **SSRF Validation:** Hệ thống có module [security_url.py](file:///c:/Hack/AutoTransAI/backend/app/core/security_url.py#L35) bảo vệ ứng dụng khỏi rủi ro SSRF khi người dùng nhập URL video ngoài internet.

---

## # 22 CURRENT KNOWN ISSUES

- YouTube Upload yêu cầu cấu hình OAuth client credentials chính xác mới có thể đăng video công khai thành công. Nếu không có credentials, Stage 6 trả về trạng thái `PUBLISHING_BLOCKED`.

---

## # 23 FUTURE EXTENSION GUIDE

Để thêm một Audio/TTS Provider mới:
1. Tạo class mới kế thừa từ `AudioProvider` trong `backend/app/providers/audio/`.
2. Implement các hàm: `validate_configuration()`, `get_voices()`, `synthesize()`.
3. Đăng ký Provider mới tại hàm `lifespan()` trong [main.py](file:///c:/Hack/AutoTransAI/backend/app/main.py#L55).

- **Source Reference:** [base.py](file:///c:/Hack/AutoTransAI/backend/app/providers/base.py#L42), [main.py](file:///c:/Hack/AutoTransAI/backend/app/main.py#L51)

---

## # 24 CHANGE SUMMARY

- Khởi tạo hệ thống Project Knowledge Base chuẩn hóa cho AI Agents & Humans.
- Tạo các file kiến trúc: `AGENTS.md`, `PROJECT_KNOWLEDGE_BASE.md`, `CHANGELOG_AI.md`, `docs/PROJECT_KNOWLEDGE_BASE.docx`.
