# AutoTransAI - Project Knowledge Base

## System Architecture

AutoTransAI (WorkflowVdAi) is a local-first AI Video Translation & Dubbing Production system built with a FastAPI backend and a React (Vite) frontend.

### Unified 6-Stage Workflow Pipeline Engine
The central engine (`app.workflow.workflow_engine.WorkflowEngine`) orchestrates six sequential stages:
1. **INGEST**: Import video, validate file/URL, probe media specs via FFprobe, store asset, extract WAV audio. Optional `copyright_check` (Studio checkbox `copyright_check_enabled`, default on) runs after trim and before STT: platform metadata (YouTube licensedContent, Bilibili `copyright`/tname, film/TV title+duration heuristics) plus Chromaprint/AcoustID if `fpcalc` and `ACOUSTID_API_KEY` exist. Red pauses the Auto job as `copyright_hold` until `POST /jobs/{id}/copyright-continue`; yellow warns and continues. No LLM. SSRF (`security_url`) blocks private/loopback/link-local/metadata; NAT64 `64:ff9b::/96`, IPv4-mapped, and 6to4 are checked via the embedded IPv4 so DNS64 of public CDNs (Bilibili) is not treated as an internal address. Optional `trim_filler` (Studio checkbox `trim_filler_enabled`, default on) scans silence + freeze on the full timeline, confirms head/tail with Gemini when available, then `ffmpeg` stream-copy trims intro/outro into `content_trimmed.mp4` before STT. Original file is kept. Safety: only head/tail, keep at least 40% and 60s, require a ~20s dead zone. URL downloads start via `POST /api/video-translator/transfers` (poll `GET /transfers/{id}` for percent/bytes/speed) then create the translation job. File uploads report browser `onUploadProgress`. Page URLs use `PageURLAdapter`. Bilibili downloads the official `playurl` MP4 (`fnval=1`) with HTTP Range resume; yt-dlp is fallback (Popen, `-c --retries 30 -N 1 --newline`). `VIDEO_DOWNLOAD_TIMEOUT=0` means no wall-clock abort while bytes are still flowing. Reject cached files smaller than 100KB. `asyncio.create_subprocess_exec` is avoided because it raises NotImplementedError on Windows uvicorn. Supported hosts include YouTube, Vimeo, TikTok, Facebook, Instagram, Google Drive, Dropbox, and Bilibili. Bilibili check-url reads `https://api.bilibili.com/x/player/pagelist?bvid=` (`?t=` timestamp, `?p=` part). Download uses browser UA/Referer and `bv*+ba` DASH merge.
2. **ANALYZE**: Speech-to-Text (STT via Gemini / Whisper fallback), language detection, speaker diarization, timeline validation & cleanup, transcript QC.
3. **TRANSLATE**: Detect and normalize terminology, atomically write non-conflicting mappings into the project Glossary, load its canonical 1:1 mappings, translate with those rules in every retry path. Language-aware glossary enforcement: `find_glossary_violations` accepts `source_language` and `target_language`, automatically skips invalid self-mapped CJK entries (e.g. `安妮→安妮` when target is Vietnamese/English) via centralized `is_self_mapped_cjk()` and `is_valid_glossary_mapping()` utilities while preserving legitimate same-term mappings (`AI→AI`, `Netflix→Netflix`). Terminology extractors (`heuristic_extract_terms`, `normalize_extracted_terms`, `llm_extract_terms`) strictly prevent untranslated CJK mappings when target language is non-Chinese. The translation prompt instructs that proper names must be translated/transliterated into target language. Valid glossary violations trigger a targeted 1-step LLM retry with violation feedback; if violations persist after retry, `RuntimeError("GLOSSARY_ENFORCEMENT_FAILED")` is raised. Invalid glossary mappings are skipped with warnings and do not trigger retry loops or crashes. Only valid glossary violations block DUB stage.
4. **DUB**: Speaker-voice mapping, TTS synthesis (Edge-TTS, Google Cloud TTS, ElevenLabs), duration analysis, atempo time stretching, sample-accurate 44.1kHz stereo PCM timeline assembly, audio normalization, dubbing QC.
5. **PRODUCE**: Subtitle generation (ASS/SRT/VTT), reframing, watermark/logo embedding, final FFmpeg video rendering & multiplexing, technical QC, then AI thumbnail generation when `thumbnail_enabled` is on.
6. **PUBLISH**: YouTube SEO metadata generation (Gemini API), thumbnail selection, user review gate. Supports true Google OAuth 2.0 connection, encrypted token storage (via `cryptography.fernet`), and async background resumable uploads via `YouTubePublishingService` tracking progress dynamically directly into `youtube_publications` database table (supporting both `job_id` and `project_id` relationship tracking). TikTok Login Kit OAuth (desktop PKCE, hex SHA256 `code_challenge`) is at `GET /api/tiktok/auth-url`, callback `GET /api/tiktok/oauth-callback`, accounts `GET/DELETE /api/tiktok/accounts`. Tokens are encrypted into `tiktok_accounts`. Settings Social buttons **never** navigate the pywebview / Edge `--app=` window; `POST /api/system/open-browser` allowlists Google/TikTok authorize URLs and launches a new Google Chrome tab (`chrome --new-tab`). Callback returns a close-this-tab HTML page; the app window polls until the account appears. Env: `TIKTOK_CLIENT_KEY`, `TIKTOK_CLIENT_SECRET`, `TIKTOK_REDIRECT_URI=http://127.0.0.1:8000/api/tiktok/oauth-callback`, `TIKTOK_SCOPES=user.info.basic,video.upload,video.publish`.

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
- `ProjectGlossary` (`project_glossaries`): The only project terminology store. Display values are preserved while NFKC/invisible/whitespace/case-normalized SHA-256 keys enforce `UNIQUE(project_id, source_key)` and `UNIQUE(project_id, translation_key)`. Manual edits and AI detection use the same service; identical retries are idempotent and either-direction collisions return conflict without overwrite. Every video job sharing `project_id` loads these canonical mappings before translation.
- `WorkflowExecution` (`workflow_executions`): Top-level record tracking `project_id`, `status` (`not_started`, `running`, `paused`, `needs_review`, `failed`, `completed`, `cancelled`), `current_stage`, `current_step`, `context_data`, `error_message`, and timestamps.
- `VideoTranslationJob` (`video_translation_jobs`): Per-video execution job tracking `project_id`, `asset_id`, `status`, `stage`, `settings_snapshot_json` (isolated configuration snapshot taken at job creation), `studio_state_json` (persisted UI step, active tab, selected segment ID), `last_checkpoint_stage` (`CREATED`, `EXTRACTING_AUDIO_DONE`, `STT_DONE`, `TRANSLATION_DONE`, `SEGMENT_EDITING_DONE`, `TTS_DONE`, `AUDIO_SYNC_DONE`, `RENDER_DONE`), `last_checkpoint_at`, watermark options, and timestamps.
- `WorkflowStageExecution` (`workflow_stage_executions`): Tracks individual stage status (`pending`, `running`, `passed`, `failed`, `needs_review`, `skipped`), QC reports, and retry counts.
- `WorkflowStepExecution` (`workflow_step_executions`): Fine-grained step execution tracking with status (`pending`, `running`, `success`, `failed`, `retrying`, `skipped`), input/output data payloads, and step retry counts.
- `VideoMergeJob` (`video_merge_jobs`): Standalone video merge job tracking `id`, `title`, `status` (`pending`, `preparing`, `processing`, `completed`, `failed`, `cancelled`), `progress` (0-100%), `input_files_json` (ordered array of source video items), `output_video_path`, `output_relative_url`, `total_duration`, `processed_duration`, `error_message`, and timestamps.
- `VideoMergeAsset` (`video_merge_assets`): Storage asset model for video merger uploads tracking `id`, `original_filename`, `file_path`, `file_size`, `duration`, `width`, `height`, `fps`, `has_audio`, `thumbnail_url`, and timestamps.

