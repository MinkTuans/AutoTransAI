# AutoTransAI - Project Knowledge Base

## System Architecture

AutoTransAI (WorkflowVdAi) is a local-first AI Video Translation & Dubbing Production system built with a FastAPI backend and a React (Vite) frontend.

### Unified 6-Stage Workflow Pipeline Engine
The central engine (`app.workflow.workflow_engine.WorkflowEngine`) orchestrates six sequential stages:
1. **INGEST**: Import video, validate file/URL, probe media specs via FFprobe, store asset, extract WAV audio.
2. **ANALYZE**: Speech-to-Text (STT via Gemini / Whisper fallback), language detection, speaker diarization, timeline validation & cleanup, transcript QC.
3. **TRANSLATE**: Project glossary loading, entity extraction, cross-batch context translation into target language (e.g., Vietnamese), segment ID drop validation and recovery, translation QC.
4. **DUB**: Speaker-voice mapping, TTS synthesis (Edge-TTS, Google Cloud TTS, ElevenLabs), duration analysis, atempo time stretching, sample-accurate 44.1kHz stereo PCM timeline assembly, audio normalization, dubbing QC.
5. **PRODUCE**: Subtitle generation (ASS/SRT/VTT), reframing, watermark/logo embedding, final FFmpeg video rendering & multiplexing, technical QC.
6. **PUBLISH**: YouTube SEO metadata generation (Gemini API), thumbnail selection, user review gate. Supports true Google OAuth 2.0 connection, encrypted token storage (via `cryptography.fernet`), and async background resumable uploads via `YouTubePublishingService` tracking progress dynamically directly into `youtube_publications` database table (supporting both `job_id` and `project_id` relationship tracking).

### Database & File Storage Architecture (100% Local & Self-Contained)
- **Database Layer (Laragon MySQL)**:
  - Primary connection: `mysql+aiomysql://root:210606@127.0.0.1:3306/autotransai` (configured via `DATABASE_URL` in `.env`).
  - Automatic dialect handling with `pool_pre_ping=True`, `pool_recycle=3600`, and MySQL backtick DDL migrations.
  - Automatic graceful fallback to local SQLite (`sqlite+aiosqlite:///data/workflow.db`) if MySQL service is stopped.
  - **Zero Supabase Dependency**: Completely eliminated `supabase-js`, `supabase-py`, PostgreSQL Supabase connection URLs, and cloud database dependencies.
- **File Storage System (Local Disk Storage)**:
  - Root directory: `storage/` (`STORAGE_ROOT`).
  - Standardized project subdirectories under `storage/projects/{project_id}/`:
    - `videos/source/` & `videos/processed/`
    - `audio/original/`, `audio/extracted/`, & `audio/dubbed/`
    - `subtitles/`
    - `thumbnails/`
    - `outputs/`
    - `temporary/`
  - Local streaming API: `GET /api/storage/files/{file_path:path}` serves media files via FastAPI `FileResponse`.

### Database Persistence Model
- `Project` (`projects`): Top-level project entity supporting `title`, `description`, `workflow_mode`, `workflow_status`, `settings_json` for reusable configuration, and timestamps.
- `ProjectTerminologyMemory` (`project_terminology_memory`): AI auto-detected entity terminology terms with `source_term`, `suggested_term`, `term_type`, `confidence`, and `needs_review`.
- `WorkflowExecution` (`workflow_executions`): Top-level record tracking `project_id`, `status` (`not_started`, `running`, `paused`, `needs_review`, `failed`, `completed`, `cancelled`), `current_stage`, `current_step`, `context_data`, `error_message`, and timestamps.
- `VideoTranslationJob` (`video_translation_jobs`): Per-video execution job tracking `project_id`, `asset_id`, `status`, `stage`, `settings_snapshot_json` (isolated configuration snapshot taken at job creation), `studio_state_json` (persisted UI step, active tab, selected segment ID), `last_checkpoint_stage` (`CREATED`, `EXTRACTING_AUDIO_DONE`, `STT_DONE`, `TRANSLATION_DONE`, `SEGMENT_EDITING_DONE`, `TTS_DONE`, `AUDIO_SYNC_DONE`, `RENDER_DONE`), `last_checkpoint_at`, watermark options, and timestamps.
- `WorkflowStageExecution` (`workflow_stage_executions`): Tracks individual stage status (`pending`, `running`, `passed`, `failed`, `needs_review`, `skipped`), QC reports, and retry counts.
- `WorkflowStepExecution` (`workflow_step_executions`): Fine-grained step execution tracking with status (`pending`, `running`, `success`, `failed`, `retrying`, `skipped`), input/output data payloads, and step retry counts.

