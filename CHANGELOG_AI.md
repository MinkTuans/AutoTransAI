- **Catalog Access Provider Integrity (2026-09-23)**:
  - Fixed cross-provider access associations with non-null provider identity and composite foreign keys in `ai_catalog.py`, `api_key.py`, and additive revision `20260923_ai_catalog`.
  - Added validated, idempotent `grant_model_access` in `catalog_access_service.py`. Expanded ORM-created and migration-created SQLite regressions plus offline MySQL checks; 32 focused tests pass. Key deletion still retains catalog models. Updated knowledge base; no real database migration performed.

- **Encrypted Credential Domain (2026-09-23)**:
  - Added `backend/app/services/credential_service.py` with stable IDs, masked immutable DTOs, provider-scoped keyed duplicate detection, authenticated payload binding, and fail-closed decryption.
  - Supports explicit Fernet master keys or first-use private `.api_key_master_key` generation; missing/invalid master keys cannot overwrite existing encrypted credentials. No legacy credential reads or migration.
  - Added isolated SQLite/temporary-directory tests in `backend/tests/test_credential_service.py`, including rollback ownership and model retention. Extended catalog identity coverage and updated knowledge base. Existing API consumers remain unchanged.

- **Canonical Catalog Schema (2026-09-23)**:
  - Added `CatalogModel`, `APIKey`, and `KeyModelAccess` in `backend/app/models/ai_catalog.py`, `api_key.py`, and model exports; provider-scoped remote identity and credential-independent catalog lifetime.
  - Added additive Alembic revision `20260923_ai_catalog` and isolated schema/migration tests in `backend/tests/test_ai_catalog_domain.py`. SQLite round-trip and offline MySQL DDL pass; no real DB migration or legacy rewrite performed. Updated knowledge base.

- **Public Media Credential Isolation (2026-09-23)**:
  - Restricted `/media` and both `/api/storage` file routes to validated media in `STORAGE_ROOT` and legacy `DATA_DIR/translator/`; blocked secrets, database files, logs, dotfiles, traversal, and escaping symlinks.
  - Preserved serving of `.flv`, `.ts`, and `.3gp` formats accepted by video ingest and merger, and valid `STORAGE_ROOT` paths nested under `DATA_DIR` such as `DATA_DIR/storage`.
  - Enforced `DATA_DIR` outside `STORAGE_ROOT` at configuration load, keeping credential, SQLite, and encryption-key storage separate. Root-level `DATA_DIR` media URLs now require migration to an allowed media root.
  - Added isolated HTTP regression tests for all three routes and adapted Unicode download coverage to a temporary legacy translator path. Updated `PROJECT_KNOWLEDGE_BASE.md`.

- **Storage Consolidation & Unified File Management Overhaul (2026-09-18)**:
  - **Summary**: Resolved dual storage directory divergence (`AutoTransAI/storage` vs `AutoTransAI/backend/storage`) and fragmented `data/translator` paths. Unified all media, project structures, and job assets into a Single Source of Truth under `AutoTransAI/storage/`. Implemented multi-directory CRUD cleanup contracts to eliminate orphan project directories, corrected security path validations, and added a safe, reversible migration script for legacy data.
  - **Path Resolver Standardization (STOR-001)**:
    - Fixed relative `Path("storage") / "projects" / ctx.project_id` in `backend/app/workflow/stages/ingest_stage.py` and `analysis/all_stages.py` to use `settings.PROJECTS_DIR / ctx.project_id`.
    - Eliminated accidental creation of `backend/storage/projects` when running backend processes from `backend/`.
  - **V2 Video Translation Job Storage Relocation (STOR-002)**:
    - Added `TRANSLATOR_DIR` property helper in `backend/app/config.py` pointing to `STORAGE_ROOT / "translator"`.
    - Relocated video translator assets (`/assets`), jobs (`/jobs`), and watermark uploads (`/watermarks`) from `DATA_DIR / "translator"` to `STORAGE_ROOT / "translator"` in `backend/app/api/routes/video_translator.py`, `backend/app/api/routes/video_editor.py`, and `backend/app/core/job_logger.py`.
    - Added backward-compatible read fallback for legacy job logs stored in `DATA_DIR`.
    - Fixed security path traversal validator in `backend/app/services/file_manager.py` to validate against `settings.PROJECTS_DIR` instead of mismatched `settings.DATA_DIR`.
  - **Comprehensive CRUD Cleanup & Orphan Prevention Contract (STOR-003)**:
    - Updated `FileCleanupService.cleanup_project()` to unconditionally purge both unified storage directories (`STORAGE_ROOT`) and legacy orphan directories (`backend/storage/projects/{item_id}` and `DATA_DIR/translator/jobs/{item_id}`).
    - Enhanced `cleanup_job_workspace()` to clean temporary working files (`chunks`, `tts`, `synced`, `work`) across both unified and legacy locations.
    - Enhanced `scan_orphan_files()` to scan unified and legacy directories for unreferenced assets and job folders.
  - **Data Migration & Rollback CLI Tool (STOR-004)**:
    - Created `backend/scripts/migrate_storage.py` supporting `--dry-run` and `--rollback`.
    - Provides non-destructive directory merging, database path rewriting for stored media URLs, and rollback manifest logging (`storage/migration_manifest.json`).
  - **Regression Testing & Schema Resilience**:
    - Added `test_cleanup_project_removes_both_unified_and_legacy_directories` and `test_cleanup_job_removes_both_unified_and_legacy_directories` in `backend/tests/test_storage_and_projects.py`.
    - Fixed invalid `ForeignKey("characters.id")` in `video_translator.py` and `workflow_engine.py` (preventing SQLite `NoReferencedTableError` when creating schema).
  - **Affected Files**: `backend/app/config.py`, `backend/app/workflow/stages/ingest_stage.py`, `analysis/all_stages.py`, `backend/app/api/routes/video_translator.py`, `backend/app/api/routes/video_editor.py`, `backend/app/core/job_logger.py`, `backend/app/services/file_manager.py`, `backend/app/services/cleanup_service.py`, `backend/app/models/video_translator.py`, `backend/app/models/workflow_engine.py`, `backend/scripts/migrate_storage.py`, `backend/tests/test_storage_and_projects.py`, `PROJECT_KNOWLEDGE_BASE.md`, `CHANGELOG_AI.md`.

- **Remaster Visual Gender Detection Pipeline — Run Immediately After STT (2026-09-18)**:
  - **Summary**: Remastered the visual gender detection pipeline so that it executes immediately after STT and before Character Mapping and Translation. Updated keyframe extraction to take 4 representative frames per speaker (0%, 25%, 75%, 100% of speech timeline) and combine them into a single 1024x576 2x2 contact sheet via FFmpeg, querying the Vision API in exactly 1 request per speaker rather than 4 separate requests. Added a unified `VisionProvider` abstraction, robust response parser (`FEMALE` before `MALE` regex checks), and strict priority resolution (`Manual Override > Visual AI > Dialogue LLM > Unknown`).
  - **Pipeline Reordering (`video_translator.py`)**:
    - Relocated Visual Gender Analysis (`detect_speakers_gender`) to run immediately after STT completion (`STT_DONE`).
    - Moved Character Mapping (`map_and_persist`) before Translation, passing `visual_genders` directly as input.
    - Enriched source transcript segments with `character_id`, `speaker_name`, `gender`, and `role` before sending them to `translate_transcript_segments`.
    - Removed redundant post-translation `map_and_persist` invocation.
  - **Multimodal Vision Provider Abstraction (`base.py`, `registry.py`, `gemini_vision.py`, `openai_vision.py`)**:
    - Created `VisionProvider(ABC)` in `app/providers/base.py` defining `analyze_image(...)`.
    - Implemented `GeminiVisionProvider` (`Google Gemini Vision`) and `OpenAIVisionProvider` (`OpenAI Vision GPT-4o/mini`).
    - Registered vision providers in `ProviderRegistry` with accessors `register_vision()`, `get_vision()`, and `list_vision()`.
  - **Visual Gender Service Remaster (`visual_gender_service.py`)**:
    - Implemented `get_speaker_sample_timestamps(...)` to sample active speech intervals at 0% (START), 25%, 75%, and 100% (END).
    - Implemented `create_contact_sheet(...)` combining 4 frames into a standardized 1024x576 2x2 contact sheet with discrete labels (`FRAME 1 - START`, `FRAME 2 - 25%`, `FRAME 3 - 75%`, `FRAME 4 - END`) using system fonts and `expansion=none`.
    - Updated prompt to enforce strict `MALE` or `FEMALE` classification with 8 selection rules (consistent speaker over background characters/bystanders).
    - Implemented `parse_gender_response(...)` with exact match, regex word boundaries (`\bFEMALE\b` before `\bMALE\b`), and tolerant Vietnamese keyword checks (`NỮ` before `NAM`).
    - Added speaker caching and independent per-speaker error handling with structured logging.
  - **Character Mapping Priority (`character_mapping_service.py`)**:
    - Updated `map_and_persist` to accept `visual_genders` and respect priority: `Manual user override (confirmed_by_user) > Visual AI > Dialogue LLM > Unknown`.
    - Updated `decision["gender"]` in `CharacterMappingResult` so downstream stages (Translation, Voice Assignment, TTS) preserve resolved genders.
  - **Testing & Verification (`test_visual_gender_service.py`)**:
    - Wrote comprehensive unit tests covering all 12 mandatory cases: male/female 4 frames, bystander discrimination, exact/regex response parsing, substring collision regression, vision error fallback, invalid text fallback, manual override priority, single short segment distribution, very short video stability, caching, real FFmpeg contact sheet creation, and 1 request per speaker count.
    - Passed all 16 visual gender service tests and full backend test suite (326 passed, 0 failed).
  - **Affected Files**: `backend/app/api/routes/video_translator.py`, `backend/app/services/video_translator/visual_gender_service.py`, `backend/app/services/video_translator/character_mapping_service.py`, `backend/app/providers/base.py`, `backend/app/providers/registry.py`, `backend/app/providers/vision/__init__.py`, `backend/app/providers/vision/gemini_vision.py`, `backend/app/providers/vision/openai_vision.py`, `backend/tests/unit/test_visual_gender_service.py`, `PROJECT_KNOWLEDGE_BASE.md`, `CHANGELOG_AI.md`.

- **Comprehensive Codebase Audit & Single Source of Truth Knowledge Base Sync (2026-09-18)**:
  - **Summary**: Conducted complete structural and architectural audit of AutoTransAI, introspecting all 29 database tables, 100+ API endpoints, services, frontend components, and launcher scripts. Restructured and updated `PROJECT_KNOWLEDGE_BASE.md` into 25 standardized sections adhering to the living documentation mandate.
  - **Database Introspection**:
    - Audited all 29 tables: `ai_function_configs`, `ai_models`, `assets`, `character_voice_profiles`, `errors`, `jobs`, `project_glossaries`, `projects`, `providers`, `qc_reports`, `segments`, `social_accounts`, `speaker_voice_mappings`, `system_settings`, `tiktok_accounts`, `usage_snapshots`, `video_assets`, `video_edit_configs`, `video_merge_assets`, `video_merge_jobs`, `video_thumbnails`, `video_translation_jobs`, `video_translation_segments`, `voice_pool_entries`, `workflow_executions`, `workflow_stage_executions`, `workflow_step_executions`, `youtube_channels`, `youtube_publications`.
    - Documented exact foreign keys, unique constraints, and schema sync mechanics.
  - **Backend & API Architecture**:
    - Catalogued all API routes across `/api/video-translator`, `/api/video-merger`, `/api/thumbnails`, `/api/settings`, `/api/projects`, `/api/providers`, `/api/storage`, `/api/system`, `/api/youtube`, and `/api/tiktok`.
    - Documented services, pipeline error handling, and model resolver priority logic.
  - **Frontend & Workflows**:
    - Documented all 5 pages (`VideoTranslator`, `VideoMerger`, `Dashboard`, `ProjectDetail`, `Settings`) and studio component hierarchy.
    - Detailed the 6-stage unified workflow engine and standalone video merger workflows.
  - **Affected Files**: `PROJECT_KNOWLEDGE_BASE.md`, `CHANGELOG_AI.md`.