### Standalone Video Merger Architecture
- **Complete Decoupling**: Completely standalone workflow, page (`VideoMerger.jsx`), and routing (`?page=merger` / `/video-merger`) accessed directly via top-level `Navbar.jsx` menu item `Ghép Video`. Zero dependency on Video Translator workflow state.
- **Resilient FFmpeg Concat & Normalization Engine (`VideoMergerService`)**:
  - Preflight Inspection: Probe each input file via `probe_media_info_async` for file existence, readability, resolution, duration, FPS, codecs, and audio presence.
  - Fast Concat (`-c copy`): Automatically used if all video inputs share identical resolution, frame rate, aspect ratio, codecs, and audio presence.
  - Complex Filter Normalization (`-filter_complex`): If video parameters differ or any video is silent (missing audio), rescales while maintaining aspect ratio with black letterboxing, normalizes FPS to 30, generates synchronized silent audio tracks via `anullsrc=r=44100:cl=stereo:d={duration}`, and concatenates into a unified H.264/AAC output MP4.
  - Real-time Progress: Tracks FFmpeg stdout `out_time_us` via `run_ffmpeg_with_progress_async` streaming progress updates to DB for real-time frontend status polling.
- **Video Merger APIs (`/api/video-merger/*`)**:
  - `POST /api/video-merger/upload`: Upload video file for merging with FFprobe probing and thumbnail frame extraction.
  - `GET /api/video-merger/assets`: List existing system video assets for selection.
  - `POST /api/video-merger/jobs`: Create merge job with ordered video sequence.
  - `POST /api/video-merger/jobs/{job_id}/start`: Start background merge task with double-click submission guard.
  - `GET /api/video-merger/jobs/{job_id}`: Real-time job status polling endpoint.
  - `POST /api/video-merger/jobs/{job_id}/retry`: Retry failed merge job.