### Real-Time Tracking & APIs
- Pre-flight Endpoint: `POST /api/video-translator/projects/{project_id}/workflow/preflight` (Evaluates CRITICAL vs OPTIONAL check prerequisites).
- Status Endpoint: `GET /api/video-translator/projects/{project_id}/workflow-status`
- Start Endpoint: `POST /api/video-translator/projects/{project_id}/workflow/start` (accepts `StartWorkflowRequest` configuration)
- Pause Endpoint: `POST /api/video-translator/projects/{project_id}/workflow/pause`
- Resume Endpoint: `POST /api/video-translator/projects/{project_id}/workflow/resume`
- Cancel Endpoint: `POST /api/video-translator/projects/{project_id}/workflow/cancel`
- Retry Stage Endpoint: `POST /api/video-translator/projects/{project_id}/workflow/stage/{stage_name}/retry`
- Project Settings Endpoints: `GET /api/projects/{project_id}/settings`, `POST /api/projects/{project_id}/settings`, `PUT /api/projects/{project_id}/settings` (enforces single source of truth, `DEFAULT_PROJECT_SETTINGS` fallback, strict `_parse_bool` boolean string normalization for `watermark_enabled` / `thumbnail_enabled`, numeric boundary validation, and emits structured debug logs `[PROJECT SETTINGS LOAD]` and `[PROJECT SETTINGS SAVE]`).
- Watermark Asset Storage & Path Resolution: `POST /api/video-translator/upload-watermark-logo` stores files under `storage/projects/{project_id}/assets/watermarks/`, creates `Asset` DB records (`asset_type="watermark_logo"`), and links `watermark_image_asset_id` directly in project `settings_json`. `WatermarkService.resolve_watermark_image_path` safely resolves relative paths against `STORAGE_ROOT` and `DATA_DIR`.
- Workflow Context & Stage Execution Order: `WorkflowContext` serializes and preserves `watermark_enabled`, `watermark_type`, `watermark_image_path`, etc., across all stages. In `ProduceStage`, `final_render` (dubbed video multiplexing) executes before `add_watermark_logo` so the watermark overlay pass is burned directly onto the final dubbed video.
- Project Detail & Management API: `GET /api/projects/{project_id}` returns project metadata, normalized settings, list of associated videos (`videos`), segments array, and glossary stats (`glossary_count`, `terminology_count`).
- Projects List Endpoint: `GET /api/projects` (Supports optional server-side pagination params: `page: int`, `page_size: int` defaulting to 8 items per page, returning `total`, `page`, `page_size`, `total_pages`).

### AI Model Routing & Single Source of Truth Architecture
- **Configuration Priority Hierarchy**:
  `REQUESTED MODEL` (explicit override) -> `SETTINGS DATABASE (ai_function_configs / ai_models)` -> `PipelineError` (Structured `AI_MODEL_NOT_FOUND` exception if model is not configured in DB).
- **Unified Resolution Engine**:
  - `AIModelResolver` (`app.services.model_resolver`) is the sole authoritative single-source-of-truth for resolving AI Models (STT, LLM, TTS, Image, Video) strictly from Database tables (`ai_function_configs` -> `ai_models`).
  - Automatically acquires an async database session if `db` parameter is omitted, querying active DB configuration directly.
  - Zero hardcoded fallback model strings (e.g. `gemini-2.5-flash`) or candidate loops (`GEMINI_MODEL_CANDIDATES` removed) exist in resolution routines.
  - `strip_gemini_model_prefix(model_name)` only strips `models/` prefix without modifying or inventing model identifiers.
  - Providers (STT, LLM) accept explicit `model` parameters resolved by `AIModelResolver` and execute API calls against the user's exact database-configured model.
- **Automatic Translation Model Resolution & Double Safety Nets**:
  - `translate_transcript_segments` accepts an optional `db` parameter and automatically invokes `AIModelResolver.resolve_model(db, capability="TRANSLATION")` if `translation_model_id` is omitted.
  - `GeminiLLMProvider.generate_text` features a secondary safety net invoking `AIModelResolver` if `model` is `None` at runtime, preventing `AI_CONFIGURATION_ERROR` pipeline crashes.
- **Runtime Request Trace Logging**:
  - All AI Model resolutions log diagnostic details: capability, selected provider, selected model ID, model name, resolution source, and fallback status.