- **Fix Auto-Confirm Voice & Auto-Resolve Same-Voice Timeline Overlaps (2026-09-18)**:
  - **Summary**: Fixed issue where enabling "Tự xác nhận nhân vật & giọng đọc hợp lệ" still prompted for confirmation, and fixed pipeline halt in Stage 4 (DUB) caused by "Phát hiện cùng giọng đọc overlap trước Audio Sync".
  - **Auto-Confirm Voice Bypass (`video_translator.py`)**:
    - Previously, low LLM confidence (<85%) or multiple speakers sharing the same default voice forced `character_voice_needs_review = True`, which bypassed the user's `auto_confirm_voice` setting.
    - Updated logic so that when `auto_confirm_voice` is enabled and all segments have valid voices assigned, the system bypasses manual review and automatically launches Phase 2 (TTS & Dubbing).
  - **Same-Voice Overlap Auto-Resolution (`timeline_scheduler.py`, `video_translator.py`)**:
    - Fixed point/zero-duration collision in `_overlap` calculation.
    - Added automatic serialization and tempo compression in `timeline_scheduler.py` when multiple segments share the same voice.
    - Added an auto-resolution step before the Pre-Sync validation gate in `video_translator.py` that serializes or clamps adjacent same-voice segments, preventing false-positive halting with `AUDIO_SCHEDULE_REVIEW`.
    - Ensured that once a user confirms or enables auto-confirm, the pipeline does not re-halt on minor timeline overlaps.
  - **Affected Files**: `backend/app/api/routes/video_translator.py`, `backend/app/services/video_translator/timeline_scheduler.py`, `backend/app/services/video_translator/visual_gender_service.py`, `CHANGELOG_AI.md`.

- **Character & Visual Gender Detection in Settings & Fix API Key/Model Resolution (2026-09-18)**:
  - **Summary**: Added AI Function Configuration & Model Routing for Visual Gender Detection to Settings UI, resolved KeyManager `KeyEntry` object unpacking error, fixed relative debug path resolution crash, and ensured automatic voice assignment on gender toggle.
  - **Settings UI & Database (`settings_service.py`, `model_resolver.py`, `Settings.jsx`)**:
    - Registered `visual_gender` (`Character & Visual Gender Detection`) as a configurable AI Function in Settings, allowing users to route visual gender tasks to custom providers and models (e.g., `gemini-3.5-flash-lite`, `gpt-4o`).
    - Added `VISUAL_GENDER` capability mapping in `model_resolver.py` and seeded existing database records in MySQL.
  - **Visual Gender Service Fixes (`visual_gender_service.py`)**:
    - Fixed bug where `key_mgr.get_active_key(provider)` returned a `KeyEntry` object instead of an API key string, causing Google Gemini API to return `400 Invalid API Key`.
    - Fixed bug where relative path `../data/visual_gender_debug.txt` raised `FileNotFoundError` when executed from the application root directory.
    - Updated default fallback model to `gemini-3.5-flash-lite`.
    - Corrected indentation in `detect_gender_from_image` to avoid dropping successful responses.
  - **Frontend UX (`VideoTranslator.jsx`)**:
    - Updated `handleToggleCharacterGender` and `handleSegmentCharacterChange` so changing or toggling gender immediately applies the user's selected default male or female voice instead of leaving the voice selector empty.
  - **Affected Files**: `backend/app/services/video_translator/visual_gender_service.py`, `backend/app/services/model_resolver.py`, `backend/app/services/settings_service.py`, `frontend/src/pages/VideoTranslator.jsx`, `CHANGELOG_AI.md`.

- **Implement STT Speaker Diarization & Multimodal Visual Gender Detection (2026-09-18)**:
  - **Summary**: Updated STT prompt to require Speaker Diarization to fix fragmented character mapping, and added a visual AI pipeline to auto-detect speaker genders via video keyframes.
  - **Backend STT Enhancements (`translator_service.py`, `stt_parser.py`)**:
    - Updated Gemini STT prompt to explicitly request `Speaker Diarization` (e.g. `Speaker 1`, `Speaker 2`), mitigating the issue where every segment defaulted to unique `UNRESOLVED_xxxx` speakers.
  - **Visual Gender Detection (`visual_gender_service.py`, `character_mapping_service.py`)**:
    - Created `visual_gender_service.py` to extract mid-segment video keyframes using FFmpeg for each distinct speaker.
    - Integrated Gemini 2.0 Flash (Multimodal) to inspect these keyframes and return whether the speaking character is `male` or `female`.
    - Integrated visual detection directly into `map_and_persist` within `character_mapping_service.py`. Visually detected gender is now injected as the authoritative gender prior to character profile creation, falling back to LLM transcript-based guesses if the visual result is uncertain.
  - **Testing (`test_visual_gender_service.py`, `test_stt_parser_diarization.py`)**:
    - Wrote unit tests for `visual_gender_service` logic with mocked API dependencies.
    - Wrote unit tests verifying `stt_parser.py` extracts `speaker_id` successfully.
    - Passed backend test suite (6/6).

- **Support Dual Default Male and Female Voice Configuration (2026-09-18)**:
  - **Summary**: Replaced single default voice control in the Studio configuration panel with two dedicated dropdowns for **Mặc định Nam (Default Male Voice)** and **Mặc định Nữ (Default Female Voice)**, persisting preferences in project settings and applying them during automatic character voice allocation.
  - **Frontend (`VideoTranslator.jsx`)**:
    - Replaced single `Giọng đọc mặc định (Default Voice)` select with two controlled selects: `Mặc định Nam (Default Male)` and `Mặc định Nữ (Default Female)`.
    - Filtered male select strictly to male voices and female select to female voices matching current target language and provider.
    - Synchronized `onChange` handlers of `targetLanguage` and `audioProviderId` to auto-update male and female default selections.
    - Added `default_male_voice_id` and `default_female_voice_id` to settings hydration, dirty checking, and job creation payloads.
  - **Backend (`projects.py`, `video_translator.py`, `voice_assignment_service.py`)**:
    - Added `default_male_voice_id` (`vi-VN-NamMinhNeural`) and `default_female_voice_id` (`vi-VN-HoaiMyNeural`) to `DEFAULT_PROJECT_SETTINGS` and `normalize_project_settings`.
    - Added `default_male_voice_id` and `default_female_voice_id` to `CreateJobRequest` and `settings_snapshot["tts"]`.
    - Updated `assign_voices` and `assign_project_voices` in `voice_assignment_service.py` to prioritize the user's default male and female voice IDs when assigning character voices.
  - **Test Suite & Build Verification**:
    - Added unit test `test_assigns_custom_default_male_and_female_voices` in `test_voice_assignment_service.py` (passing).
    - Executed full unit test suite: 308 passed, 4 skipped out of 312 tests.
    - Executed frontend production build: `npm run build` compiled 100% cleanly without errors.
  - **Affected Files**: `frontend/src/pages/VideoTranslator.jsx`, `backend/app/api/routes/projects.py`, `backend/app/api/routes/video_translator.py`, `backend/app/services/video_translator/voice_assignment_service.py`, `backend/tests/unit/test_voice_assignment_service.py`, `PROJECT_KNOWLEDGE_BASE.md`, `CHANGELOG_AI.md`.

- **Convert Provider & Voice to Controlled Select Dropdowns with Authoritative Validation (2026-09-18)**:
  - **Summary**: Converted plain text inputs for Provider, Voice, and Character into controlled HTML/React `<select>` dropdowns across both the Translation Configuration panel and Segment Review editor, backed by authoritative backend validation.
  - **Frontend Enhancements (`VideoTranslator.jsx`)**:
    - Replaced raw text inputs with `<select>` elements for Provider, Voice, and Character.
    - Provider select dynamically draws registered audio providers (`edge_tts`, `google_cloud_tts`, `elevenlabs`) with formatted display labels and availability indicators.
    - Voice select is dynamically populated from provider voice cache, strictly filtered by target language (`target_language`) and character gender (`male`/`female`).
    - Genders marked as `unknown` display `[ Chưa xác định giới tính ]` without pre-selecting a voice, and provide quick toggles (`♂ Nam` / `♀ Nữ`) to resolve gender interactively.
    - Character select displays human-readable character labels (`Name — Gender`) while preserving stable `character_id` as the underlying value.
    - Switching provider immediately invalidates previous voice selection, preventing provider/voice mismatch.
    - Existing/legacy records resolve to human-readable options or display explicit disabled `⚠️` options when unavailable.
  - **Backend Audio Providers & Voice Registries**:
    - Updated `edge_tts_provider.py`, `google_tts_provider.py`, and `elevenlabs_provider.py` with fallback voices and gender/language metadata for resilient offline and test operation.
  - **Authoritative Backend API Validation (`video_translator.py`)**:
    - Implemented `validate_voice_assignment()` helper to validate provider registration, voice existence for provider, target language compatibility, and character gender matching.
    - `PUT /jobs/{job_id}/character-voice-review`: Validates voice assignments and rejects invalid assignments with HTTP 400.
    - `POST /jobs/{job_id}/character-voice-review/validate`: Validates all segment voice assignments, reporting specific issues (`invalid_provider`, `invalid_voice`, `target_language_mismatch`, `gender_mismatch`, `gender_unresolved`).
    - Enriched segment review data with `characters` array and mapped `character_name` and `gender` per segment.
  - **Test Suite & Build Verification**:
    - Created `backend/tests/unit/test_character_voice_validation_api.py` with 13 unit tests covering all validation rules and API endpoints (100% passing).
    - Executed full unit test suite: 307 passed, 4 skipped out of 311 tests.
    - Executed frontend production build: `npm run build` compiled 100% cleanly without errors.
  - **Affected Files**: `frontend/src/pages/VideoTranslator.jsx`, `backend/app/api/routes/video_translator.py`, `backend/app/providers/audio/edge_tts_provider.py`, `backend/app/providers/audio/google_tts_provider.py`, `backend/app/providers/audio/elevenlabs_provider.py`, `backend/tests/unit/test_character_voice_validation_api.py`, `PROJECT_KNOWLEDGE_BASE.md`, `CHANGELOG_AI.md`.

- **Execution of Post-Implementation Verification Audit Fixes (2026-09-18)**:
  - **Summary**: Implemented five verified fixes identified during the post-implementation audit, investigated browser playback codecs, added 5 regression tests, and synchronized documentation.
  - **Fix 1 — Target Language Injection (`video_translator.py`, `voice_assignment_service.py`)**:
    - Resolved `target_language` dynamically from `b_job.settings_snapshot_json` / job configuration instead of defaulting to `vi-VN` at call site.
    - Supported normalized language codes (`vi`, `vi-VN`, `en`, `en-US`, `zh`, `zh-CN`).
    - Filtered candidate voices in `assign_voices` strictly by target language.
  - **Fix 2 — Auto-Confirm Cross-Contamination (`video_translator.py`, `projects.py`, `video_translator.py` model)**:
    - Decoupled `auto_confirm_translation` and `auto_confirm_voice`.
    - Added `auto_confirm_voice` setting to job model, requests, default project settings, and snapshot.
    - If any required character voice profile is unconfirmed (`confirmed_by_user=False`) and `auto_confirm_voice=False`, translation confirmation will not trigger TTS rendering; job halts cleanly at `NEEDS_REVIEW` / `CHARACTER_VOICE_REVIEW`.
  - **Fix 3 — Stable Character Identity (`character_mapping_service.py`)**:
    - Updated `map_and_persist` to prioritize stable `speaker_id` persistent mapping lookup in `SpeakerVoiceMapping` to reuse `character_id`.
    - Protected user-confirmed `CharacterVoiceProfile` records (`confirmed_by_user=True`) from LLM name/gender/role overwrite on retries or character mapping regeneration.
  - **Fix 4 — Unicode Download Headers (`storage.py`)**:
    - Removed manual `headers={"Content-Disposition": ...}` string formatting from `FileResponse` in download endpoint.
    - Relied on Starlette's native `FileResponse(path, filename)` RFC 5987 header formatting, resolving `UnicodeEncodeError` for filenames with Chinese characters (`未日临先锋圣母_哔哩哔哩_bilibili.mp4`), Vietnamese diacritics, spaces, and special characters.
  - **Fix 5 — Async File Copy (`service.py`)**:
    - Replaced synchronous `shutil.copy2(...)` in `VideoSourceService.import_uploaded_file` with `await asyncio.to_thread(shutil.copy2, source_path, dest_path)` to prevent blocking the FastAPI event loop.
  - **Fix 6 — Browser Playback Codecs Investigation (`ffprobe.py`, `sync_service.py`)**:
    - `get_video_metadata` extracts `video_codec` (`codec_name`).
    - `VideoAudioSyncService.render_and_mux_video` uses `-c:v copy` for standard H.264/avc1 video streams, but automatically falls back to `-c:v libx264 -pix_fmt yuv420p` when muxing non-H.264 video streams (HEVC/VP9/AV1/ProRes) to guarantee universal browser playback compatibility.
  - **Fix 7 — Unit & Regression Test Verification (`test_audit_verified_fixes_regression.py`)**:
    - Added 5 regression tests covering target language boundary, independent confirmation, confirmed character persistence, unicode download, and async file copy.
    - Ran unit test suite: 294 passed out of 294.
    - Ran frontend production build: `npm run build` 100% clean.
  - **Affected Files**: `backend/app/api/routes/video_translator.py`, `backend/app/services/video_translator/voice_assignment_service.py`, `backend/app/services/video_translator/character_mapping_service.py`, `backend/app/api/routes/storage.py`, `backend/app/services/video_source/service.py`, `backend/app/media/ffprobe.py`, `backend/app/services/video_translator/sync_service.py`, `backend/app/models/video_translator.py`, `backend/app/api/routes/projects.py`, `backend/tests/unit/test_audit_verified_fixes_regression.py`, `PROJECT_KNOWLEDGE_BASE.md`, `CHANGELOG_AI.md`.