- Pre-flight Endpoint: `POST /api/video-translator/projects/{project_id}/workflow/preflight` (Evaluates CRITICAL vs OPTIONAL check prerequisites).
- Status Endpoint: `GET /api/video-translator/projects/{project_id}/workflow-status`
- Start Endpoint: `POST /api/video-translator/projects/{project_id}/workflow/start` (accepts `StartWorkflowRequest` configuration)
- Pause Endpoint: `POST /api/video-translator/projects/{project_id}/workflow/pause`
- Resume Endpoint: `POST /api/video-translator/projects/{project_id}/workflow/resume`
- Cancel Endpoint: `POST /api/video-translator/projects/{project_id}/workflow/cancel`
- Retry Stage Endpoint: `POST /api/video-translator/projects/{project_id}/workflow/stage/{stage_name}/retry`
- Project Settings Endpoints: `GET /api/projects/{project_id}/settings`, `POST /api/projects/{project_id}/settings`, `PUT /api/projects/{project_id}/settings` (enforces single source of truth, `DEFAULT_PROJECT_SETTINGS` fallback, strict `_parse_bool` boolean string normalization for `watermark_enabled` / `thumbnail_enabled` / `auto_confirm_translation` / `youtube_enabled` / `youtube_ai_seo_enabled`, YouTube Channel Name, Title Template with zero-padded `{episode}` order calculation, Description default, Tags merge engine `merge_youtube_tags` case-insensitive deduplication, numeric boundary validation, and emits structured debug logs `[PROJECT SETTINGS LOAD]` and `[PROJECT SETTINGS SAVE]`).
- Automated Translation Text Confirmation (`auto_confirm_translation`): Enabled by default (`True`). Strictly one-shot via `auto_confirm_executed` snapshot flag to prevent duplicate confirmation loops or multiple concurrent render tasks across polling/heartbeats. When Phase 1 (Speech-to-Text & Translation) finishes, backend automatically confirms translated text segments, persists `confirmed` status in DB, and releases job lock before launching Phase 2 (`execute_job_render_pipeline`: TTS dubbing synthesis, time-stretch audio sync, and FFmpeg video rendering). Standalone idempotent helper `auto_confirm_and_start_render_if_needed(job_id)` checks `auto_confirm_executed` and `COMPLETED` terminal guards, guaranteeing seamless transition to `DUB` (`GENERATING_TTS`) without redundant execution.
- Single Source of Truth 6-Stage Workflow Synchronization: `GET /api/video-translator/projects/{project_id}/workflow-status` dynamically resolves lifecycle stages (`INGEST` → `ANALYZE` → `TRANSLATE` → `DUB` → `PRODUCE` → `PUBLISH`) from active `VideoTranslationJob` status (`SEGMENT_EDITING`, `GENERATING_TTS`, `AUDIO_SCHEDULE_REVIEW`, `SYNCING_AUDIO`, `RENDERING`, `COMPLETED`), ensuring stage cards in `WorkflowTimeline.jsx` never freeze at `INGEST` once ingestion sub-steps pass. `AUDIO_SCHEDULE_REVIEW`, `TTS_DONE`, `SYNCING_AUDIO`, and `AUDIO_SYNC_DONE` are correctly mapped to Stage 4 (`DUB`).
- Smart Retry & Phase 2 Resume: `smart_retry_job_api` and `retry_stage_api` inspect `last_checkpoint_stage` and existing segments. If segments are already translated (`TRANSLATION_DONE`, `DUB`, `AUDIO_SCHEDULE_REVIEW`, `SYNCING_AUDIO`), retries resume directly into Phase 2 without deleting segments or re-running Phase 1 STT/translation. Terminal status guards prevent re-execution on already `COMPLETED` jobs.
- Verbatim Echo Safeguards & Targeted Recovery: `is_verbatim_echo()` performs linguistic analysis to detect untranslated source echoes (e.g. CJK outputs when translating Chinese to Vietnamese). When echoes occur (e.g. 22/42 segments echo source text), the pipeline logs `[Translation Audit]`, retries strictly the 22 invalid segments while keeping the 20 valid translations intact, merges the corrected segments, logs `[Translation Retry]`, and completes the job (`[TRANSLATION COMPLETED]`). If echoes persist after max retries, the provider fails cleanly (`Translation validation failed on {provider}: {count}/{total} segments were verbatim echoes.`) and triggers provider failover without resetting job progress or segment indices.