### Gemini STT Robust Parsing & Resilient Pipeline Architecture
- **Multi-Stage Response Parsing (`app.services.video_translator.stt_parser`)**:
  - `parse_gemini_stt_response` processes raw Gemini API responses through 6 sequential fallback stages:
    1. Strict JSON parsing (`json.loads`).
    2. Markdown code block stripping (` ```json ... ``` `).
    3. Regex object/array extraction (`{...}` / `[...]`) ignoring outer conversational filler text.
    4. Malformed JSON sanitization (removing trailing commas, repairing unescaped newlines/control characters in string literals, fixing Python boolean literals).
    5. Plain-text / timestamped dialogue fallback parser (`[00:00 - 00:05] Text` or plain text block).
    6. Schema normalization (mapping `items`, `transcript`, `dialogue`, `sentences` -> `segments`; mapping `lang`, `language_code` -> `language`).
- **Gemini API JSON Enforcement**:
  - `transcribe_audio_with_gemini` includes `generationConfig: {"response_mime_type": "application/json", "temperature": 0.1}` in API request payloads.
- **Enhanced Debug & Log Traceability**:
  - Raw Gemini response snippets (first 1000 characters) are logged to `logger.error` and `log_job_event` when parsing exceptions occur.

### Frontend Workflow UI Controls & Smart Retry Flow
- **Button State Machine**:
  - `not_started`, `completed`, `cancelled`, `failed`: Displays only `▶ Start Workflow` button.
  - `running`: Displays `⏸ Pause` and `🛑 Cancel` buttons.
  - `paused`: Replaces `Pause` with `▶ Resume` button while retaining `🛑 Cancel`.
  - **Optimistic State Transition**: Clicking `▶ Start Workflow` immediately triggers optimistic frontend status set (`status: 'running'`), ensuring instant visual action response without lag.
- **Unified Workflow Layout Hierarchy**:
  1. `Unified 6-Stage Workflow Pipeline` (`WorkflowTimeline.jsx`): Always fixed and expanded at the top.
  2. `Error Message Card` (`❌ Xử Lý Thất Bại`): Positioned directly beneath `WorkflowTimeline.jsx` when workflow state is `failed`.
  3. `Job Progress Panel` (`📊 Tiến Trình Xử Lý Pipeline (Job: ...)`): Positioned directly beneath Error Card, rendering overall progress, stage details, and debug telemetry.
  4. `Collapsible Configuration & Control Cards`: Section cards (`⚙️ Cấu hình Nhập Video`, `📖 Quản Lý Thuật Ngữ`, `🖼️ Tạo Thumbnail AI`) feature collapsible accordion controls (`▼ Mở rộng` / `▲ Thu gọn`) for a clean, non-cluttered interface.
- **Stage Execution Animations & Passed States**:
  - **Running Stage**: Highlighted with an animated glowing pulse border (`stagePulseGlow`), animated spinning gear badge (`spinner-icon`), and bright cyan accent.
  - **Passed/Completed Stage**: Rendered with solid emerald green border (`#10B981`), green checkmark badge (`✓ Passed`), and emerald highlight.
- **Smart Retry Error Handling & Global React ErrorBoundary**:
  - Global `ErrorBoundary` class in `main.jsx` catches any uncaught React component render errors, rendering a dark fallback card with error details and a reload button instead of a blank screen.
  - `handleRetryJob` and `handleRetryStage` in `VideoTranslator.jsx` execute `retryJob` or `retryStage` mutually exclusively to prevent concurrent pipeline double-invocations.
  - Backend `retry_stage_api` safeguards job lookup with try-except, gracefully restarting associated jobs without throwing 500 errors.

### Codebase Audit & Unused Component Cleanup
- **Stale Import & Build Fix**: Removed broken `AIThumbnailPanel` imports in `VideoTranslator.jsx` and `ProjectDetail.jsx`, fixing production Vite builds (`npm run build` 100% clean).
- **Unused Directory & Model Cleanup**: Removed obsolete directories `PIPER_MODELS/` (offline TTS experiment), `mdx_models/` (245MB legacy UVR/MDX ONNX models), `scratch/` (temporary test scripts), `docs/` & `PROJECT_KNOWLEDGE_BASE.docx`, and `data/r2_storage/`.
- **Frontend Asset Optimization**: Removed unused starter assets (`hero.png`, `typescript.svg`, `favicon.svg`, `icons.svg`).
- **Backend Dependency & Code Hygiene**: Removed `asyncpg` dependency from `requirements.txt`, removed legacy Postgres string replacement in `database.py`, removed duplicate imports in `main.py`, removed unused imports in `projects.py` and `video_translator.py`, and deleted obsolete scripts (`apply_db_schema.py`, `init_mysql_db.py`).