- **Execution of Plan.md: Voice Allocation, Dual Confirmation Gates & Workflow Engine Refinements (2026-09-18)**:
  - **Summary**: Implemented comprehensive architectural fixes and validation policies outlined in `Plan.md`.
  - **Voice Allocation & Target Language / Gender Enforcement (`voice_assignment_service.py`)**:
    - `assign_voices` and `assign_project_voices` strictly filter candidate voices by job target language (`target_language`, e.g. `vi-VN`) and gender (`male` / `female`).
    - Foreign-language fallback (e.g., assigning English voice `en-US-GuyNeural` for Vietnamese target) has been completely removed. Unresolvable voice/gender now triggers `no_available_voice` / `GENDER_UNRESOLVED` review gate.
    - Preserved user-confirmed `CharacterVoiceProfile` records from LLM overwrite.
    - Voice conflict identity now uses provider identity tuple `(voice_provider, voice_id)`.
  - **Dual Independent Confirmation Gates (`video_translator.py`, `VideoTranslator.jsx`)**:
    - Introduced `auto_confirm_voice` setting alongside `auto_confirm_translation`. Both gates must pass validation before Phase 2 (`GENERATING_TTS` / `DUB`) execution.
    - Updated studio UI with checkboxes for `Tự xác nhận bản dịch hợp lệ` and `Tự xác nhận nhân vật & giọng đọc hợp lệ`.
  - **Unified Workflow Engine Repair (`dub_stage.py`, `produce_stage.py`)**:
    - Replaced calls to non-existent `VideoTranslatorService` with direct calls to `get_registry()` and `VideoAudioSyncService` (`build_dubbed_audio_timeline`, `render_and_mux_video`).
  - **Audio & Render Quality Enforcement (`translator_service.py`)**:
    - TTS synthesis errors are logged with full tracebacks and fail cleanly instead of silently replacing speech clips with silence.
    - Output video FFprobe duration and stream validation strictly enforced before job completion.
  - **Affected Files**: `backend/app/services/video_translator/voice_assignment_service.py`, `backend/app/services/video_translator/character_mapping_service.py`, `backend/app/api/routes/video_translator.py`, `backend/app/workflow/stages/dub_stage.py`, `backend/app/workflow/stages/produce_stage.py`, `frontend/src/api.js`, `frontend/src/pages/VideoTranslator.jsx`, `PROJECT_KNOWLEDGE_BASE.md`, `CHANGELOG_AI.md`.

- **Fix SAME_VOICE_OVERLAP & Confirm Validation Gate in Video Translator (2026-09-17)**:
  - **Symptom & Stack**:
    ```text
    [NEEDS_REVIEW] Audio schedule requires review due to same-voice overlap.
    [CONFIRM_RESUME] User confirmed Character/Voice and Audio Schedule review. Proceeding to TTS & Dubbing.
    ...
    [RENDER] Final FFmpeg render starting...
    ValueError: SAME_VOICE_OVERLAP: segments 53 and 54 use en-US-GuyNeural
    ```
  - **Root Causes**:
    1. `validate_character_voice_review` evaluated `passed = len(missing) == 0`, ignoring unresolved voice conflicts and audio schedule overlaps.
    2. `execute_job_render_pipeline` bypassed `schedule_result.requires_review` if `is_review_confirmed` was True, continuing into Audio Sync and FFmpeg render despite active conflicts.
    3. Frontend polling polled every 1.5s and called `setSegments(newJob.segments)` directly from DB, wiping out user-edited voice selections during `needs_review` and sending updates purely by `speaker_id`.
    4. TTS cache checked only file existence, ignoring whether `voice_id` or text had changed on disk.
  - **Fix 1 — Strict Validation & Deduplicated Issues (`video_translator.py`)**:
    - `validate_character_voice_review` now validates missing assignments and runs `schedule_segments` across the actual audio timeline.
    - Flags direct and scheduler `same_voice_overlap` issues with structured details (`segment_ids`, `segment_numbers`, `voice_id`, `message`).
    - Issues deduplicated with stable key: `(reason, tuple(sorted(segment_ids)), voice_id)`.
    - `passed = len(missing) == 0 and len(issues) == 0`.
  - **Fix 2 — Strict Confirm & Resume Gate (`video_translator.py`)**:
    - `confirm_character_voice_review` re-validates schedule. If conflicts exist, raises HTTP 409, logs `[CONFIRM] Review confirmation rejected because unresolved conflicts remain`, maintains `NEEDS_REVIEW`, and rejects rendering.
    - Idempotent: Duplicate confirms while processing or completed return cleanly without duplicate tasks.
  - **Fix 3 — Elimination of Render Bypass & Double Validation Gates (`video_translator.py`)**:
    - `execute_job_render_pipeline` never bypasses `schedule_result.requires_review`. If unresolved, halts immediately and keeps `NEEDS_REVIEW`.
    - Added Pre-Sync Gate and Pre-Render Gate before FFmpeg render to ensure `same_voice_overlap == False`.
    - Preserved `sync_service.py` `ValueError: SAME_VOICE_OVERLAP` as defensive safety net.
  - **Fix 4 — Auto-Resolution via VoicePoolEntry (`video_translator.py`)**:
    - Conflicting unconfirmed segments attempt deterministic replacement from `VoicePoolEntry` (matching language/gender).
    - If resolved: invalidates cache for that segment only, regenerates TTS for that segment, re-schedules, logs `[AUDIO_SCHEDULE] Conflict resolved`, and continues.
  - **Fix 5 — Granular TTS Cache Invalidation with Sidecar Metadata (`video_translator.py`)**:
    - Sidecar metadata `seg_{num}.meta.json` tracks `{voice_id, voice_provider, translated_text}`.
    - Changing segment 53's voice invalidates and regenerates only segment 53 (`[TTS_CACHE] Invalidating segments: [53]`, `[TTS] Regenerating segments: [53]`), while segments 1-52 and 54 are kept cached.
  - **Fix 6 — Frontend Polling & State Stability (`VideoTranslator.jsx`)**:
    - Polling merges server updates while preserving user form inputs for `character_id`, `voice_provider`, `voice_id`, and `translated_text` during `needs_review` and `segment_editing`.
    - Supports per-segment `segment_id` in mappings update.
    - Formats structured conflict error messages cleanly in the UI.
  - **Fix 7 — Comprehensive Regression Suite (`test_same_voice_overlap_lifecycle.py`)**:
    - Added tests for all 7 required cases (Same voice non-overlapping, Same voice overlapping, Confirm with conflict rejected, User voice change resolved, Granular TTS caching, Duplicate confirm idempotency, Completed job terminal guard). All 7 passed.
  - **Affected files**: `backend/app/api/routes/video_translator.py`, `frontend/src/pages/VideoTranslator.jsx`, `backend/tests/unit/test_same_voice_overlap_lifecycle.py`, `PROJECT_KNOWLEDGE_BASE.md`, `CHANGELOG_AI.md`.

- **Fix Verbatim Echoes: Targeted Segment Recovery, Preservation & Clean Provider Failover (2026-09-17)**:
  - **Symptom & Production Log**:
    ```text
    STT completed: Chinese | Validated Segments: 42
    Gemini Translation: input_count=42, output_count=42, missing_count=0
    Translation validation failed on Gemini: 22/42 segments were verbatim echoes.
    ```
  - **Root Cause**: Gemini returned 42 outputs matching the segment count, but 22 segments were verbatim echoed Chinese source text instead of translated Vietnamese. Previously, verbatim echoes failed the whole batch or triggered whole-batch retries that could hallucinate or loop without preserving the 20 already valid segments.
  - **Fix 1 — `is_verbatim_echo()` Linguistic Validator (`translator_service.py`)**: Checks for exact string identity on linguistic content and pure CJK characters when translating from Chinese to non-Chinese languages. Safely ignores non-linguistic tokens (numbers, punctuation) and source segments lacking CJK characters.
  - **Fix 2 — Targeted Segment Retry with Valid Segments Preservation (`translator_service.py`)**: When verbatim echoes or missing translations are detected, the pipeline isolates ONLY the invalid segment IDs (e.g. 22/42), preserving the 20 valid ones. It sends a targeted correction prompt specifying source and target languages, strict translation rules, and exact segment IDs (`invalid_ids`), then cleanly merges the corrected translations into the final list (20 + 22 = 42).
  - **Fix 3 — Preserved Core Validation Rule & Clean Failover (`translator_service.py`)**: Kept the exact validation `err_msg = f"Translation validation failed on {llm.provider_name}: {untranslated_count}/{len(segments)} segments were verbatim echoes."`. If echoes persist across all retry attempts, the provider cleanly fails and triggers candidate provider failover without creating new jobs or resetting segment indices to 0.
  - **Fix 4 — Structured Audit Logging (`translator_service.py`)**:
    - `[Translation Audit] batch=1/1 input=42 output=42 valid=20 verbatim_echo=22 missing=0 retry_ids=[...]`
    - `[Translation Retry] retry_count=1 retry_input=22 retry_output=22 remaining_invalid=0`
    - `[TRANSLATION COMPLETED] job_id=... segments=42 translated=42`
  - **Fix 5 — Comprehensive Regression Tests (`test_workflow_lifecycle_regression.py`)**:
    - `test_verbatim_echo_targeted_retry_and_merge`: Verified 42 inputs with 22 echoes retrying only the 22 invalid items, preserving 20 valid items, and merging 42 final segments.
    - `test_verbatim_echo_persistent_triggers_validation_error_and_failover`: Verified persistent echoes trigger the exact validation failure and failover cleanly to the fallback provider.
  - **Verification**: All 282 backend unit tests pass (4 skipped).
  - **Affected files**: `translator_service.py`, `test_workflow_lifecycle_regression.py`, `PROJECT_KNOWLEDGE_BASE.md`, `CHANGELOG_AI.md`.

- **Fix Translation Workflow Infinite Loop & State Machine Integrity (2026-09-17)**:
  - **Root Causes**:
    1. `execute_job_render_pipeline` invoked `schedule_segments()` which marked `cannot_fit` and set `requires_review = True` on same-voice segments exceeding 3.0s displacement, causing the pipeline to halt and transition to `status = "needs_review"`, `stage = "AUDIO_SCHEDULE_REVIEW"`.
    2. `STAGE_MAP` in `get_workflow_status_api` lacked `"AUDIO_SCHEDULE_REVIEW"`, causing the 6-stage workflow to fall back to `("INGEST", 1)`. The UI displayed *Stage 1: INGEST (Chờ xác nhận)* despite 80% progress and 45/45 segments translated.
    3. Clicking "Xác Nhận Nhân Vật / Giọng Đọc & Tiếp Tục Render TTS" called `confirm_character_voice_review`, which re-launched `execute_job_render_pipeline`. It hardcoded `completed_segments_count = 0` and `current_step = "Đang tạo giọng đọc TTS (0/N)"`, re-ran `schedule_segments()` with the identical strict 3.0s policy, halted at 45/45 again, and returned to review — causing an infinite loop.
    4. Clicking "Retry Stage INGEST" or `smart_retry_job_api` unconditionally invoked `start_translation_pipeline`, which deleted all existing segments (`delete(VideoTranslationSegment)`) and re-translated from segment 0.
  - **Fix 1 — STAGE_MAP Alignment (`video_translator.py`)**: Added `"AUDIO_SCHEDULE_REVIEW": ("DUB", 4)`, `"TTS_DONE": ("DUB", 4)`, and `"AUDIO_SYNC_DONE": ("DUB", 4)` to `STAGE_MAP`. Workflow stage accurately displays Stage 4 (DUB) instead of falling back to INGEST.
  - **Fix 2 — Review Confirmation & Relaxed Schedule Policy (`video_translator.py`)**: `confirm_character_voice_review` now persists `review_confirmed = True` and `audio_schedule_confirmed = True` in `settings_snapshot_json`. `execute_job_render_pipeline` detects this confirmation, applies a relaxed schedule policy (`max_reschedule_seconds=60.0`, `max_tempo=2.0`), serializes same-voice segments, and continues directly to Audio Sync and Final Render instead of halting.
  - **Fix 3 — Segment Progress & TTS Caching Preservation (`video_translator.py`)**: Pre-scans existing valid `.wav` clips in `execute_job_render_pipeline` before the generation loop, initializing `completed_segments_count` to the cached count rather than resetting to 0.
  - **Fix 4 — Smart Retry Phase 2 Routing (`video_translator.py`)**: `smart_retry_job_api` and `retry_stage_api` check `last_checkpoint_stage` and existing segments. Retries for `DUB`, `AUDIO_SCHEDULE_REVIEW`, or later stages resume directly into Phase 2 without wiping translated segments or re-running Phase 1 STT/translation.
  - **Fix 5 — One-Shot Auto-Confirm (`video_translator.py`)**: Added `auto_confirm_executed` snapshot guard to `auto_confirm_and_start_render_if_needed`, ensuring auto-confirm executes strictly once and cannot be re-triggered by status polling or heartbeat loops.
  - **Fix 6 — Terminal COMPLETED Guards (`video_translator.py`)**: Added checks in `start_translation_pipeline`, `execute_job_render_pipeline`, `render_final_translated_video`, and `smart_retry_job_api` to immediately return without re-running if job status is `COMPLETED`.
  - **Fix 7 — Frontend Button State Machine (`WorkflowTimeline.jsx`)**: Guarded "Start" button from rendering when workflow status is `completed` or `needs_review`.
  - **Fix 8 — Regression Test Suite (`test_workflow_lifecycle_regression.py`)**: Created 5 comprehensive unit tests verifying one-shot auto confirm, terminal completed protection, STAGE_MAP mapping, review confirmation bypass, and smart retry Phase 2 resume. All 280 unit tests pass (4 skipped).
  - **Affected files**: `video_translator.py`, `WorkflowTimeline.jsx`, `test_workflow_lifecycle_regression.py`, `PROJECT_KNOWLEDGE_BASE.md`.