- Watermark Asset Storage & Path Resolution: `POST /api/video-translator/upload-watermark-logo` stores files under `storage/projects/{project_id}/assets/watermarks/`, creates `Asset` DB records (`asset_type="watermark_logo"`), and links `watermark_image_asset_id` directly in project `settings_json`. `WatermarkService.resolve_watermark_image_path` safely resolves relative paths against `STORAGE_ROOT` and `DATA_DIR`.
- Workflow Context & Stage Execution Order: `WorkflowContext` serializes and preserves `watermark_enabled`, `watermark_type`, `watermark_image_path`, etc., across all stages. In `ProduceStage`, `final_render` (dubbed video multiplexing) executes before `add_watermark_logo` so the watermark overlay pass is burned directly onto the final dubbed video.
- Project Detail & Management API: `GET /api/projects/{project_id}` returns project metadata, normalized settings, list of associated videos (`videos`), segments array, and glossary stats (`glossary_count`, `terminology_count`). `PATCH /api/projects/{project_id}` and `PUT /api/projects/{project_id}` update `Project.title`, `Project.description`, and synchronize `VideoAsset.title` in SQLite DB.
- Projects List Endpoint: `GET /api/projects` (Supports optional server-side pagination params: `page: int`, `page_size: int` defaulting to 8 items per page, returning `total`, `page`, `page_size`, `total_pages`).

### AI Model Routing & Single Source of Truth Architecture
- **Configuration Priority Hierarchy**:
  `GLOBAL DB ROUTING (ai_function_configs / ai_models)` -> `AIModelResolver` -> `PipelineError` (Structured `AI_MODEL_NOT_FOUND` exception if model is not configured in DB).
