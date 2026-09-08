- **Persistent Studio State, Isolated Settings Snapshot, Checkpoint System, & Resume Workflow (2026-09-07)**:
  - **Per-Job Isolated Studio State & Settings Snapshot**: Added `settings_snapshot_json`, `studio_state_json`, `last_checkpoint_stage`, and `last_checkpoint_at` columns to `VideoTranslationJob` ORM model ([video_translator.py](file:///c:/Hack/AutoTransAI/backend/app/models/video_translator.py)). When a job is created, its exact AI provider, model, voice, watermark, and audio mix configuration is saved in `settings_snapshot_json`, isolating existing jobs from global settings modifications.
  - **Dedicated Studio State & Checkpoint API Endpoints**: Implemented `GET /api/video-translator/jobs/{job_id}/studio-state`, `PATCH /api/video-translator/jobs/{job_id}/studio-state`, `POST /api/video-translator/jobs/{job_id}/checkpoint`, `POST /api/video-translator/jobs/{job_id}/resume`, and `POST /api/video-translator/jobs/{job_id}/apply-settings` in [video_translator.py](file:///c:/Hack/AutoTransAI/backend/app/api/routes/video_translator.py).
  - **Pipeline Checkpoints & Job Lock Concurrency Safety**: Integrated `EXTRACTING_AUDIO_DONE`, `STT_DONE`, `TRANSLATION_DONE`, `SEGMENT_EDITING_DONE`, `TTS_DONE`, `AUDIO_SYNC_DONE`, and `RENDER_DONE` stage checkpoints into pipeline background tasks. Added `_active_job_locks` asyncio locks preventing duplicate execution across multiple browser tabs.
  - **Pre-flight Check NameError Fix**: Fixed missing `Asset` model import (`from app.models.asset import Asset`) in [video_translator.py](file:///c:/Hack/AutoTransAI/backend/app/api/routes/video_translator.py#L34), resolving HTTP 500 error (`NameError: name 'Asset' is not defined`) during Pre-flight check when creating a new project.
  - **React UI ReferenceError Fix**: Defined `handleCancelJob = handleCancelWorkflow` in [VideoTranslator.jsx](file:///c:/Hack/AutoTransAI/frontend/src/pages/VideoTranslator.jsx#L592), resolving `ReferenceError: handleCancelJob is not defined` when rendering job action buttons.
  - **FFmpeg Drawtext Fontconfig Access Violation Fix**: Implemented cross-platform system font path resolver `resolve_system_font_path()` in [watermark_service.py](file:///c:/Hack/AutoTransAI/backend/app/services/video_editor/watermark_service.py#L183) (`C:/Windows/Fonts/arial.ttf`), eliminating Windows FFmpeg crash (exit code 3221225477 / Fontconfig error) during video rendering.
  - **Frontend Navigation, URL State Sync & Debounced Autosave**: Updated "Mở Studio" buttons in [ProjectDetail.jsx](file:///c:/Hack/AutoTransAI/frontend/src/pages/ProjectDetail.jsx) to pass both `project.id` and `job_id`. Updated [App.jsx](file:///c:/Hack/AutoTransAI/frontend/src/App.jsx) to maintain active page, project ID, and job ID in URL query parameters (`?page=translator&jobId=...`) and localStorage. Added 800ms debounced autosave for edited transcript segments and studio UI state in [VideoTranslator.jsx](file:///c:/Hack/AutoTransAI/frontend/src/pages/VideoTranslator.jsx).
  - **Automated Integration Testing**: Created comprehensive integration test suite [test_persistent_studio_state.py](file:///c:/Hack/AutoTransAI/backend/tests/integration/test_persistent_studio_state.py) covering all 8 test scenarios. All 8 tests passed 100% (0 failures).

- **React Global ErrorBoundary & Mutually Exclusive Smart Retry Fix (2026-09-07)**:
  - **Global Error Boundary (`main.jsx`)**: Implemented top-level `ErrorBoundary` in [main.jsx](file:///c:/Hack/AutoTransAI/frontend/src/main.jsx) to catch uncaught component rendering exceptions and display a formatted dark Error Card with error trace details and a reload button, preventing blank/black screen crashes.
  - **Mutually Exclusive Retry Calls**: Refactored `handleRetryJob` and `handleRetryStage` in [VideoTranslator.jsx](file:///c:/Hack/AutoTransAI/frontend/src/pages/VideoTranslator.jsx#L593-L620) to execute `retryJob` or `retryStage` mutually exclusively, preventing double pipeline background task invocations.
  - **Backend Retry Safeguards**: Wrapped job lookup in `retry_stage_api` ([video_translator.py](file:///c:/Hack/AutoTransAI/backend/app/api/routes/video_translator.py#L1580-L1605)) with try-except safeguards to guarantee clean HTTP 200 responses.
  - **Automated Verification**: Ran Vite production build (`npm run build` - 1.04s clean) and backend unit tests (`pytest backend/tests/unit` - 130 tests 100% passed).

- **Smart Retry Button & Pipeline Restart Trigger Fix (2026-09-07)**:
  - **Backend Pipeline Background Trigger**: Updated `retry_stage_api` (`POST /projects/{project_id}/workflow/stage/{stage_name}/retry`) in [video_translator.py](file:///c:/Hack/AutoTransAI/backend/app/api/routes/video_translator.py#L1570-L1605) to automatically locate and restart associated `VideoTranslationJob` records, spawning `start_translation_pipeline(job.id, background_tasks, session)` background tasks upon stage retries.
  - **Frontend Optimistic Feedback & Polling**: Refactored `handleRetryJob` and `handleRetryStage` in [VideoTranslator.jsx](file:///c:/Hack/AutoTransAI/frontend/src/pages/VideoTranslator.jsx#L900-L950) to clear error states (`setPipelineError(null)`), set optimistic processing state (`setIsProcessing(true)`), and trigger both job and stage retry API endpoints.
  - **UI Loading Spinner**: Added visual loading spinner (`Đang Thử Lại...`) and disabled states to `🔄 Smart Retry` buttons during action execution.
  - **Automated Verification**: Ran production Vite build (`npm run build` - 100% clean) and backend unit tests (`pytest backend/tests/unit` - 130 tests passed 100%).

- **Automatic Translation Model Resolution & Pipeline Safety Net Fix (2026-09-07)**:
  - **Fixed `translate_transcript_segments` Resolution**: Updated [translator_service.py](file:///c:/Hack/AutoTransAI/backend/app/services/video_translator/translator_service.py#L909-L917) and [video_translator.py](file:///c:/Hack/AutoTransAI/backend/app/api/routes/video_translator.py#L540-L545) to accept `db` session and automatically query `AIModelResolver` for the active `TRANSLATION` capability model if `translation_model_id` is omitted.
  - **Secondary Provider Safety Net**: Added fallback resolution in [gemini_provider.py](file:///c:/Hack/AutoTransAI/backend/app/providers/llm/gemini_provider.py#L86-L92) `generate_text()` so missing model parameters automatically resolve from database settings instead of raising `AI_CONFIGURATION_ERROR`.
  - **Automated Verification**: All translation and model routing unit tests passed 100% (17 passed).

- **Robust Gemini STT Response Parser & JSON Mime Type Enforcement (2026-09-07)**:
  - **Created `parse_gemini_stt_response` Module**: Added dedicated multi-stage parser [stt_parser.py](file:///c:/Hack/AutoTransAI/backend/app/services/video_translator/stt_parser.py) executing 6 sequential fallback stages: strict JSON parsing, markdown code block stripping (` ```json ... ``` `), regex object/array extraction (`{...}` / `[...]`), malformed JSON sanitization (trailing commas, unescaped string literal newlines/control characters, Python booleans), plain-text timestamped dialogue fallback parsing (`[00:00 - 00:05] Text`), and schema normalization (`items`, `transcript`, `dialogue`, `sentences` -> `segments`; `lang`, `language_code` -> `language`).
  - **Upgraded Gemini API Payload**: Updated `transcribe_audio_with_gemini` in [translator_service.py](file:///c:/Hack/AutoTransAI/backend/app/services/video_translator/translator_service.py#L516-L536) to pass `generationConfig: {"response_mime_type": "application/json", "temperature": 0.1}`, enforcing JSON mime type output natively at the AI provider level.
  - **Enhanced Debug & Log Traceability**: Integrated raw response logging (first 1000 characters) to `logger.error` and `log_job_event` when parsing exceptions occur.
  - **Comprehensive Unit Testing**: Created [test_gemini_stt_parser.py](file:///c:/Hack/AutoTransAI/backend/tests/unit/test_gemini_stt_parser.py) covering 7 requirement edge cases. All 17 STT unit tests passed 100% (0 failures).

- **AI Model Resolver Capability Compatibility Fix (2026-09-07)**:
  - **Multimodal LLM & Custom Model Capability Compatibility**: Upgraded `_is_capability_compatible()` in [model_resolver.py](file:///c:/Hack/AutoTransAI/backend/app/services/model_resolver.py#L81-L90) so user-configured Gemini and OpenAI models (such as `gemini-3.5-flash-lite` or custom models) properly resolve for Speech-To-Text (STT) and Translation, even if their catalog entry was created with `["LLM"]`.
  - **Auto-populated Capabilities for Custom Gemini/OpenAI Models**: Updated `add_custom_model()` in [settings_service.py](file:///c:/Hack/AutoTransAI/backend/app/services/settings_service.py#L331-L355) so custom Gemini and OpenAI models automatically include `STT`, `LLM`, and `TRANSLATION` capabilities.
  - **Automated Verification**: All 123 backend unit tests (`pytest backend/tests/unit`) passed 100% (119 passed, 4 skipped, 0 failed).

- **Default AI Model Seed & Deletion Safety Updates (2026-09-07)**:
  - **Updated Seed Defaults**: Changed initial system seed model in `DEFAULT_AI_FUNCTIONS` and `DEFAULT_AI_MODELS` from `gemini-2.0-flash` to `gemini-1.5-flash` (universally supported across all Google Gemini API key tiers and regions).
  - **Safe Model Deletion Re-assignment**: Fixed `SettingsService.delete_model()` so deleting models automatically reassigns any active function configuration to an alternate matching model instead of setting NULL, preventing ORM `IntegrityError` and allowing users to delete `gemini-2.0-flash` or any unwanted model cleanly from Settings UI.
  - **Automated Verification**: Ran backend unit tests (`pytest backend/tests/unit` - 119 passed, 4 skipped, 0 failed).

- **Single Source of Truth AI Model Routing Architecture & Database-Only Resolution (2026-09-07)**:
  - **Eliminated Hardcoded String Defaults**: Completely removed all hardcoded fallback model strings (`"gemini-2.5-flash"`) from `AIModelResolver`, `strip_gemini_model_prefix()`, `qc_service.py`, `youtube_service.py`, and `DEFAULT_PROJECT_SETTINGS`.
  - **Strict Database Model Resolution**: `AIModelResolver` (`app.services.model_resolver`) now queries Database tables (`ai_function_configs` -> `ai_models`) strictly. If `db` session is omitted, it automatically creates a DB session to query active DB settings.
  - **Structured Error Propagation**: If a model is not configured in the Database, `AIModelResolver` raises structured `PipelineError` (`AI_MODEL_NOT_FOUND`) instead of silently falling back to a hardcoded string.
  - **STT & LLM Model Propagation**: Updated `GeminiSTTProvider`, `WhisperSTTProvider`, `GroqSTTProvider`, `GeminiLLMProvider`, `OpenAILLMProvider`, `qc_service.py`, and `youtube_service.py` to accept explicit `model` parameters resolved from Settings database.
  - **Model String Normalization**: `strip_gemini_model_prefix(model_name)` only strips `models/` prefix without mutating or inventing model names.
  - **Automated Verification**: All unit tests in `backend/tests/unit/` passed 100%.

- **Full Codebase Audit & Dead Component / Unused Code Cleanup (2026-09-07)**:
  - **Vite Build & Stale Import Fix**: Removed broken `AIThumbnailPanel` imports in [VideoTranslator.jsx](file:///c:/Hack/AutoTransAI/frontend/src/pages/VideoTranslator.jsx) and [ProjectDetail.jsx](file:///c:/Hack/AutoTransAI/frontend/src/pages/ProjectDetail.jsx), restoring 100% clean production builds (`npm run build`).
  - **Unused Folders & Models Removal**: Deleted unused directories `PIPER_MODELS/`, `mdx_models/` (~245MB legacy ONNX models), `scratch/`, `docs/`, `PROJECT_KNOWLEDGE_BASE.docx`, and `data/r2_storage/`.
  - **Frontend Asset Cleanup**: Deleted unused starter assets (`hero.png`, `typescript.svg`, `favicon.svg`, `icons.svg`).
  - **Frontend API Cleanup**: Removed dead API client functions `projectsApi.configure` and `projectsApi.precheck` in [api.js](file:///c:/Hack/AutoTransAI/frontend/src/api.js).
  - **Backend Dependency Cleanup**: Removed obsolete `asyncpg` dependency from [requirements.txt](file:///c:/Hack/AutoTransAI/backend/requirements.txt).
  - **Backend Dead Code & Imports Cleanup**: Removed duplicate route/provider imports in [main.py](file:///c:/Hack/AutoTransAI/backend/app/main.py), removed legacy Postgres string replacement in [database.py](file:///c:/Hack/AutoTransAI/backend/app/database.py), removed unused `Asset` import in [video_translator.py](file:///c:/Hack/AutoTransAI/backend/app/api/routes/video_translator.py), and removed unused imports in [projects.py](file:///c:/Hack/AutoTransAI/backend/app/api/routes/projects.py).
  - **Backend Script Cleanup**: Deleted obsolete scripts `backend/scripts/apply_db_schema.py` and `backend/scripts/init_mysql_db.py`.
  - **Automated Verification**: Ran `npm run build` (passed in 1.10s) and `pytest` (120 unit tests 100% passed).

- **Active Pipeline Navigation Guard & Leave Warning Prompt**:
  - **Browser Tab Close & Refresh Guard**: Added `beforeunload` event listener in [VideoTranslator.jsx](file:///c:/Hack/AutoTransAI/frontend/src/pages/VideoTranslator.jsx#L186-L210) to warn user before closing or reloading browser tab when a video translation workflow is actively running (`isProcessing` or `running`).
  - **In-App Navbar Route Interception**: Updated [App.jsx](file:///c:/Hack/AutoTransAI/frontend/src/App.jsx#L15-L40) and [Navbar.jsx](file:///c:/Hack/AutoTransAI/frontend/src/components/Navbar.jsx#L4-L20) to intercept top navigation links (`Quản lý Dự án`, `+ Tạo dự án mới`, `⚙️ Cài đặt`, Logo), prompting confirmation dialog before leaving the page so users don't accidentally disrupt real-time tracking.

- **Instant Watermark Logo Persistence & Asset Table Fallback**:
  - **Instant DB Persistence**: Updated `handleLogoUpload` in [VideoTranslator.jsx](file:///c:/Hack/AutoTransAI/frontend/src/pages/VideoTranslator.jsx#L142-L165) to immediately call `projectsApi.saveSettings(selectedProjectId, ...)` upon uploading a logo file, ensuring `watermark_image_path` is instantly saved in Database settings and not lost across project switching.
  - **Asset Table Fallback Lookup**: Updated `preflight_workflow_api` in [video_translator.py](file:///c:/Hack/AutoTransAI/backend/app/api/routes/video_translator.py#L1480-L1495) to automatically query the `Asset` table for `watermark_logo` assets if `watermark_image_path` is missing in request payload or settings JSON.

- **Preflight Check Watermark Logo Path Resolution Fix**:
  - **Resolved Relative Storage Paths**: Updated [preflight.py](file:///c:/Hack/AutoTransAI/backend/app/services/preflight.py#L347-L354) to use `resolve_watermark_image_path(watermark_image_path)` instead of raw `Path(...).exists()`.
  - **Fixed False Negative Validation**: Fixed pre-flight check failure (`Chưa chọn file Logo Ảnh hoặc file Logo không tồn tại`) where uploaded logo relative paths (`projects/p_xxx/assets/watermarks/logo.png`) failed to resolve against `STORAGE_ROOT` or `DATA_DIR`.

- **Gemini STT Model Resolution & Fallback Optimization**:
  - **Dynamic Model Selection**: Model is dynamically selected from user dropdown (or DB config) via `AIRouter.resolve_stt_model`, NOT fixed/hardcoded.
  - **Active Model Fallback Queue**: Updated `GEMINI_MODEL_CANDIDATES` in [gemini_provider.py](file:///c:/Hack/AutoTransAI/backend/app/providers/llm/gemini_provider.py#L20-L40) to include `gemini-2.0-flash`, `gemini-1.5-pro`, `gemini-1.5-flash`, and `gemini-2.0-flash-lite`.
  - **Auto-Fallback on HTTP 404**: Upgraded [translator_service.py](file:///c:/Hack/AutoTransAI/backend/app/services/video_translator/translator_service.py#L525-L585) so if Google API returns HTTP 404 for a specific model endpoint on `v1beta`, the system seamlessly fails over to the next candidate model (`gemini-2.0-flash`), preventing pipeline failure.

- **AI Thumbnail Panel DB Settings Binding Fix**:
  - **Passed Missing `projectId` & `initialCustomInstruction` Props**: Updated [VideoTranslator.jsx](file:///c:/Hack/AutoTransAI/frontend/src/pages/VideoTranslator.jsx#L1781-L1788) to pass `projectId={selectedProjectId || activeProjectId || job?.project_id}` and `initialCustomInstruction={thumbnailInstruction}` to `AIThumbnailPanel`.
  - **Query Settings by Target ID (`projectId || jobId`)**: Upgraded [AIThumbnailPanel.jsx](file:///c:/Hack/AutoTransAI/frontend/src/components/AIThumbnailPanel.jsx#L45-L60) to query `projectsApi.getSettings(targetId)` using `projectId || jobId`, populating `customInstruction` with real database values.

- **Studio Project Selector Bar Layout Optimization**:
  - **Flex Layout Alignment**: Removed `justifyContent: 'space-between'` and added `flex: 1` to the `<select>` container in [VideoTranslator.jsx](file:///c:/Hack/AutoTransAI/frontend/src/pages/VideoTranslator.jsx#L1008-L1028), eliminating the large empty gap and placing the dropdown box directly adjacent to the `➕ Tạo dự án mới` button.

- **Studio (Dịch video) AI Thumbnail Card & Custom Instruction Integration**:
  - **Added AI Thumbnail Settings Panel in Studio Form**: Rendered the `🖼️ Tự Động Tạo Thumbnail AI` card in `VideoTranslator.jsx` directly under translation settings (matching `ProjectDetail.jsx`), featuring a sleek toggle switch, `Phong Cách Thumbnail (Style)` select, `AI Image Provider` select, and `💬 Yêu Cầu Bổ Sung (Custom Instruction)` textarea.
  - **Auto-Sync Saved Instructions**: Upgraded `AIThumbnailPanel.jsx` to load saved `thumbnail_custom_instruction`, `thumbnail_style`, and `thumbnail_provider` from project settings on mount/selection.

- **Project Detail Custom Instruction Component UI Match**:
  - **Identical Styling & Classes**: Updated `💬 Yêu Cầu Bổ Sung (Custom Instruction):` label and `<textarea>` in `ProjectDetail.jsx` to use exact Bootstrap class names (`form-label text-light small fw-bold`, `form-textarea form-control form-control-sm bg-dark text-light border-secondary`) matching `AIThumbnailPanel.jsx`.
  - **Pixel-Perfect Alignment**: Resolved label text color, font weight, and textarea border/focus ring discrepancies between Project Detail page and AI Thumbnail Panel.

- **Project Detail UI & Video Management Upgrade**:
  - **Full Option & Layout Parity with Studio (AI Thumbnail Alignment)**:
    - Restructured AI Thumbnail card in `ProjectDetail.jsx` to match `AIThumbnailPanel.jsx` in `VideoTranslator.jsx` 100%.
    - Converted squeezed side-by-side dropdowns into full-width stacked select controls: `🎭 Phong Cách Thumbnail (Style):`, `⚙️ AI Image Provider:`, and `💬 Yêu Cầu Bổ Sung (Custom Instruction):`.
    - Eliminated option text truncation (such as `👻 Horror (U tối, bí ẩn, kinh dị)` getting cut off) and aligned placeholders.
  - **ProjectDetail Blank Screen Fix**:
    - Restored missing `const [isTabDirty, setIsTabDirty] = useState(false)` state declaration in `ProjectDetail.jsx`, resolving runtime `ReferenceError: setIsTabDirty is not defined` crash.
  - **Video Deletion from Project**:
    - Added `🗑️ Xóa` button under `THAO TÁC` column in "Danh sách Video trong Dự án" table (`ProjectDetail.jsx`).
    - Integrated `handleDeleteVideo()` with user confirmation prompt and `projectsApi.delete(v.id)`, removing video jobs, database records, and workspace files with cascading cleanup.
  - **Custom Toggle Switch UI Upgrade**:
    - Replaced standard checkbox controls (`Bật Watermark` and `Tự động Tạo Thumbnail`) on `ProjectDetail.jsx` with sleek modern iOS-style toggle switches (thanh trượt đóng mở).
    - Removed text labels as requested, rendering clean glowing toggle switches next to card headers.

- **Watermark Toggle & Settings Desynchronization Fix ("Khi lưu vẫn mất")**:
  - **SQLAlchemy ORM JSON Mutation Tracking (`flag_modified`)**:
    - Added `from sqlalchemy.orm.attributes import flag_modified` and `copy.deepcopy` in `save_project_settings` (`backend/app/api/routes/projects.py`). Resolved SQLAlchemy ORM issue where in-place JSON column mutations were not flagged dirty, preventing MySQL `UPDATE` queries.
  - **Backend Fallback Endpoint & DB Row Persistence**:
    - Updated fallback branch in `GET /api/projects/{project_id}` and `GET /api/projects/{project_id}/settings`. If queried by job ID and `Project` record does not exist yet, the system auto-creates a `Project` DB row, links `job.project_id = real_p_id`, and commits normalized settings.
  - **Job Creation & Workflow Start Inheritance**:
    - Upgraded `create_job` (`POST /api/video-translator/jobs`) to inherit watermark settings (`watermark_enabled`, `watermark_type`, `watermark_image_path`, etc.) from `Project.settings_json` if job creation request body uses defaults.
    - Upgraded `preflight_workflow_api` and `start_workflow_api` (`POST /projects/{project_id}/workflow/start`) in `video_translator.py` to merge saved project settings with incoming payload, preventing default `watermark_enabled: false` payload from overriding saved watermark settings.
  - **Automated Verification**:
    - Ran pytest suite `backend/tests/unit/` (120 unit tests 100% passed).

- **Watermark Toggle Fix & Pipeline Execution Upgrade**:
  - **UI Option Cards Conditional Rendering Fix**:
    - Resolved UI rendering bug in `ProjectDetail.jsx` where Watermark and AI Thumbnail option cards remained fully expanded and visible even when "Bật Watermark" or "Tự động Tạo Thumbnail" checkboxes were UNCHECKED.
    - Wrapped option sections in `parseBool(pSettings.watermark_enabled) ? (...) : (...)` and `parseBool(pSettings.thumbnail_enabled) ? (...) : (...)`, cleanly hiding configuration controls and displaying an informative disabled banner (`🚫 Watermark hiện đang TẮT...`) when turned OFF.
    - Synchronized radio button selection states (`🖼️ Logo Ảnh` vs `🔤 Watermark Text`) with input sub-panels in both `ProjectDetail.jsx` and `VideoTranslator.jsx`.
  - **Boolean String Parsing Fix**:
    - Created `_parse_bool()` helper in `backend/app/api/routes/projects.py` and `parseBool()` in React frontend (`VideoTranslator.jsx`, `ProjectDetail.jsx`).
    - Resolved critical truthy bug where string `"false"` evaluated to `True` in Python `bool("false")` and JavaScript `Boolean("false")`, causing watermark switch to remain stuck ON.
  - **Watermark Image Path Resolution**:
    - Built `resolve_watermark_image_path()` in `WatermarkService` (`backend/app/services/video_editor/watermark_service.py`) to safely resolve relative asset paths (`projects/{id}/assets/watermarks/logo.png`) against `STORAGE_ROOT` and `DATA_DIR`.
  - **ProduceStage Step Ordering & Workflow Context Preservation**:
    - Reordered `ProduceStage.STEPS` in `produce_stage.py` so `final_render` (dubbed video multiplexing) runs before `add_watermark_logo`, ensuring the watermark is overlayed directly onto the dubbed video.
    - Updated `WorkflowContext` data model and `to_dict()` / `from_dict()` serialization to preserve watermark settings (`watermark_enabled`, `watermark_type`, `watermark_image_path`, `watermark_text`, `watermark_position`, `watermark_scale`, `watermark_opacity`, `watermark_margin`, `watermark_font_size`) across stages.
  - **Automated Verification**:
    - Added unit test cases for boolean string parsing and path resolution in `backend/tests/unit/test_project_settings_persistence.py` (120 unit tests 100% passed).

- **Project-Based Settings Persistence & Project Management Upgrade**:
  - **Single Source of Truth & Settings Normalization**:
    - Created `DEFAULT_PROJECT_SETTINGS` and `normalize_project_settings()` helper in `backend/app/api/routes/projects.py`, enforcing system default fallbacks and strict numeric/enum constraints (`watermark_position`, `watermark_scale`, `watermark_opacity`, `watermark_margin`).
    - Upgraded `GET /api/projects/{project_id}/settings` and `POST / PUT /api/projects/{project_id}/settings` to validate, save, commit, and return exact server persisted configuration.
    - Added structured runtime diagnostic logging (`[PROJECT SETTINGS LOAD]` and `[PROJECT SETTINGS SAVE]`).
  - **Watermark Logo Asset Persistence**:
    - Upgraded `POST /api/video-translator/upload-watermark-logo` to accept `project_id`, storing logo files in `storage/projects/{project_id}/assets/watermarks/`, creating `Asset` DB records (`asset_type="watermark_logo"`), and persisting `watermark_image_asset_id` into project `settings_json`.
  - **Frontend State Sync, Comprehensive Dirty State & Project Switching Guard**:
    - Overhauled `VideoTranslator.jsx` to track 100% of UI controls across all 9 categories (Video Input, Language, AI Models, Voice, Original Audio, Watermark, AI Thumbnail).
    - Built deep equality comparison in dirty state `useEffect`, activating the unsaved changes alert bar whenever ANY option is modified.
    - Built `handleDiscardChanges()` and project switching guard modal (`showSwitchGuardModal`), prompting users to save, discard, or cancel project switching when unsaved changes exist.
  - **Workflow Configuration Snapshotting**:
    - Upgraded `POST /api/video-translator/projects/{project_id}/workflow/start` in `video_translator.py` to freeze project settings into `WorkflowExecution.context_data["settings_snapshot"]`, logging `[WORKFLOW SETTINGS SNAPSHOT]`.
  - **Project Detail Page & Management Upgrade**:
    - Upgraded `ProjectDetail.jsx` with tabbed navigation: Overview & Videos table, Project Settings summary (with logo preview & AI provider details), and Glossary Manager.
    - Added interactive `⚙️ Chỉnh sửa cấu hình & Dịch Video` button navigating directly to Video Translator view with project pre-selected.
  - **Automated Regression Suite**:
    - Added `backend/tests/unit/test_project_settings_persistence.py` (100% passed).

- **Critical AI Model Routing & Single Source of Truth Bug Fix**:
  - **Root Cause Resolution**: Resolved configuration drift bug where `transcribe_audio_with_gemini` ignored UI database settings and iterated a hardcoded legacy array containing deprecated `gemini-2.0-flash` (HTTP 404).
  - **Configuration Priority Hierarchy**: Added `AIRouter.resolve_stt_model(db, requested_model)` enforcing:
    `REQUESTED MODEL` -> `DATABASE AI FUNCTION CONFIG` -> `ENVIRONMENT DEFAULT` -> `HARDCODED SAFE DEFAULT (gemini-2.5-flash)`.
  - **Model Normalization**: Built `normalize_gemini_model_name()` in `gemini_provider.py` stripping `models/` prefix and auto-migrating deprecated model strings to `gemini-2.5-flash`.
  - **Diagnostic Logging**: Added structured debug logs (`[STT CONFIG]`, `[STT ROUTING]`, `[STT API REQUEST]`) tracing exact database model, resolved router model, and actual API URL requested.
  - **Preflight & Defaults**: Updated `run_video_translator_preflight()` to report exact active model (`gemini-2.5-flash`) and removed legacy `gemini-2.0-flash` defaults.
  - **Automated Regression Tests**: Added `tests/unit/test_stt_model_routing.py` (100% passed).

- **Project Detail Page Fix & Backend Endpoint Integration**:
  - **Backend Payload Enhancement**:
    - Updated `GET /api/projects/{project_id}` in `projects.py` to query and include the `segments` array for standard projects, preventing React `TypeError: Cannot read properties of undefined (reading 'length')` crashes.
    - Added fallback query in `GET /api/projects/{project_id}` checking `VideoTranslationJob` & `VideoTranslationSegment` records if a translation job ID is queried.
  - **Frontend Null Safety & Defensive Rendering**:
    - Added safe optional chaining and fallback arrays `(project.segments || [])`, `(providers?.audio || [])`, and `(providers?.video || [])` in `ProjectDetail.jsx`.
    - Added safe title String formatting `(project.title || 'Project').replace(...)`.
    - Built friendly error / empty state card with `← Quay lại Dashboard` button in `ProjectDetail.jsx` and `App.jsx` when project ID is invalid or not found, preventing blank dark screen rendering.

- **Unified Workflow Pipeline Layout, Active Animations & Collapsible Accordion Overhaul**:
  - **Layout Restructuring**:
    - Placed `Unified 6-Stage Workflow Pipeline` (`WorkflowTimeline.jsx`) permanently fixed at the top of the Video Translator view.
    - Moved Error Message Card (`❌ Xử Lý Thất Bại`) directly beneath `WorkflowTimeline.jsx` so pipeline execution failures are immediately visible below the stage pipeline.
    - Positioned Job Progress Panel (`📊 Tiến Trình Xử Lý Pipeline (Job: ...)`) directly beneath the Error Card.
    - Converted all configuration panels (`⚙️ Cấu hình Nhập Video, Dịch & Lồng Tiếng`, `📖 Quản Lý Thuật Ngữ`, `🖼️ Tạo Thumbnail AI`) into collapsible cards (`CollapsibleCard`) with clean accordion toggle controls (`▼ Mở rộng` / `▲ Thu gọn`).
  - **Stage Execution Visual Feedback & Animations**:
    - Added CSS keyframe animations `@keyframes stagePulseGlow` and `@keyframes spinIcon`.
    - Active/Running stages (`running` state) now display an animated cyan pulsing border glow, spinning gear icon, and cyan step badge.
    - Passed/Completed stages (`passed` state) display a solid emerald green border (`#10B981`), green checkmark badge (`✓ Passed`), and emerald highlight.
  - **Optimistic State Feedback on Start Workflow**:
    - Updated `executeStartWorkflowAfterPreflight` and `handleStartWorkflow` to optimistically update frontend state (`status: 'running'`, `current_stage: 'INGEST'`) as soon as `Start Workflow` is clicked, providing instant visual button transition (`⏸ Pause` & `🛑 Cancel`) without UI delay.

- **Laragon MySQL Database Connection Update**:
  - Updated `DATABASE_URL` in `.env` and `config.py` to `mysql+aiomysql://root:210606@127.0.0.1:3306/autotransai`.
  - Installed `aiomysql` and `pymysql` in python environment.
  - Automatically created `autotransai` database and initialized all tables via DDL schema migration.
  - Added project ID deduplication in `GET /api/projects` endpoint.
- **Workflow UI Action Controls & Smart Retry Flow**:
  - **Button State Machine**: Refined `WorkflowTimeline.jsx` control button display logic:
    - Initial / finished / idle states (`not_started`, `completed`, `cancelled`, `failed`): Renders only `▶ Start Workflow` button.
    - Running state (`running`): Hides `Start Workflow`; renders `⏸ Pause` and `🛑 Cancel` buttons.
    - Paused state (`paused`): Replaces `Pause` with `▶ Resume` button while retaining `🛑 Cancel` button.
  - **Smart Retry Error Delegation**:
    - Updated `handleRetryJob` in `VideoTranslator.jsx` so clicking `🔄 Smart Retry` delegates to stage retry (`POST /api/video-translator/projects/{project_id}/workflow/stage/{stage_name}/retry`) resuming workflow execution from the exact stage that failed.
    - Enhanced Error Message Card rendering to trigger when `workflowStatusData` status is `failed` and display `workflowStatusData?.error_message`.
- **Unified 6-Stage Workflow Execution APIs**:
  - `POST /api/video-translator/projects/{project_id}/workflow/start`: Accepts `StartWorkflowRequest` with full pipeline context (`video_url`, `video_path`, `target_language`, `audio_provider_id`, `llm_provider_id`, `voice_id`, `watermark` settings).
  - `POST /api/video-translator/projects/{project_id}/workflow/cancel`: Safely cancels running 6-stage workflow tasks and updates DB state to `cancelled`.
  - `POST /api/video-translator/projects/{project_id}/workflow/stage/{stage_name}/retry`: Resets stage state and steps to `pending` and resumes execution from specified stage.
- **Frontend Timeline Controls & Live Polling**:
  - Added **🛑 Cancel Workflow** and **🔄 Retry Stage** action buttons to `WorkflowTimeline.jsx`.
  - Added loading indicator states (`loadingAction`), disabling buttons while API calls are pending.
  - Added stage step breakdown drawer showing live step statuses (`import_video`, `speech_to_text`, `translate_transcript`, etc.).
  - Unified real-time polling in `VideoTranslator.jsx` to fetch `/workflow-status` alongside `/jobs/{id}` every 1.5s.

- **`backend/app/models/video_translator.py`**:
  - Added `project_id` foreign key column to `VideoTranslationJob` referencing `projects.id`.
- **`backend/app/api/routes/video_translator.py`**:
  - Updated `create_translation_job` (`POST /jobs`) to auto-create and link a real `Project` row in `projects` table if no valid `project_id` is supplied.
  - Added `_validate_project_exists()` helper returning structured HTTP 404 (`PROJECT_NOT_FOUND`) if `project_id` is missing, invalid, or `'default_project'`, eliminating database `ForeignKeyViolationError` (HTTP 500).
- **`frontend/src/pages/VideoTranslator.jsx`**:
  - Removed `'default_project'` string fallback completely.
  - Added project validation check before calling workflow APIs (`Start`, `Pause`, `Resume`, `Cancel`, `Retry Stage`), prompting user if no valid project is active.

- **Server-Side Projects List Pagination (8 items per page)**:
  - Updated `GET /api/projects` endpoint in `projects.py` to support `page` and `page_size` query parameters (default 8 items per page).
  - Returns pagination metadata (`total`, `page`, `page_size`, `total_pages`).
  - Updated `projectsApi.list(page, pageSize)` in `frontend/src/api.js` to send query params.
  - Updated `Dashboard.jsx` to fetch exact 8 items per page from backend on page navigation, avoiding fetching full dataset over network.

- **Unified Workflow, Project System & Pre-flight Validation Overhaul**:
  - **Project System & Selector**:
    - Enhanced `Project` model with `description` and `settings_json` columns for persistent project configurations.
    - Built interactive `Project Selector` header in `VideoTranslator.jsx` with direct "Select Project" dropdown, "Create Project Modal", current project badge, and "Dirty Settings Indicator" bar.
    - Completely eliminated `default_project` and fake hardcoded project IDs across frontend and backend.
  - **Pre-flight Check Engine**:
    - Created `run_video_translator_preflight()` service in `preflight.py` checking Video Input, Project Existence, DB connection, FFmpeg binaries, Storage Permissions, LLM Provider Health, TTS Health, Watermark Settings, and Optional Thumbnail AI.
    - Classified pre-flight checks into **CRITICAL** (blocks execution if failed) vs **OPTIONAL** (displays warnings, allows execution).
    - Exposed `POST /api/video-translator/projects/{project_id}/workflow/preflight` endpoint.
    - Created interactive `Pre-flight Result Modal` displaying categorized green checkmarks, yellow warnings, and critical error messages with "Start Workflow", "Retry Check", or "Open Settings" actions.
  - **Hybrid Terminology System**:
    - Added `ProjectTerminologyMemory` ORM model & `project_terminology_memory` database table.
    - Added REST endpoints for listing, adding, and deleting project terminology memory items.
    - Enhanced `TranslateStage` to load Manual Glossary terms (Priority 1) and Terminology Memory (Priority 2), injecting explicit terminology rules into LLM prompts.
    - Upgraded `ProjectGlossaryManager.jsx` with a tabbed interface separating Manual Glossary and AI Terminology Memory.
  - **Optional Thumbnail AI & Watermark Handling**:
    - Thumbnail AI works dynamically even when custom instructions are empty.
    - Failures in Thumbnail AI generate optional warnings and do not crash or halt the video translation pipeline.
    - Watermark validation checks for text/image parameters when enabled.

- **Complete Supabase Removal & Full Local Migration (Laragon MySQL + Local File Storage)**:
  - **Database Migration to Laragon MySQL**:
    - Updated `backend/app/config.py` with `DATABASE_URL` defaulting to `mysql+aiomysql://root:@127.0.0.1:3306/autotransai` (with graceful SQLite fallback if MySQL service is stopped).
    - Updated `backend/app/database.py` with MySQL dialect support (`is_mysql`), `pool_pre_ping=True`, `pool_recycle=3600`, and MySQL backtick DDL column migration.
    - Updated `backend/requirements.txt`: Removed `supabase`, added `aiomysql` and `pymysql`.
    - Created `backend/scripts/migrate_to_mysql.py` for exporting SQLite DB to Laragon MySQL.
  - **Pure Local Storage Architecture**:
    - Refactored `backend/app/services/storage_service.py` to `LocalStorageService`, stripping all Supabase SDK dependencies.
    - Standardized local file structure under `storage/projects/{project_id}/` (`videos/source/`, `videos/processed/`, `audio/original/`, `audio/extracted/`, `audio/dubbed/`, `subtitles/`, `thumbnails/`, `outputs/`, `temporary/`).
    - Configured local media file streaming via `GET /api/storage/files/{file_path:path}`.
  - **UI & Configuration Clean-up**:
    - Updated `frontend/src/pages/Settings.jsx`, `frontend/src/pages/Dashboard.jsx`, and `frontend/src/components/AIThumbnailPanel.jsx` to reflect Local Disk Storage and Laragon MySQL setup.
    - Cleaned up `.env.example` removing all `SUPABASE_*` configuration keys.

### Affected Files
- `backend/app/config.py`
- `backend/app/database.py`
- `backend/app/services/storage_service.py`
- `backend/app/services/settings_service.py`
- `backend/app/services/preflight.py`
- `backend/scripts/migrate_to_mysql.py`
- `backend/requirements.txt`
- `frontend/src/pages/Settings.jsx`
- `frontend/src/pages/Dashboard.jsx`
- `frontend/src/components/AIThumbnailPanel.jsx`
- `.env.example`
- `PROJECT_KNOWLEDGE_BASE.md`
- `CHANGELOG_AI.md`