- **Complete GLOSSARY_ENFORCEMENT_FAILED pipeline fix — final verification (2026-09-17)**:
  - **Completion**: All fixes from the glossary enforcement pipeline overhaul verified and passing.
  - **Fix 1 — `terminology_extractor.py`**: Added `is_chinese_language()`, `has_cjk_characters()`, `is_pure_cjk()`, `is_valid_glossary_mapping()` utilities. Updated `heuristic_extract_terms()`, `normalize_extracted_terms()`, `llm_extract_terms()`, `persist_detected_terms()`, and `extract_and_persist_from_segments()` to reject CJK self-mapped entries when target language is non-Chinese.
  - **Fix 2 — `translator_service.py`**: Updated `_translation_json_prompt` with rule 3 requiring name transliteration in target language. Updated `find_glossary_violations()` to skip invalid entries with warnings. Added targeted 1-step retry for valid glossary violations in `translate_transcript_segments()`. Raises `RuntimeError("GLOSSARY_ENFORCEMENT_FAILED")` only after retry fails for valid violations.
  - **Fix 3 — `video_translator.py` (backend routes)**: Guarded `auto_confirm_and_start_render_if_needed` against running when `job.status == NEEDS_REVIEW`.
  - **Fix 4 — `VideoTranslator.jsx` (frontend)**: Deduplicated validation error reasons using `Set` so `voice_conflict` appears only once.
  - **Fix 5 — `test_glossary_enforcement.py`**: Fixed `GlossaryMockLLM` class — moved `LLMProvider` import to module level, removed duplicate function header that broke class scoping. 22 test cases pass.
  - **Verification**: 275 backend unit tests passed (4 skipped), frontend Vite build clean.
  - **Affected files**: `terminology_extractor.py`, `translator_service.py`, `video_translator.py` (routes), `VideoTranslator.jsx`, `test_glossary_enforcement.py`
  - **Knowledge Base**: Updated TRANSLATE stage in `PROJECT_KNOWLEDGE_BASE.md` with `is_valid_glossary_mapping()`, targeted retry, and invalid glossary skip behaviour.

- **Fix GLOSSARY_ENFORCEMENT_FAILED: language-aware glossary enforcement pipeline (2026-09-17)**:
  - **Root Cause**: Self-mapped CJK glossary entries (`source_term=安妮, translated_term=安妮`) were created via `_persist_translation_names` → `persist_detected_terms`, which lacked the CJK self-mapping filter present only in `extract_and_persist_from_segments`. These entries then caused `find_glossary_violations` to falsely flag valid translations (e.g. Vietnamese "Annie") as violations because the enforcement demanded Chinese characters in Vietnamese output.
  - **Fix 1 — `is_self_mapped_cjk()` utility** (`terminology_extractor.py`): Centralized CJK self-mapping detection. Returns True only when source is purely CJK, maps to itself, and target language is NOT Chinese. Latin/ASCII self-maps (`AI→AI`, `Netflix→Netflix`) are never flagged.
  - **Fix 2 — `persist_detected_terms`** (`terminology_extractor.py`): Now accepts `target_lang` param and filters out self-mapped CJK entries before saving to DB. This prevents invalid entries from being created in the first place.
  - **Fix 3 — `find_glossary_violations`** (`translator_service.py`): Now accepts `source_language` and `target_language` params. Skips enforcement for invalid self-mapped CJK entries with structured logging (`GLOSSARY_SKIP_INVALID_MAPPING`). Only valid violations raise `GLOSSARY_ENFORCEMENT_FAILED`.
  - **Fix 4 — `_translation_json_prompt`** (`translator_service.py`): Filters self-mapped CJK entries from glossary rules sent to LLM, preventing confusing instructions like "translate 安妮 as 安妮".
  - **Fix 5 — `translate_stage.py`**: `_check_consistency` now passes `source_language` and `target_language` from workflow context to `find_glossary_violations`.
  - **Fix 6 — `llm_extract_terms` prompt** (`terminology_extractor.py`): Explicitly instructs LLM that CJK `suggested_term` MUST be the target-language rendering, not the original Chinese characters.
  - **Fix 7 — Voice conflict deduplication** (`video_translator.py`): `validate_character_voice_review` now deduplicates `voice_conflict` issues by character pair, preventing the same conflict from appearing multiple times.
  - **Fix 8 — Test mock** (`test_gemini_translation.py`): Updated `fake_persist` mock to accept new `target_lang` kwarg.
  - **Affected files**: `terminology_extractor.py`, `translator_service.py`, `translate_stage.py`, `video_translator.py`, `test_gemini_translation.py`
  - **New test file**: `test_glossary_enforcement.py` (18 test cases covering all scenarios)
  - **Knowledge Base**: Updated TRANSLATE stage description in `PROJECT_KNOWLEDGE_BASE.md`

- **Fix GLOSSARY_ENFORCEMENT_FAILED crash due to untranslated CJK terms (2026-09-17)**:
  - **Symptom**: Jobs translating Chinese to Vietnamese crashed in the `TRANSLATE` stage with `GLOSSARY_ENFORCEMENT_FAILED` because the LLM terminology extractor captured untranslated names (e.g. `{"source_term": "安妮", "required": "安妮"}`). The glossary then forced the translator to output raw Chinese characters, which the Vietnamese translation naturally didn't include.
  - **Fix**: Upgraded `extract_and_persist_from_segments` in `terminology_extractor.py` to apply the untranslated CJK filter *globally* to both LLM-extracted and Heuristic-extracted terms. Now, if `source_term` matches `suggested_term`, is entirely CJK, and the target language is not Chinese, the term is strictly rejected.


- **Fix Auto Confirm voice_conflict bug and Proper Name validation strictness (2026-09-17)**:
  - **Symptom 1**: Auto Confirm was blocked by repetitive `voice_conflict` errors when overlapping speakers were assigned the same voice.
  - **Fix 1**: Modified `start_translation_pipeline` to prioritize `auto_confirm`, bypassing the `NEEDS_REVIEW` stage completely. Modified `validate_character_voice_review` to downgrade `voice_conflict` to a non-blocking warning so users aren't permanently stuck if voice pool exhaustion causes unavoidable conflicts.
  - **Symptom 2**: AI hallucinatory or mispelled names (like `tiếng viêt` instead of `tiếng Việt`) were extracted and saved into the database, violating the strict exact-match requirement.
  - **Fix 2**: Implemented `validate_and_align_extracted_terms` in `terminology_extractor.py`. This cross-references AI extracted terms precisely against the isolated original source text (avoiding pollution from translated text). It forces exact substring deduplication and drops any terms not found in the source text.


- **Fix Smart Retry and `CHARACTER_VOICE_REVIEW` stage mapping alignment (2026-09-17)**:
  - **Symptom**: When a job completed Phase 1 translation but speaker mapping confidence was low or voice conflicts occurred, the stage stuck on `INGEST` (Stage 1) despite 60% completion. Clicking `Retry` or `Retry Stage` failed to reset/retry the job, leaving the red error `Character/Voice chưa hợp lệ: voice_conflict, voice_conflict` permanently on screen.
  - **Root Cause**:
    1. `STAGE_MAP` in `get_workflow_status_api` omitted `"CHARACTER_VOICE_REVIEW"`, causing `STAGE_MAP.get(job.stage)` to fall back to `("INGEST", 1)`.
    2. `retry_stage_api` checked `job.status in [FAILED, SEGMENT_EDITING, CREATED]` but omitted `NEEDS_REVIEW`, causing retry calls on jobs in `needs_review` to be ignored without restarting the pipeline or clearing `error_message`.
    3. `assign_voices` and `assign_project_voices` in `voice_assignment_service.py` failed to auto-resolve voice conflicts for unconfirmed speakers when retrying.
  - **Fix**:
    1. Mapped `"CHARACTER_VOICE_REVIEW": ("TRANSLATE", 3)` in `STAGE_MAP` and aligned `st_status` in `get_workflow_status_api`.
    2. Added `TranslationJobStatus.NEEDS_REVIEW.value` to `retry_stage_api` allowed restart statuses.
    3. Enhanced `assign_voices` to auto-resolve unconfirmed voice conflicts by selecting distinct available pool voices for overlapping speakers.
  - **Verification**: Verified clean React build (`npm run build` 100% clean) and backend test suite (`pytest` unit/integration tests passed).

- **Enforce Single Cover Photo Selection Mode for Project Default Thumbnails (2026-09-17)**:
  - **Symptom**: Selecting/uploading default project thumbnails accumulated multiple images in a grid gallery instead of managing 1 single active cover photo.
  - **Fix**:
    1. **Backend** (`app/api/routes/thumbnail.py`): Updated `upload_default_thumbnail` to automatically purge previous cover photos in `storage/projects/{id}/default_thumbnails/` before saving the new file, and updated `list_default_thumbnails` to return only the single latest cover photo.
    2. **Frontend** (`VideoTranslator.jsx` & `api.js`): Replaced multi-thumbnail grid with a clean Single Cover Photo Component (displays single image preview card, image details, `📷 Thay đổi ảnh` replace button, and `🗑️ Xóa ảnh` button, or a single upload dropzone when empty). Added `deleteLibrary` API call.
  - **Verification**: Verified clean React build (`npm run build` 100% clean) and backend unit tests (`pytest test_workflow_engine.py` 100% pass).

- **Fix `needs_review` state polling reset and unclickable confirm button (2026-09-17)**:
  - **Symptom**: When a job completed Phase 1 translation but speaker mapping confidence was low or voice conflicts occurred, the backend placed the job into `needs_review` status. However, the confirm button was permanently disabled (`isProcessing = true`) and unclickable, and the Segment Editor card failed to render.
  - **Root Cause**:
    1. `VideoTranslator.jsx` status polling omitted `'needs_review'` from the list of terminal/review statuses that call `setIsProcessing(false)`, leaving `isProcessing` stuck as `true`.
    2. `SegmentEditor` render condition checked `job.status === 'segment_editing'` but omitted `'needs_review'`, hiding the segment editor and character/voice input fields.
    3. `handleValidateAndResumeCharacterVoices` lacked a `try...catch...finally` wrapper, throwing unhandled exceptions and failing to clear `isProcessing` on validation failure.
  - **Fix**: Added `'needs_review'` to `setIsProcessing(false)` status checks, included `'needs_review'` in Segment Editor render condition and `WorkflowTimeline` status mappings, wrapped `handleValidateAndResumeCharacterVoices` with `try...catch...finally`, and updated the button label and state handling.
  - **Verification**: Verified clean React build (`npm run build` 100% clean) and status state flow.

- **Fix Windows Desktop Launcher Frontend Readiness Check Failure (2026-09-17)**:
  - **Symptom**: App could not be opened via shortcut `run_app.bat` / `AutoTransAI Studio.lnk` because the launcher timed out waiting for Vite frontend readiness (`Frontend exited or did not become ready (exit=None)`).
  - **Root Cause**: `app_launcher.py` checked readiness by probing `FRONTEND_URL` (`http://127.0.0.1:5173`) over IPv4, but `npx vite --port 5173` without explicit `--host 127.0.0.1` bound only to IPv6 `localhost` (`::1:5173`), causing HTTP connection attempts to `127.0.0.1` to be refused until the readiness check timed out.
  - **Fix**: Added explicit `--host 127.0.0.1 --port 5173` flags to Vite execution calls in `app_launcher.py`, `app_launcher.ps1`, and `frontend/start_frontend.cmd`.
  - **Verification**: Verified readiness check with automated test script (`test_launch.py`); both backend and frontend successfully start and pass HTTP 200 health checks.