- **Single Source of Truth Enforcement**:
  - Model selection is managed 100% globally via **AI Function Configuration & Routing** (`Settings Studio & AI Management` -> `AI Function Config` tab).
  - Individual project settings cards exclusively manage per-project asset preferences (Target Language, Voice ID, Original Audio Mode, Watermarks, Thumbnails). Per-project AI model overrides were completely removed to prevent configuration drift and guarantee strict adherence to the global AI Function Config database routing.
  - `AIModelResolver` (`app.services.model_resolver`) is the sole authoritative single-source-of-truth for resolving AI Models (STT, LLM, TTS, Image, Video) strictly from Database tables (`ai_function_configs` -> `ai_models`).
  - Automatically acquires an async database session if `db` parameter is omitted, querying active DB configuration directly.
  - Zero hardcoded fallback model strings (e.g. `gemini-2.5-flash`) or candidate loops (`GEMINI_MODEL_CANDIDATES` removed) exist in resolution routines.
  - `strip_gemini_model_prefix(model_name)` only strips `models/` prefix without modifying or inventing model identifiers.
  - Providers (STT, LLM) accept explicit `model` parameters resolved by `AIModelResolver` and execute API calls against the user's exact database-configured model.
- **Automatic Translation Model Resolution & Double Safety Nets**:
  - `translate_transcript_segments` accepts an optional `db` parameter and automatically invokes `AIModelResolver.resolve_model(db, capability="TRANSLATION")` if `translation_model_id` is omitted.
  - `GeminiLLMProvider.generate_text` features a secondary safety net invoking `AIModelResolver` if `model` is `None` at runtime, preventing `AI_CONFIGURATION_ERROR` pipeline crashes.
- **AI Image Generation & Pollinations AI Integration**:
  - `PollinationsImageProvider` (`app.providers.image.pollinations_provider`) is registered as a free, keyless AI Image Generation provider (`IMAGE_GENERATION` capability) in the global provider registry.
  - `SettingsService.get_eligible_providers_for_function` lists `pollinations` alongside `fal` and `openai` as compatible candidates for `image_generation`.
  - Default image generation routing (`DEFAULT_AI_FUNCTIONS`) sets `pollinations` (`pollinations-default`) as the primary zero-config image provider for thumbnails and visual assets.
- **Runtime Request Trace Logging**:
  - All AI Model resolutions log diagnostic details: capability, selected provider, selected model ID, model name, resolution source, and fallback status.

### Gemini STT Robust Parsing & Resilient Pipeline Architecture

### Character Voice Profiles & Post-TTS Scheduling
- Production integration remains in `app/api/routes/video_translator.py`; no parallel pipeline was introduced.
- STT segments preserve upstream `speaker_id`/speaker labels. Missing diarization becomes a distinct `UNRESOLVED_####` speaker so uncertain speakers are never merged automatically.
- `SpeakerVoiceMapping` remains backward-compatible and links project speakers to `CharacterVoiceProfile`, the authoritative project-scoped provider/voice assignment reused across episodes.
- `VoicePoolEntry` inventories voices independently of Character Mapping. EdgeTTS preferences are `vi-VN-NamMinhNeural` for main male and `vi-VN-HoaiMyNeural` for main female.
- Character Mapping runs after translation. Low confidence or voice conflicts set the job to `needs_review`; `auto_confirm_translation` cannot bypass this gate.
- Segment source timestamps are copied to `original_start/original_end` and never replaced by TTS timing. Measured `tts_duration` feeds `timeline_scheduler.py`, which writes `scheduled_start/scheduled_end`, overlap metadata, and a stable schedule action.
- Small different-voice overlaps may remain; same-voice overlaps are serialized. Bounded scheduling returns `cannot_fit` and `needs_review` if same-voice overlaps cannot fit safely. Confirming via `/character-voice-review/confirm-resume` re-validates the schedule and strictly rejects with HTTP 409 if unresolved conflicts remain. In `execute_job_render_pipeline`, automatic deterministic resolution uses `VoicePoolEntry` for unconfirmed conflicts when alternative voices are available, invalidates TTS cache specifically for changed segments (`[TTS_CACHE] Invalidating segments: [...]`), and regenerates only those clips (`[TTS] Regenerating segments: [...]`). Strict Pre-Sync and Pre-Render validation gates halt the pipeline and revert to `needs_review` if any same-voice overlap persists, while `build_dubbed_audio_timeline` in `sync_service.py` preserves `ValueError: SAME_VOICE_OVERLAP` as the ultimate defensive safety net.
- Review APIs under `/api/video-translator/jobs/{job_id}/character-voice-review` allow edit, validate, and confirm/resume. Mappings support `segment_id` for per-segment voice adjustments. Duplicate Confirm requests are idempotent and ignore terminal/active states without creating new render jobs. Polling preserves active form edits in UI during `needs_review` and `segment_editing`. `/projects/{project_id}/character-profiles` and `/voice-pool` expose persistent profiles and available voices. Existing `/voice-map` keys and payloads remain supported.
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

