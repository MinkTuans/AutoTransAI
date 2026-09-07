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
6. **PUBLISH**: YouTube SEO metadata generation, thumbnail selection, user review gate, YouTube publication via OAuth / upload service.

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
- Project Settings Endpoints: `GET /api/projects/{project_id}/settings`, `POST /api/projects/{project_id}/settings`, `PUT /api/projects/{project_id}/settings` (enforces single source of truth, `DEFAULT_PROJECT_SETTINGS` fallback, numeric boundary validation, and emits structured debug logs `[PROJECT SETTINGS LOAD]` and `[PROJECT SETTINGS SAVE]`).
- Watermark Asset Storage: `POST /api/video-translator/upload-watermark-logo` stores files under `storage/projects/{project_id}/assets/watermarks/`, creates `Asset` DB records (`asset_type="watermark_logo"`), and links `watermark_image_asset_id` directly in project `settings_json`.
- Workflow Execution Snapshotting: `POST /api/video-translator/projects/{project_id}/workflow/start` freezes project settings into `WorkflowExecution.context_data["settings_snapshot"]` so active executions remain isolated from post-start settings edits.
- Project Detail & Management API: `GET /api/projects/{project_id}` returns project metadata, normalized settings, list of associated videos (`videos`), segments array, and glossary stats (`glossary_count`, `terminology_count`).
- Projects List Endpoint: `GET /api/projects` (Supports optional server-side pagination params: `page: int`, `page_size: int` defaulting to 8 items per page, returning `total`, `page`, `page_size`, `total_pages`).

### AI Model Routing & Single Source of Truth Architecture
- **Configuration Priority Hierarchy**:
  `REQUESTED MODEL` -> `DATABASE AI FUNCTION CONFIG (ai_function_configs)` -> `ENVIRONMENT DEFAULT (GEMINI_STT_MODEL/GEMINI_MODEL)` -> `HARDCODED SAFE DEFAULT (gemini-2.5-flash)`
- **Unified Resolution Engine**:
  - `AIRouter.resolve_stt_model(db, requested_model)` resolves active STT provider & model.
  - `normalize_gemini_model_name(model_name)` normalizes model strings (`models/gemini-2.5-flash` -> `gemini-2.5-flash`) and auto-migrates deprecated model strings (`gemini-2.0-flash` -> `gemini-2.5-flash`).
- **Runtime Request Trace Logging**:
  - Every STT execution logs exact diagnostic traces: `[STT CONFIG]`, `[STT ROUTING]`, and `[STT API REQUEST]` verifying actual model requested from AI providers.

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
- **Smart Retry Error Handling**:
  - When a workflow stage execution fails, the Error Message Card displays the exact stage error message and error details directly beneath `WorkflowTimeline.jsx`.
  - Clicking `🔄 Smart Retry` triggers stage-level retry (`POST /api/video-translator/projects/{project_id}/workflow/stage/{stage_name}/retry`) resuming execution directly from the failed stage.