- **Fail-fast Windows Shortcut launcher with visible startup diagnostics (2026-09-16)**:
  - **Symptom**: Opening the Shortcut displayed the Vite UI, but project creation and Local Storage tests failed through the proxy because FastAPI had already stopped; `pythonw.exe` and `DEVNULL` hid the traceback.
  - **Fix**: `app_launcher.py` now logs backend/frontend startup to `data/launcher_logs/`, requires a live launcher-owned backend before starting Vite, requires a live launcher-owned Vite process before opening pywebview, and shows the failed component plus diagnostic detail/log path in a Windows error dialog.
  - **Process safety**: Removed Uvicorn `--reload`, refuses pre-existing listeners on ports 8000/5173, and removes broad port-owner termination so cleanup only targets child process trees created by this launcher. Added regression tests for readiness/process-exit failure, occupied-port ownership, log setup/capture, backend spawn failure, and reloader exclusion.

- **Project Glossary is the single terminology source of truth (2026-09-16)**:
  - Removed the AI Auto Terminology Memory model, runtime table, endpoints, UI tab, and dual-source translation lookup.
  - AI terminology detection now writes directly through the canonical Glossary service before translation.
  - NFKC/invisible/whitespace/case normalization plus two project-scoped unique keys enforce a 1:1 source/translation mapping under retries and races.
  - Added conflict-safe add/edit APIs, legacy-data migration audit, Studio/Unified prompt enforcement, and a pre-TTS canonical validation gate.

- **Pollinations AI Image Provider added to AI Function Config options (2026-09-16)**:
  - **Status**: Verified Pollinations AI image generation (`https://image.pollinations.ai/prompt/...`) is 100% functional, free, and requires no API key.
  - **Fix**: Added `pollinations` to `known_providers` in `SettingsService.get_eligible_providers_for_function` so it now populates as a selectable provider option for capability `IMAGE_GENERATION` in Settings -> AI Function Config -> `Image & Asset Generation`.
  - **Defaults**: Updated `DEFAULT_AI_FUNCTIONS` for `image_generation` to default to `pollinations` (`pollinations-default`), and added auto-fallback logic in `ensure_defaults_seeded` for existing databases initialized with unconfigured `fal`.

- **Translate STT as one numbered JSON and save names (2026-09-15)**:
  - Auto gửi `{"lines":[{"n":1,"text":"..."}]}` (n = thứ tự STT) và nhận cùng dạng kèm `names` (nhân vật/địa danh/tổ chức). Gắn dịch lại đúng câu. Tên lưu terminology memory. JSON quá dài vẫn tách lô như cũ.

- **Studio option checkboxes on one equal-width row (2026-09-15)**:
  - Auto-Confirm, Tự cắt intro/outro, and `Kiểm tra bản quyền` sit in one `repeat(3, 1fr)` row so the third label no longer wraps shorter than the others.

- **Bilibili `/video/av…` URLs resolve duration without yt-dlp (2026-09-15)**:
  - Studio `Kiểm tra URL` on `https://www.bilibili.com/video/av14901263585041?t=26.0` returned HTTP 400 `Không lấy được thời lượng Bilibili` because the parser only accepted `BV…`. AV/aid now uses `pagelist?aid=` and playurl/view APIs the same way.

- **Studio Auto actually generates the YouTube thumbnail (2026-09-15)**:
  - Checkbox `Tự Động Tạo Thumbnail AI` was saved on the Studio form but dropped by `CreateJobRequest` and never run in `execute_job_render_pipeline` (only WorkflowEngine PRODUCE). Snapshot now stores the flag; after render Auto calls Pollinations. YouTube modal generates on open if missing, plus nút `Tạo thumbnail AI ngay`.

- **Tighten Auto Memory: drop verbs/kinship/conjunction n-grams (2026-09-15)**:
  - Screenshot still showed `爬上`, `弟子`, `哥哥`, `上车`, `而且門派` as Character/Location. 2-char CJK now requires a common surname (`张三`, `姜男`, `李四`); `派`/`门` alone is not a place; prefixes like `而且` are rejected. `李飞羽` → Lý Phi Vũ and toponyms like `基途河` stay.

- **Terminology Memory keeps proper names only; TTS no longer hangs DUB (2026-09-15)**:
  - **Memory**: Heuristic CJK n-grams saved subtitle clauses as `Other 60%` (`看来今天`, `我先走了`) and required Duyệt vào Glossary. Extractor now keeps character/location/organization names only, skips function-word fragments, and does not set `needs_review`. GET hides leftover junk. Prompt tells Gemini: names only, no clauses.
  - **DUB stall**: Job stuck at `Đang tạo giọng đọc TTS (31/193)` because `edge_tts.Communicate.save` had no timeout. Each segment now has a 45s timeout (3 attempts), empty text is skipped, already-written wav files are reused so Retry Stage DUB continues from 32/193.

- **TikTok Login Kit OAuth + open Chrome tab, not the app window (2026-09-15)**:
  - **Ask**: Connect TikTok like YouTube, and stop OAuth from taking over the desktop app (pywebview / Edge `--app=`), which cannot return after TikTok/Google login.
  - **Auth**: `GET /api/tiktok/auth-url` builds `https://www.tiktok.com/v2/auth/authorize/` with desktop PKCE (hex SHA256 challenge). Callback exchanges code at `open.tiktokapis.com/v2/oauth/token/`, fetches display name, encrypts tokens into `tiktok_accounts`.
  - **Chrome**: `POST /api/system/open-browser` only allows Google/TikTok authorize HTTPS URLs and runs `chrome --new-tab`. YouTube OAuth uses the same path. Callback shows “đóng tab Chrome, quay lại AutoTransAI”; Settings polls for the new account.
  - **Config**: `TIKTOK_CLIENT_KEY`, `TIKTOK_CLIENT_SECRET`, `TIKTOK_REDIRECT_URI`, `TIKTOK_SCOPES`. Register the redirect URI on developers.tiktok.com (Login Kit, localhost/127.0.0.1 with port).

- **Pre-STT copyright risk check (2026-09-14)**:
  - **Scope**: Studio checkbox `Kiểm tra bản quyền trước khi dịch` (default on), after trim / before STT.
  - **Signals (no LLM)**: YouTube `licensedContent`, Bilibili `copyright`/tname via view API, film/TV title+duration heuristics, Chromaprint/AcoustID when `fpcalc` + `ACOUSTID_API_KEY` are present.
  - **Levels**: red pauses Auto as `copyright_hold` until `POST /jobs/{id}/copyright-continue`; yellow warns and continues; green means no known match (not a legal clearance).
  - **Files**: `copyright_check.py`, INGEST step, job snapshot, Studio checkbox + hold banner.

- **Allow Bilibili (and other public hosts) resolved via DNS64/NAT64 (2026-09-14)**:
  - **Symptom**: `POST /import` HTTP 400 `Tên miền www.bilibili.com phân giải về địa chỉ nội bộ (64:ff9b::a434:13e) bị cấm truy cập.`
  - **Root cause**: SSRF treated `ip.is_reserved` as internal. NAT64 well-known prefix `64:ff9b::/96` sits in `::/8`, so Python marks it reserved even when it embeds a public IPv4 (here `164.52.1.62`).
  - **Fix**: Unwrap NAT64 / IPv4-mapped / 6to4 and SSRF-check the embedded IPv4. Public CDN still allowed; RFC1918, loopback, and link-local metadata stay blocked.

- **Record proper names from the Vietnamese translation in Auto Memory (2026-09-14)**:
  - **Symptom**: Glossary tab `AI Auto Terminology Memory (0)` after Translate, even though the segment editor showed names like `Lý Tiêu Dao`.
  - **Root cause**: Extractor only read source `text` (skipped `translated_text` when source existed). Latin heuristic was ASCII `[A-Z][a-z]+` and required 2 hits, so Vietnamese diacritics never matched. LLM parse was also too strict and failed silently.
  - **Fix**: Join source + translation into the extract blob. Unicode title-case runs (`Lý Tiêu Dao`, `Thanh Vân Thành`, `John Smith`) are saved even once. LLM accepts `{terms|entities|names}` and `name`/`translation` aliases. Persist rolls back on DB error so the job session stays usable. TranslateStage also extracts after translation.

- **Save AI Terminology Memory on the Studio Auto job path (2026-09-14)**:
  - **Root cause**: Auto uses `POST /jobs/{id}/start`, not TranslateStage. Entity extract never ran, so the UI stayed at (0).
  - **Fix**: After STT/translate, `extract_and_persist_from_segments` writes `project_terminology_memory`. Glossary panel opens and refetches on job progress.

- **Auto-trim intro/outro filler before STT (2026-09-14)**:
  - **Problem**: Videos with ~7 min of content plus ~7 min of endcards/ads still went through STT/TTS/render for the whole file.
  - **Behavior**: Optional Studio checkbox `Tự cắt intro/outro thừa` (default on, same pattern as Auto-Confirm Translation). After audio extract, scan the full timeline (silence + freeze on head/tail) and optionally confirm edges with Gemini. `ffmpeg -ss/-t -c copy` writes `content_trimmed.mp4`, original file is kept.
  - **Safety**: Only head and tail; refuse if keep-window &lt; 40% or &lt; 60s; 20s dead-zone required.

- **Refresh Windows Search/Start shortcut icon (2026-09-14)**:
  - **Symptom**: Search still showed the old hoodie wolf after the T-wolf logo landed.
  - **Root cause**: Start Menu uses `AutoTransAI Studio.lnk` + Windows icon cache, not the in-app PNG.
  - **Fix**: `update_app_icon.ps1` rewrites the project/Start Menu shortcuts to `app-logo.ico` and runs on launch.

- **Fix desktop app not opening after a fake ICO (2026-09-14)**:
  - **Symptom**: Double-clicking AutoTransAi did nothing. `pythonw.exe` hid the error.
  - **Root cause**: `frontend/public/app-logo.ico` was a 1254×1254 PNG saved with a `.ico` name. `webview.start(icon=...)` on Windows needs a real ICO container (typically ≤256px).
  - **Fix**: Rebuild a 6-size Windows ICO. Launcher still opens the window if the icon file is invalid.

- **Remaster frontend visual system across all pages (2026-09-14)**:
  - **Scope**: Visual/layout only. 6-stage Studio flow, APIs, and pipeline unchanged.
  - **Design system**: New tokens, Plus Jakarta Sans, glass navbar pills, cards, buttons, tabs, forms, modals, hover/press motion in [App.css](frontend/src/App.css).
  - **Layout**: Studio header + segmented URL/upload; Dashboard project cards; Merger 2-column dropzone; Settings/ProjectDetail pill tabs.
  - **Nav labels**: Studio, Ghép Video, Dự án, Cài đặt.

- **Persist AI Terminology Memory and allow library thumbnails (2026-09-14)**:
  - **Terminology**: TRANSLATE `extract_entities` was a stub (`return True`) so Auto Memory stayed at 0. Extract repeated CJK/Latin names, optionally enrich via LLM, and upsert `project_terminology_memory`. UI refetches when job status changes.
  - **Thumbnails**: New source `library` uses images in `storage/projects/{id}/default_thumbnails`. Upload/list/delete via `/api/thumbnails/library/{project_id}`. Produce copies the selected file instead of generating (saves tokens).

- **Auto-generate thumbnail after Produce; enlarge YouTube publish modal (2026-09-14)**:
  - **Issue**: Checking “Tự Động Tạo Thumbnail AI” did not create an image; publish popup was 640px with no video/thumb preview.
  - **Pipeline**: PRODUCE now runs `generate_ai_thumbnail` after `final_video_qc` when `thumbnail_enabled` is on. Settings are sent on workflow start. PUBLISH reuses that URL.
  - **UI**: YouTube modal is full-width with current top/bottom 1.5rem gap; left pane previews dubbed video + AI thumbnail, right pane keeps SEO/upload fields.

- **Do not kill in-progress video downloads on a 5-minute wall clock (2026-09-14)**:
  - **Symptom**: `Hết thời gian tải video.` while the transfer bar was still running; no Job ID yet.
  - **Root cause**: `VIDEO_DOWNLOAD_TIMEOUT` defaulted to 300s and `asyncio.wait_for` / HTTP deadline aborted a slow but live download.
  - **Fix**: timeout `0` = unlimited. Native HTTP uses no read timeout; yt-dlp is not wrapped in `wait_for` when unlimited. Stall/resume still retries dropped connections.