### Frontend Visual System
- Dark studio theme in `frontend/src/App.css`: Plus Jakarta Sans, indigo/cyan accent, glass navbar pills, cards, tabs, forms, modals.
- Top nav (`Navbar.jsx`): Studio, Ghép Video, Dự án, Cài đặt. Active item is a filled pill.
- Dashboard lists projects as cards (not a dense table). Settings and Project Detail use a shared pill tab bar.

### Windows Desktop Launcher Reliability
- The Shortcut path remains `AutoTransAI Studio.lnk` → `AutoTransAi.vbs` → `app_launcher.py`.
- The launcher starts FastAPI without the development reloader and writes startup output to `data/launcher_logs/backend.log`; Vite output goes to `data/launcher_logs/frontend.log` (spawned with `--host 127.0.0.1 --port 5173` to guarantee IPv4 binding).
- Backend `/api/system/health` must return HTTP 200 from the launcher-owned live process before Vite starts, and Vite must return HTTP 200 from its launcher-owned process before pywebview opens. Pre-existing listeners are refused, cleanup targets only child process trees created by this launcher, and startup/log/spawn failures show a Windows error dialog instead of opening a frontend that cannot reach its backend.

### Frontend Workflow UI Controls & Smart Retry Flow
- **Button State Machine**:
  - `not_started`, `completed`, `cancelled`, `failed`: Displays only `Start` button.
  - `running`: Displays `Pause` and `Cancel` buttons.
  - `paused`: Replaces `Pause` with `Resume` button while retaining `Cancel`.
  - **Optimistic State Transition**: Clicking `Start` immediately triggers optimistic frontend status set (`status: 'running'`), ensuring instant visual action response without lag.
- **Unified Workflow Layout Hierarchy (2-Column Responsive Studio Layout)**:
  1. `Studio Header Bar`: Compact project selector dropdown and settings dirty warning banner.
  2. `Main Studio Grid` (`.translator-studio-grid`):
     - **Left Primary Column**: Integrated `Unified 6-Stage Workflow Pipeline` (`WorkflowTimeline.jsx`) incorporating stage cards, overall progress, stage progress, heartbeat status, FFmpeg process stats, STT/Translation/TTS status, debug telemetry, and compact inline error alert -> Compact Video Input & Translation/Dubbing Config Panel.
     - **Right Auxiliary Column**: Advanced Branding & AI Controls Card containing Watermark (Logo/Text toggle, preview, position/scale sliders) and AI Auto Thumbnail (Style, Provider, Custom Instructions) built with progressive disclosure.
  3. `Below Viewport Area`: Project Glossary Manager accordion (`ProjectGlossaryManager.jsx`, default collapsed to maintain single-viewport fit) -> Segment Editor (when Phase 1 completes) -> Final Dubbed Video Player & Export Studio.
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