- **Download Bilibili via official playurl MP4 with Range resume (2026-09-14)**:
  - **Symptom**: Transfer still failed with "Mạng cắt file giữa chừng" but the UI showed the Extracting URL preamble instead of `509 bytes read, 18052770 more expected`.
  - **Root cause**: yt-dlp DASH still truncated; error mapper used `err_text[:180]` (start of log). Official `x/player/playurl?fnval=1` returns a single MP4 that accepts HTTP 206 Range (verified 8KB + Content-Range 0-8191/37089181).
  - **Fix**: Prefer native playurl + `download_http_with_resume`; keep yt-dlp as fallback. Snippet now uses the `bytes read` line. Tests cover snippet, playurl durl parse, and pagelist `cid`.

- **Fix Windows NotImplementedError on URL ingest (2026-09-14)**:
  - **Root cause**: `run_yt_dlp_with_progress_async` used `asyncio.create_subprocess_exec`, which raises `NotImplementedError` on Windows uvicorn SelectorEventLoop. Transfer failed before a Job ID existed.
  - **Fix**: Spawn yt-dlp with `subprocess.Popen` + `asyncio.to_thread` (same pattern as FFmpeg progress). Tests assert no `asyncio.create_subprocess_exec` and parse a progress line from Popen stdout.

- **Show ingest transfer progress and harden Bilibili download (2026-09-14)**:
  - **Symptoms**: Pipeline stuck at INGEST 0% with no Job ID; yt-dlp `509 bytes read, 18052770 more expected` after 10 retries.
  - **Root cause**: `POST /import` blocked until yt-dlp finished (no progress). Default 10 retries + concurrent fragments + caching tiny leftover files.
  - **Backend**: yt-dlp now uses `-c --retries 30 -N 1 --newline`, streams progress, maps truncated CDN reads, rejects cache files &lt; 100KB. New `POST/GET /api/video-translator/transfers` for pollable download percent/bytes/speed.
  - **Frontend**: Transfer bar on WorkflowTimeline; axios `onUploadProgress` for video import, watermark logo, and Video Merger uploads.
  - **Tests**: progress line parse, retries/`-N 1` in command, truncated-download Vietnamese error.

- **Fix Bilibili check-url duration 00:00 (2026-09-14)**:
  - **Root cause**: `GET metadata` for `https://www.bilibili.com/video/BV1dRMP68Ehp?t=40.9` fell back to dummy `{title: "Video từ Bilibili", duration: 0}` when yt-dlp was missing or failed. Query `t` is a timestamp, not a part index. Bilibili `view` API is often HTTP 412; `x/player/pagelist` returns real part duration (P1 = 893s).
  - **Backend**: Parse BVID/`p`, map pagelist JSON, and prefer pagelist before yt-dlp in [page_url_adapter.py](backend/app/services/video_source/page_url_adapter.py). Do not return fake 0 duration as valid Bilibili metadata.
  - **Tests**: `test_parse_bilibili_video_ref_ignores_timestamp_query`, `test_bilibili_pagelist_maps_part_duration`. Live pagelist fetch: title `宠物心声诊所 1`, duration `893`.

- **Fix Bilibili URL ingest HTTP 400 empty error (2026-09-14)**:
  - **Root cause**: `POST /api/video-translator/import` for `https://www.bilibili.com/video/BV1dRMP68Ehp?t=40.9` failed at INGEST. Bilibili was not in `PAGE_DOMAINS` (display `Www.bilibili.com`), yt-dlp used `b[ext=mp4]/best[ext=mp4]/best` (incompatible with Bilibili DASH), subprocess `check=True` raised `CalledProcessError` without stderr, and the pipeline banner truncated `❌ ...` to `×`.
  - **Backend**: Added Bilibili hosts, browser UA/referer, `bv*+ba` merge-to-mp4, `check=False`, and human-readable 412 mapping in [page_url_adapter.py](backend/app/services/video_source/page_url_adapter.py). Import 400 now always includes a non-empty `detail` in [video_translator.py](backend/app/api/routes/video_translator.py).
  - **Frontend**: Let the browser set FormData multipart boundary in [api.js](frontend/src/api.js); wrap full error text in [WorkflowTimeline.jsx](frontend/src/components/WorkflowTimeline.jsx).
  - **Tests**: `test_adapter_can_handle_bilibili_url`, `test_bilibili_domain_display_name`, `test_yt_dlp_download_cmd_for_bilibili_uses_browser_headers`, `test_yt_dlp_412_error_is_human_readable`.

- **Implement Standalone Video Merger Feature (2026-09-12)**:
  - **Feature Architecture**: Added independent **Video Merger** feature, completely decoupled from the Video Translation workflow (`VideoTranslator.jsx`). Route `?page=merger` (`/video-merger`) accessed via top-level `Navbar.jsx` menu item `🎬 Ghép Video`.
  - **Database Persistence**: Added ORM models `VideoMergeJob` (`video_merge_jobs`) and `VideoMergeAsset` (`video_merge_assets`) in [video_merger.py](file:///c:/Hack/AutoTransAI/backend/app/models/video_merger.py) and exported them in [__init__.py](file:///c:/Hack/AutoTransAI/backend/app/models/__init__.py).
  - **Resilient FFmpeg Engine**: Created `VideoMergerService` in [merger_service.py](file:///c:/Hack/AutoTransAI/backend/app/services/video_merger/merger_service.py):
    - Preflight media inspection (file existence, readability, resolution, FPS, video/audio stream verification via FFprobe).
    - Fast Concat copy (`-c copy`) for identical video specs.
    - Complex Filter Normalization (`-filter_complex`) for mixed resolutions, varying FPS, or silent videos (scaling with aspect ratio preservation, black letterboxing, FPS 30 normalization, and silent audio generation via `anullsrc=r=44100:cl=stereo:d={duration}`).
    - Real-time streaming progress tracking via `run_ffmpeg_with_progress_async`.
  - **Backend API Router**: Implemented [video_merger.py](file:///c:/Hack/AutoTransAI/backend/app/api/routes/video_merger.py) (`/api/video-merger/upload`, `/assets`, `/jobs`, `/jobs/{id}/start`, `/jobs/{id}`, `/jobs/{id}/retry`, `/jobs/{id}`) and mounted router in [main.py](file:///c:/Hack/AutoTransAI/backend/app/main.py).
  - **Frontend UI & Page**: Created standalone [VideoMerger.jsx](file:///c:/Hack/AutoTransAI/frontend/src/pages/VideoMerger.jsx) with upload dropzone, system asset picker modal, drag & drop / button reordering, live summary stats, double-click guard action button, progress bar (0-100%), HTML5 output player, download button, and optional YouTube publish modal trigger. Updated [Navbar.jsx](file:///c:/Hack/AutoTransAI/frontend/src/components/Navbar.jsx), [App.jsx](file:///c:/Hack/AutoTransAI/frontend/src/App.jsx), [api.js](file:///c:/Hack/AutoTransAI/frontend/src/api.js), and [App.css](file:///c:/Hack/AutoTransAI/frontend/src/App.css).
  - **Storage & Download Enhancements**: Updated `download_file` and `get_storage_file` in [storage.py](file:///c:/Hack/AutoTransAI/backend/app/api/routes/storage.py) to seamlessly resolve both absolute disk paths and relative URL prefixes (`api/storage/files/`, `storage/`). Updated [VideoMerger.jsx](file:///c:/Hack/AutoTransAI/frontend/src/pages/VideoMerger.jsx) to use `handleDownloadOutput()` triggering reliable force attachment download.
  - **YouTube Publisher Compatibility**: Enhanced `publish_youtube_endpoint`, `get_initial_youtube_metadata_endpoint`, and `generate_youtube_seo_endpoint` in [video_editor.py](file:///c:/Hack/AutoTransAI/backend/app/api/routes/video_editor.py) to support both `VideoTranslationJob` and `VideoMergeJob` output targets cleanly.
  - **Verification**: Verified clean end-to-end FFmpeg merge normalization on synthetic test videos (1280x720 30fps + 1920x1080 24fps silent video merged cleanly to 5s 1920x1080 30fps video), 100% clean Vite build (`npm run build`), and 100% passing backend pytest suite.

- **Add Strict Prohibition of Autonomous Project Deletion Mandate (2026-09-12)**:
  - **Mandatory Agent Rules Update**: Added `RULE 8: Strict Prohibition of Autonomous Project Deletion` to [AGENTS.md](file:///c:/Hack/AutoTransAI/AGENTS.md).
  - **Rule Mandate**: Prohibits any AI assistant or automated system from deleting project repositories, codebase directories, database records, or key source files on its own initiative without explicit user authorization.

- **Redesign YouTube / SEO Settings Architecture — Separate Default Template and AI Generator (2026-09-09)**:
  - **Single Source of Truth & Project Defaults**: Added `youtube_enabled`, `youtube_channel_name`, `youtube_title_template`, `youtube_description_default`, `youtube_default_tags`, `youtube_ai_seo_enabled`, `youtube_ai_allow_title`, `youtube_ai_allow_description`, `youtube_ai_allow_tags` to `DEFAULT_PROJECT_SETTINGS` and updated `normalize_project_settings` in [projects.py](file:///c:/Hack/AutoTransAI/backend/app/api/routes/projects.py).
  - **Tag Merging & Title Template Engine**:
    - Implemented `merge_youtube_tags(default_tags, ai_tags)` in [youtube_service.py](file:///c:/Hack/AutoTransAI/backend/app/services/video_editor/youtube_service.py) with case-insensitive duplicate detection (`#AI` vs `#ai`), order preservation (defaults first), and whitespace/comma normalization.
    - Implemented `render_title_template` with variable substitution (`{episode}`, `{project_name}`, `{channel_name}`, `{video_name}`) and episode zero-padding (e.g. `01`, `02`).
    - Implemented `calculate_project_video_episode(session, project_id, job_id)` to resolve 1-indexed video sequence order based on `created_at` timestamp without database ID coupling.
  - **AI SEO Generator Integration**: Refactored `generate_youtube_seo_metadata` in [youtube_service.py](file:///c:/Hack/AutoTransAI/backend/app/services/video_editor/youtube_service.py) so Gemini AI generates only supplementary SEO content while Python code enforces default template, description, and tag precedence.
  - **Backend API Endpoints**: Added `GET /api/video-editor/jobs/{job_id}/initial-youtube-metadata` and updated `generate_youtube_seo_endpoint` in [video_editor.py](file:///c:/Hack/AutoTransAI/backend/app/api/routes/video_editor.py).
  - **Frontend UI & Publisher Modal**:
    - Added **📺 YouTube & SEO Defaults** card in [ProjectDetail.jsx](file:///c:/Hack/AutoTransAI/frontend/src/pages/ProjectDetail.jsx) Settings tab with Channel Name, Title Template + live preview, Default Description, Default Tags, Enable Switch, and AI SEO Generator controls.
    - Updated [YouTubePublisherModal.jsx](file:///c:/Hack/AutoTransAI/frontend/src/components/YouTubePublisherModal.jsx) to fetch initial rendered defaults on mount and perform AI SEO generation without overwriting project default metadata.
    - Added `getInitialSEO` to `videoEditorApi` in [api.js](file:///c:/Hack/AutoTransAI/frontend/src/api.js).
  - **Verification**: Created test suite [test_youtube_seo_architecture.py](file:///c:/Hack/AutoTransAI/backend/tests/unit/test_youtube_seo_architecture.py) and verified 100% passing tests (12/12 passed in `pytest`).

- **Cleanup Job & Project ID Storage Folders (2026-09-09)**:
  - **Storage Maintenance**: Cleaned up 72 legacy test/execution job and project directories across `storage/projects`, `backend/storage/projects`, `backend/storage/translator/jobs`, and `data/translator/jobs`.
  - **Preserved Asset Directory**: Preserved active project folder `backend/storage/projects/aa03da8e` as requested.

- **Add Project Title Editing & Persisted Synchronization (2026-09-09)**:
  - **Backend API Endpoints**: Implemented `PATCH /api/projects/{project_id}` and `PUT /api/projects/{project_id}` (`update_project`) in [projects.py](file:///c:/Hack/AutoTransAI/backend/app/api/routes/projects.py) and added `ProjectUpdate` schema (`title`, `description`) in [project.py](file:///c:/Hack/AutoTransAI/backend/app/schemas/project.py). The endpoint updates both `Project.title` and associated `VideoAsset.title` records in SQLite DB.
  - **Frontend API Integration**: Added `update: (id, data) => api.patch('/projects/' + id, data).then(...)` to `projectsApi` in [api.js](file:///c:/Hack/AutoTransAI/frontend/src/api.js).
  - **Frontend Studio UI & Management Views**:
    - [VideoTranslator.jsx](file:///c:/Hack/AutoTransAI/frontend/src/pages/VideoTranslator.jsx): Added "✏️ Sửa tên" button in header project dropdown and `showEditTitleModal` overlay modal with backend API sync.
    - [ProjectDetail.jsx](file:///c:/Hack/AutoTransAI/frontend/src/pages/ProjectDetail.jsx): Added inline header title editing and `handleSaveTitle` handler with backend API sync.
    - [Dashboard.jsx](file:///c:/Hack/AutoTransAI/frontend/src/pages/Dashboard.jsx): Added project action table button and `editModal` overlay modal with backend API sync.
  - **Rule Compliance**: Enforced strict prohibition of automatic project deletion across the entire codebase.
  - **Verification**: Verified clean frontend build (`npm run build` succeeded with 0 errors) and 100% passing backend tests (`pytest`).

- **Fix Backend Auto-Confirm Execution & Non-Blocking Hand-off to Phase 2 Render (2026-09-09)**:
  - **Recursive Lock Deadlock Fix**: Resolved issue where `run_pipeline()` held `get_job_lock(job_id)` while calling `execute_job_render_pipeline(job_id)`, causing Phase 2 to immediately return due to `lock.locked()`. Refactored `run_pipeline` to release job lock prior to scheduling Phase 2 render and implemented `_active_render_jobs` set tracking in `execute_job_render_pipeline`.
  - **Idempotent Auto-Confirm Helper**: Added `auto_confirm_and_start_render_if_needed(job_id)` in [video_translator.py](file:///c:/Hack/AutoTransAI/backend/app/api/routes/video_translator.py) which marks segments as `confirmed`, transitions job status to `GENERATING_TTS` (`DUB`), and launches Phase 2 rendering. Hooked helper into `GET /jobs/{job_id}`, `GET /projects/{project_id}/workflow-status`, `resume_workflow_api`, and `check_and_mark_stalled_jobs`.
  - **State Machine Normalization**:
    - **Auto-Confirm ON**: `TRANSLATE (RUNNING)` → `TRANSLATE (COMPLETED)` → `AUTO CONFIRMING` → `DUB (GENERATING_TTS)`.
    - **Auto-Confirm OFF**: `TRANSLATE (RUNNING)` → `TRANSLATE (COMPLETED)` → `WAITING FOR USER CONFIRMATION (segment_editing)` (no heartbeat timeout).
  - **Integration Test Suite**: Expanded [test_auto_confirm_and_stage_sync.py](file:///c:/Hack/AutoTransAI/backend/tests/integration/test_auto_confirm_and_stage_sync.py) to cover segment confirmation, auto-confirm helper execution, and idempotency (100% passed). Verified clean frontend build (`npm run build`).

- **Fix Unified 6-Stage Workflow Lifecycle, Stage State Machine & Auto-Confirm Synchronization (2026-09-09)**:
  - **Auto-Confirm Worker Heartbeat Persistence**: Resolved `STALLED` job timeout errors during Phase 2 rendering by maintaining active background heartbeat loop (`start_job_heartbeat`) during `execute_job_render_pipeline`, preventing `check_and_mark_stalled_jobs` from falsely marking active jobs as failed after 60s.
  - **Backend Stage Status Single Source of Truth**: Updated `get_workflow_status_api` in [video_translator.py](file:///c:/Hack/AutoTransAI/backend/app/api/routes/video_translator.py) to dynamically derive real-time lifecycle stages (`INGEST` → `ANALYZE` → `TRANSLATE` → `DUB` → `PRODUCE` → `PUBLISH`) and stage status from `VideoTranslationJob`.
  - **Frontend Stage Normalization**: Refactored [WorkflowTimeline.jsx](file:///c:/Hack/AutoTransAI/frontend/src/components/WorkflowTimeline.jsx) stage status mapping using `STAGE_ORDER_MAP`, ensuring stage cards update accurately (`Passed`, `Running`, `Needs Review`, `Waiting`) without UI freezing at `INGEST`.
  - **Auto-Confirm Translation Flow**: Fixed workflow execution when `auto_confirm_translation = True` so completed translated text automatically transitions to `DUB` (`GENERATING_TTS`), bypassing manual prompt while preserving manual confirmation UI when `auto_confirm_translation = False`.
  - **Integration Verification**: Added comprehensive test suite [test_auto_confirm_and_stage_sync.py](file:///c:/Hack/AutoTransAI/backend/tests/integration/test_auto_confirm_and_stage_sync.py) verifying both Auto-Confirm ON/OFF transitions and 6-stage backend status synchronization (100% passed). Verified clean frontend build (`npm run build`).

- **Rebuild Video Translator (Unified Workflow) Studio UI & Viewport Optimization (2026-09-09)**:
  - **Unified 6-Stage Workflow Pipeline Integration**: Consolidated the standalone `📊 Tiến Trình Xử Lý Pipeline` card directly inside [WorkflowTimeline.jsx](file:///c:/Hack/AutoTransAI/frontend/src/components/WorkflowTimeline.jsx). Added Job ID, overall progress %, stage progress %, Heartbeat status, FFmpeg process stats, STT/Translation/TTS status, segment counts, debug telemetry toggle, and compact inline error alert.
  - **2-Column Responsive Studio Layout**: Restructured [VideoTranslator.jsx](file:///c:/Hack/AutoTransAI/frontend/src/pages/VideoTranslator.jsx) into a 2-column Studio Grid (`.translator-studio-grid` in [App.css](file:///c:/Hack/AutoTransAI/frontend/src/App.css)). Primary column holds the Integrated Unified Pipeline and compact Video Input & Translation/Dubbing config card. Auxiliary column holds Watermark (Logo/Text) and AI Auto Thumbnail controls built with progressive disclosure.
  - **100% Single-Viewport Containment**: Set `ProjectGlossaryManager` to default collapsed state below the main grid, enabling standard desktop viewports (1366x768, 1440x900, 1920x1080) to view all core workflow controls without vertical scrolling.
  - **Compact Error Handling**: Integrated `❌ Xử Lý Thất Bại` directly inside the Pipeline card footer with working "Xem Log" and "Smart Retry" actions without layout shifting.
  - **Verification & Compatibility**: Verified 100% clean build via `npm run build` (0 JSX errors) and preserved all backend API contracts, polling, SSE, and DB persistence.

- **Fix `TypeError: render_dubbed_video() got an unexpected keyword argument 'output_path'` (2026-09-08)**:
  - **Parameter Signature Alignment**: Updated invocation of `render_dubbed_video` in [video_translator.py](file:///c:/Hack/AutoTransAI/backend/app/api/routes/video_translator.py#L1556) to match the parameter names expected by `translator_service.py` (`original_audio_mode`, `output_video_path`, `work_dir=job_dir`).
  - **Execution Verification**: Verified via `scratch/test_render_dubbed_video_call.py` targeting Job `92ccc5b3` that TTS synthesis, time-stretching, and video multiplexing rendering proceed cleanly without signature exceptions.

- **Fix Workflow Resume Execution & Context Synchronization (2026-09-08)**:
  - **Failed Stage Checkpoint Reset**: Updated `resume_workflow` in [workflow_engine.py](file:///c:/Hack/AutoTransAI/backend/app/workflow/workflow_engine.py#L148) to reset any `FAILED` stages or steps back to `PENDING` so the execution loop re-runs incomplete/failed steps instead of skipping them.
  - **Workflow Context Auto-Hydration**: Added automatic video source DB resolution at the start of `_run_workflow_loop` in [workflow_engine.py](file:///c:/Hack/AutoTransAI/backend/app/workflow/workflow_engine.py#L275) and persisted updated `WorkflowContext` to `wf_exec.context_data` after every successful step completion.
  - **Translation Job Resume Integration**: Enhanced `resume_workflow_api` in [video_translator.py](file:///c:/Hack/AutoTransAI/backend/app/api/routes/video_translator.py#L2037) to accept `BackgroundTasks` and automatically resume/restart any associated `VideoTranslationJob` in `FAILED`, `CREATED`, or `SEGMENT_EDITING` state.
  - **Execution Verification**: Verified via `scratch/test_resume_workflow.py` that resuming project `fe2777b1` successfully sets engine status to `running`, clears error flags, and resumes step execution cleanly with HTTP 200 OK.

- **Fix `Video file not found for project {project_id}: None` & Ingest Stage Execution (2026-09-08)**:
  - **Database Asset Auto-Resolution**: Added `_resolve_video_from_db` to `IngestStage` in [ingest_stage.py](file:///c:/Hack/AutoTransAI/backend/app/workflow/stages/ingest_stage.py#L49) and updated `start_workflow_api` in [video_translator.py](file:///c:/Hack/AutoTransAI/backend/app/api/routes/video_translator.py#L2007). When `ctx.video_path` or `ctx.video_url` is missing from project settings snapshot, the pipeline auto-resolves the source video file from associated `VideoTranslationJob` & `VideoAsset` records or `Project.media_url` in DB.
  - **Correct Active Imports & Path Robustness**: Replaced missing legacy functions with active services: `get_video_metadata_async` from `app.media.ffprobe` (with robust `Path` type normalization), `extract_audio_from_video` from `app.services.video_translator.translator_service`, `upload_file_to_r2` alias in `app.services.storage_service`, and `get_video_source_service` for video downloading.
  - **Execution Verification**: Verified that retrying or starting stage INGEST for project `fe2777b1` resolves asset `c436d70a` (`C:\Hack\AutoTransAI\data\translator\assets\c436d70a\input_source.mp4`), successfully executing all 5 steps (`import_video`, `validate_video`, `probe_video`, `store_asset`, `extract_audio`) and launching STT transcription seamlessly.

- **Fix `ValueError: No workflow execution found for project` in `POST /.../workflow/stage/{stage}/retry` (2026-09-08)**:
  - **Auto-Recovery Execution**: Updated `retry_stage` and `resume_workflow` in [workflow_engine.py](file:///c:/Hack/AutoTransAI/backend/app/workflow/workflow_engine.py#L137) to auto-initialize a new `WorkflowExecution` record for the project instead of throwing a raw `ValueError` HTTP 500 error when retrying or resuming a project without a pre-existing execution.
  - **Stage Override Context**: Enabled `start_workflow` in [workflow_engine.py](file:///c:/Hack/AutoTransAI/backend/app/workflow/workflow_engine.py#L69) to respect `initial_stage` context parameter when initializing auto-recovered executions.
  - **Endpoint Verification**: Verified that `POST /api/video-translator/projects/fe2777b1/workflow/stage/INGEST/retry` auto-creates execution record and returns `STATUS 200 OK` with `current_stage: INGEST`.

- **Fix `NameError: name 'job_id' is not defined` in `POST /api/video-translator/jobs` (2026-09-08)**:
  - **Variable Initialization Fix**: Defined `job_id = str(uuid.uuid4())[:8]` in `create_translation_job` in [video_translator.py](file:///c:/Hack/AutoTransAI/backend/app/api/routes/video_translator.py#L405) prior to initializing `VideoTranslationJob`.
  - **Endpoint Verification**: Verified that `POST /api/video-translator/jobs` responds cleanly with HTTP 200 OK and valid job object payload.

- **Automated Translation Text Confirmation on Workflow Execution (2026-09-08)**:
  - **Automated Phase 1 -> Phase 2 Transition**: Refactored rendering execution (`execute_job_render_pipeline`) in [video_translator.py](file:///c:/Hack/AutoTransAI/backend/app/api/routes/video_translator.py). When executing "Start Workflow" (or starting translation pipeline), Phase 1 (Speech-to-Text & Translation) automatically confirms translated segments and seamlessly transitions straight into Phase 2 (TTS Dubbing → Audio Sync → FFmpeg Render Video) without pausing at `SEGMENT_EDITING`.
  - **`auto_confirm_translation` Setting Integration**: Added `auto_confirm_translation: True` default setting to `DEFAULT_PROJECT_SETTINGS` in [projects.py](file:///c:/Hack/AutoTransAI/backend/app/api/routes/projects.py), `VideoTranslationJob` ORM model in [video_translator.py](file:///c:/Hack/AutoTransAI/backend/app/models/video_translator.py), and request models (`CreateJobRequest`, `StartWorkflowRequest`).
  - **Frontend Control Toggle**: Added a project setting UI toggle (`⚡ Tự Động Xác Nhận Văn Bản Dịch & Render Lồng Tiếng`) in [VideoTranslator.jsx](file:///c:/Hack/AutoTransAI/frontend/src/pages/VideoTranslator.jsx), allowing users to switch between fully automated execution (default) and manual segment review before rendering.

- **Global AI Function Config Single Source of Truth & Project Settings UI Cleanup (2026-09-08)**:
  - **Removed Per-Project Model Override Card**: Removed redundant `🤖 AI Providers & Models` card from Project Settings (`ProjectDetail.jsx`), enforcing 100% single-source-of-truth model resolution via **AI Function Configuration & Routing** (`Settings Studio & AI Management`).
  - **Balanced Responsive Grid Layout**: Re-aligned Project Settings cards into a clean, symmetric 2x2 grid (`repeat(auto-fit, minmax(340px, 1fr))`) covering `Ngôn ngữ & Video Input`, `Voice & Dubbing`, `Watermark / Logo Configuration`, and `AI Thumbnail Configuration`.
  - **Backend Pipeline Resolution Verification**: Verified that STT, Translation, TTS, Image, and Video AI services exclusively resolve models via `AIModelResolver` against the database (`ai_function_configs` -> `ai_models`), eliminating configuration drift.

- **Fix `project_id` Invalid Keyword Argument for `YouTubePublication` (2026-09-08)**:
  - **ORM Model Schema Fix**: Added `project_id` column (`Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)`) to `YouTubePublication` model in [video_editor.py](file:///c:/Hack/AutoTransAI/backend/app/models/video_editor.py#L132-L140).
  - **Automated Schema Auto-Migration**: Allowed `_sync_schema_sync` in `database.py` to auto-issue `ALTER TABLE youtube_publications ADD COLUMN project_id` on app startup across SQLite and MySQL.
  - **Router & Pipeline Integration**: Passed both `job_id` and `project_id` when instantiating `YouTubePublication` in [video_editor.py](file:///c:/Hack/AutoTransAI/backend/app/api/routes/video_editor.py#L240-L250), [publish_stage.py](file:///c:/Hack/AutoTransAI/backend/app/workflow/stages/publish_stage.py#L134-L145), and [youtube.py](file:///c:/Hack/AutoTransAI/backend/app/api/routers/youtube.py#L207-L218).

- **PKCE Code Verifier Persistence for Google OAuth (2026-09-08)**:
  - **PKCE State Tracking**: Added `_oauth_verifiers` dictionary mapping `state` to `flow.code_verifier` in [youtube.py](file:///c:/Hack/AutoTransAI/backend/app/api/routers/youtube.py#L65-L105).
  - **Fixed `(invalid_grant) Missing code verifier` Exception**: Preserved the generated PKCE verifier across initial authorization URL generation (`get_auth_url`) and callback token exchange (`oauth_callback`), ensuring 100% successful Google OAuth token exchange.

- **Allow Local HTTP Transport for OAuth Callback (2026-09-08)**:
  - **Insecure Transport Fix**: Set `os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'` at module load time in [youtube.py](file:///c:/Hack/AutoTransAI/backend/app/api/routers/youtube.py#L1-L15).
  - **Fixed `(insecure_transport) OAuth 2 MUST utilize https` Error**: Allowed local development callbacks (`http://localhost:8000/...` & `http://127.0.0.1:8000/...`) to execute token exchange without requiring HTTPS certificates on localhost.

- **Pydantic Settings Model Fix for YouTube OAuth (2026-09-08)**:
  - **Added Missing Fields**: Added `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`, and `ENCRYPTION_KEY` fields to the `Settings` class in [app/config.py](file:///c:/Hack/AutoTransAI/backend/app/config.py#L95-L100).
  - **Fixed `AttributeError`**: Resolved `AttributeError: 'Settings' object has no attribute 'YOUTUBE_CLIENT_ID'` exception when calling `GET /api/youtube/auth-url`.
  - **Dynamic Config Loading**: Updated `_get_client_config()` in [youtube.py](file:///c:/Hack/AutoTransAI/backend/app/api/routers/youtube.py#L37-L50) to dynamically query `get_settings()`, returning valid Google OAuth 2.0 URLs.

- **Real-Time YouTube Upload Progress Bar & Polling Integration (2026-09-08)**:
  - **Backend Chunk Progress Updates**: Enhanced `YouTubePublishingService.execute_async_upload()` in [youtube_service.py](file:///c:/Hack/AutoTransAI/backend/app/services/video_editor/youtube_service.py#L225-L255) to track chunk upload progress via `status.progress()`, writing real-time upload percentage (`0%` -> `100%`) directly into `pub.progress` in database.
  - **Async Task Trigger & Polling Endpoint**: Updated `publish_youtube_endpoint` in [video_editor.py](file:///c:/Hack/AutoTransAI/backend/app/api/routes/video_editor.py#L201-L245) to create a `YouTubePublication` record and launch background upload tasks. Added `getUploadStatus` in [api.js](file:///c:/Hack/AutoTransAI/frontend/src/api.js) targeting `GET /api/youtube/upload/{id}/status`.
  - **Animated UI Progress Bar**: Designed animated glowing progress bar component in [YouTubePublisherModal.jsx](file:///c:/Hack/AutoTransAI/frontend/src/components/YouTubePublisherModal.jsx#L205-L225) with dynamic width fill (`0-100%`), percent text readout (`⏳ Đang tải video lên YouTube... 45%`), and auto-transition to success view upon 100% completion.

- **YouTube Real OAuth Upload Endpoint Integration (2026-09-08)**:
  - **Eliminated Fake Mock Link Fallback**: Updated `publish_youtube_endpoint` in [video_editor.py](file:///c:/Hack/AutoTransAI/backend/app/api/routes/video_editor.py#L201-L245) to query the active connected `YouTubeChannel` from Database and decrypt its `credentials_json` using `decrypt_data(...)`.
  - **Real Resumable YouTube API Upload**: Connected decrypted Google OAuth tokens to `YouTubePublishingService.upload_to_youtube(...)` to perform authentic resumable video uploads via `googleapiclient.discovery.build("youtube", "v3", credentials=creds)` returning authentic YouTube video URLs (`https://www.youtube.com/watch?v=REAL_ID`).
  - **Missing OAuth Connection Guard**: If no active YouTube channel is linked in DB, `publish_youtube_endpoint` returns a clear HTTP 400 error message instructing the user to navigate to Settings -> Social Accounts to connect their Google YouTube account first.
  - **Social Accounts UI & API Integration**: Added `youtubeApi` client methods in [api.js](file:///c:/Hack/AutoTransAI/frontend/src/api.js) and updated [Settings.jsx](file:///c:/Hack/AutoTransAI/frontend/src/pages/Settings.jsx) with a direct `🔴 Kết Nối YouTube (Google OAuth 2.0)` button triggering the Google OAuth consent flow (`GET /api/youtube/auth-url`).

- **Unsaved Data Protection & Modal Exit Confirmation (2026-09-08)**:
  - **YouTube Publisher Modal Safe Close**: Added `handleSafeClose` in [YouTubePublisherModal.jsx](file:///c:/Hack/AutoTransAI/frontend/src/components/YouTubePublisherModal.jsx) to intercept backdrop clicks, header close ("&times;"), and "Hủy" button events, showing a confirmation prompt (`window.confirm`) whenever unsaved title, description, or tags exist.
  - **Create Project Modal Exit Protection**: Added `closeCreateProjectModalSafely` in [VideoTranslator.jsx](file:///c:/Hack/AutoTransAI/frontend/src/pages/VideoTranslator.jsx) to guard project title and description inputs against accidental backdrop or cancel clicks.
  - **Settings Modals Exit Guard**: Added safe close handlers (`closeAddKeyModalSafely`, `closeAddProviderModalSafely`, `closeAddModelModalSafely`, `closeAddSocialModalSafely`) in [Settings.jsx](file:///c:/Hack/AutoTransAI/frontend/src/pages/Settings.jsx) for API keys, custom providers, models, and social accounts modals.
  - **Browser Tab Unload Guard**: Integrated `beforeunload` event listeners across [VideoTranslator.jsx](file:///c:/Hack/AutoTransAI/frontend/src/pages/VideoTranslator.jsx) and [Settings.jsx](file:///c:/Hack/AutoTransAI/frontend/src/pages/Settings.jsx) to alert users if they attempt to refresh or navigate away while mid-entry.

- **YouTube OAuth 2.0 & Async Resumable Upload Pipeline (2026-09-08)**:
  - **Encrypted OAuth Credentials**: Integrated `cryptography.fernet` to securely encrypt and decrypt Google OAuth refresh tokens within the `YouTubeChannel` database model, eliminating hardcoded API keys.
  - **YouTube Resumable Upload Background Tasks**: Developed `execute_async_upload` within `YouTubePublishingService` to support chunked, resumable uploads directly to YouTube Data API v3 while running in an `asyncio.to_thread` background task.
  - **Database Progress Tracking**: Expanded `YouTubePublication` ORM model to track real-time upload progress percentage (`progress` column) and states (`pending`, `uploading`, `success`, `failed`). Created an Alembic migration (`20260908_youtube_progress`) for the schema change.
  - **OAuth & Upload APIs**: Created new REST API router (`/api/youtube`) to manage the Google Auth Flow (`/auth-url`, `/oauth-callback`), channel list, account disconnection, and asynchronous upload triggering and polling (`/upload`, `/upload/{id}/status`).
  - **Publish Stage Integration**: Integrated the new async upload workflow seamlessly into the `publish_stage.py` pipeline step, handling Google credential decryption and automatic auto-refresh logic natively via `google-auth-oauthlib` and `google-api-python-client`.

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
# Character Voice Mapping and Timeline Scheduling (2026-09-16)
- Added persistent `CharacterVoiceProfile` and provider-neutral `VoicePoolEntry`; extended existing `SpeakerVoiceMapping` without removing legacy API fields.
- Preserved STT speaker metadata and immutable source timeline fields on translation segments.
- Added whole-transcript conservative Character Mapping, project profile reuse, voice conflict validation, and a `needs_review` gate that also applies when translation auto-confirm is enabled.
- Added per-segment TTS provider/voice selection, FFprobe-measured TTS duration, bounded overlap-aware scheduling, same-voice serialization, supporting-character ducking, and PCM same-voice overlap rejection.
- Added Character/Voice review, validation, confirm/resume, profile, and voice-pool APIs plus Studio review fields and controls.
- Added Alembic revision `20260916_character_voice_timeline` and focused schema/STT/mapping/assignment/scheduler/backward-compatibility tests.
- Verification: 30 focused backend tests passed; legacy `/voice-map` real-SQLite integration test passed; frontend production build passed. Full backend suite: 262 passed, 7 skipped, 1 pre-existing preflight seed failure (`AI_MODEL_NOT_FOUND`). The historical clean Alembic chain also fails before the new revision because the initial migration lacks `video_translation_jobs` expected by `20260822_sync_schema`. A real three-speaker video mux could not run in this Linux environment because the `ffmpeg` executable is absent; scheduler and PCM behavior remain covered by generated-WAV/unit tests.

# Stability, Security & Consistency Overhaul (2026-09-18)
- **Security & Database Foundation**:
  - Removed hardcoded MySQL password from `config.py`.
  - Fixed critical path traversal vulnerability in `security.py` and `storage.py` by implementing robust `Path.is_relative_to()` checks instead of raw string prefix matching.
  - Enforced SQLite `PRAGMA foreign_keys=ON` fallback on startup via SQLAlchemy connection events in `database.py`.
  - Added missing `ForeignKey` constraints to all SQLAlchemy models and applied manual Alembic migration (`20260918_add_foreign_keys.py`) to safely alter SQLite tables.
- **Memory & Storage Optimizations**:
  - Prevented Out-Of-Memory (OOM) crashes in `fal_provider.py` and `kling_provider.py` by implementing `httpx` chunked stream downloading (`aiter_bytes`) for large video files.
  - Eliminated disk leaks by ensuring standalone video merge job outputs are deleted when their `VideoMergeJob` row is deleted, and excluded active outputs from premature sweep by `cleanup_service.py`.
- **Backend Flow & API Stability**:
  - Corrected `preflight.py` to accurately report false on exceptions rather than returning false-positive success.
  - Removed dangerous `os.environ` mutation in `key_manager.py` and `youtube.py` request handlers to avoid cross-request contamination in the asynchronous FastAPI environment.
  - Removed test-specific hardcodes (such as the 0-byte file check bypass in `visual_gender_service.py` and mock YouTube upload IDs in `youtube_service.py`).
  - Implemented strict Pydantic payload validation (`ConfigureProjectRequest`) in `projects.py`.
  - Implemented missing `GET /api/video-translator/assets/{asset_id}` endpoint required by the frontend API client.
- **Startup Reconciliation Engine**:
  - Created `reconciliation.py` service to detect and gracefully fail zombie jobs left in `RUNNING` or `PROCESSING` states during ungraceful server shutdowns. This routine is now wired into the `main.py` application lifespan, preventing locked UI states.
- **Frontend & UX Improvements**:
  - Replaced hardcoded `http://127.0.0.1:8000` Server-Sent Events (SSE) URLs in `VideoTranslator.jsx` with standard relative `/` paths, fixing connections in remote or reverse-proxy deployments.
  - Updated `model_resolver.py` to dynamically query `AIModel` via database lookup instead of relying on rudimentary string matching.
  - Extended the YouTube publish feature (`video_editor.py`) to properly utilize the `channel_id` parameter.
  - Added `pywebview` to `requirements.txt` and ignored scratch analysis files in `.gitignore`.
