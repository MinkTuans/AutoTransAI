# AI CHANGELOG

## [2026-09-05] — Fix PostgreSQL asyncpg Datetime DataError (Timestamp tzinfo strip)

### Task Description
Resolved `[HTTP 500] POST /video-translator/jobs` failure caused by asyncpg `DataError: invalid input for query argument $18: can't subtract offset-naive and offset-aware datetimes` when inserting or updating PostgreSQL `TIMESTAMP WITHOUT TIME ZONE` columns.

### Added / Modified / Removed Features
- **Naive UTC Datetime Enforcement:** Updated `video_translator.py`, `heartbeat.py`, `orchestrator.py`, `projects.py`, `usage_snapshot.py`, and `settings.py` so that all timestamp values (`last_heartbeat`, `created_at`, `updated_at`, `connected_at`, `snapshot_at`) use `datetime.now(timezone.utc).replace(tzinfo=None)`.
- **Database Compatibility:** Prevents `asyncpg` from throwing `DataError` when writing to Supabase PostgreSQL database tables.

### Affected Files
- `backend/app/api/routes/video_translator.py`
- `backend/app/api/routes/projects.py`
- `backend/app/services/video_translator/heartbeat.py`
- `backend/app/workflow/orchestrator.py`
- `backend/app/models/settings.py`
- `backend/app/models/usage_snapshot.py`
- `CHANGELOG_AI.md`

---

### Task Description
Resolved the issue where users were unable to add API keys ("Không ấn thêm API key được") from the Settings Studio UI and fixed multi-provider key synchronization to `.env` in the backend `KeyManager` service.

### Added / Modified / Removed Features
- **Frontend Direct Key Action & Save Key Fix:** Added explicit `+ Thêm Key` buttons to every paid AI Provider Card in Settings Studio (`Settings.jsx`). Added in-modal error alert display (`modalError`), direct `onClick` handler on `Save Key` button, input auto-focus, and validation so clicking Save Key will never fail silently or hang when input is missing or invalid.
- **Fixed Table Alignment Bug:** Fixed table row layout misalignment in `Settings.jsx` Key Manager table by replacing `display: flex` on `<td>` with an inner `inline-flex` wrapper and adding `vertical-align: middle` to `.table th, .table td` in `App.css`.
- **Desktop Launcher Auto-Reload:** Added `--reload` flag to Uvicorn in `app_launcher.ps1` so backend Python code changes automatically reload in real time.
- **Backend Key Synchronization & Priority Parsing:** Fixed `_sync_env_file()` in `key_manager.py` to auto-synchronize primary API keys for **all** providers (`GEMINI_API_KEY`, `OPENAI_API_KEY`, `GOOGLE_CLOUD_TTS_API_KEY`, `ELEVENLABS_API_KEY`, `KLING_API_KEY`, `FAL_API_KEY`) into `.env`, `os.environ`, and app `settings`. Updated `providers.py` to safely convert `priority` inputs to valid integers.
- **Verification:** Verified frontend production build via `npm run build` in `frontend/`.

### Affected Files
- `frontend/src/pages/Settings.jsx`
- `frontend/src/App.css`
- `app_launcher.ps1`
- `backend/app/api/routes/providers.py`
- `backend/app/services/key_manager.py`
- `CHANGELOG_AI.md`

---

### Task Description
Designed a modern custom scrollbar for WebKit (Chrome/Edge/Safari/Brave) & Firefox, and re-balanced the input fields in `Project Glossary & Terminology Memory` to reduce the Option select dropdown width to 1/3 size.

### Added / Modified / Removed Features
- **Custom Web Scrollbar:** Added modern, dark-slate custom scrollbar (`8px` track, `#334155` rounded thumb, `#6366f1` hover accent, Firefox `scrollbar-width: thin`) in `App.css`.
- **Glossary Input Re-balancing:** Updated `ProjectGlossaryManager.jsx` form layout so `Source Term` and `Vietnamese Translation` inputs take full flex space while the `Type` Option dropdown is reduced to 150px (1/3 size).
- **Visual Verification:** Build verified via `npm run build` and visually confirmed via browser subagent screenshot.

### Affected Files
- `frontend/src/App.css`
- `frontend/src/components/ProjectGlossaryManager.jsx`
- `CHANGELOG_AI.md`

---

## [2026-09-05] — Complete UI Layout & Responsive CSS Alignment Fixes

### Task Description
Fixed all layout overflow, imbalanced padding, cut-off header navigation links, button margin leakage, and modal dialog alignment issues across the entire application UI.

### Added / Modified / Removed Features
- **Refactored CSS System:** Updated `App.css` with universal `box-sizing: border-box`, standard card padding (`1.5rem`), removed bottom margin leakage on `.btn`, and centered modal dialog classes (`.modal-backdrop`, `.modal-dialog`, `.modal-header`, `.modal-body`, `.modal-footer`).
- **Fixed Header Navbar:** Resolved header right-edge text cut-off on `+ Tạo dự án mới` and `⚙️ Cài đặt` links in `Navbar.jsx` with responsive flex-wrap and container max-width bounds.
- **Standardized Modals:** Refactored all 5 modals in `Settings.jsx` and `YouTubePublisherModal.jsx` to use clean, centered modal dialog structures with balanced top and bottom padding.
- **Verified UI:** Build verified via `npm run build` and live visual verification via `browser_subagent`.

### Affected Files
- `frontend/src/App.css`
- `frontend/src/components/Navbar.jsx`
- `frontend/src/components/YouTubePublisherModal.jsx`
- `frontend/src/pages/Settings.jsx`
- `CHANGELOG_AI.md`

---

## [2026-09-05] — Complete Migration to Supabase PostgreSQL (Option 1)

### Task Description
Completed full database migration from local SQLite (`data/workflow.db`) to **Supabase PostgreSQL** (`postgresql+asyncpg://...`) for **both Development and Production** environments. Removed automatic SQLite fallback in active runtime configuration.

### Added / Modified / Removed Features
- **Configured:** Updated `config.py` `DB_URL` property to require `SUPABASE_DATABASE_URL` or `DATABASE_URL` and raise an explicit `ValueError` if missing. Automatic SQLite fallback in runtime logic is completely disabled.
- **Backed Up:** Created offline backup `data/backup/workflow_before_supabase_migration.db`.
- **Scripted:** Enhanced `migrate_to_supabase.py` with topological table migration order and automatic PostgreSQL sequence resets (`setval`) for auto-increment integer PK tables (`segments`, `video_translation_segments`, `usage_snapshots`, `errors`).
- **Added:** Created [SUPABASE_POSTGRESQL_MIGRATION_REPORT.md](file:///c:/Hack/AutoTransAI/SUPABASE_POSTGRESQL_MIGRATION_REPORT.md) detailing all 19 required migration sections.

### Affected Files
- `backend/app/config.py`
- `backend/app/database.py`
- `backend/scripts/migrate_to_supabase.py`
- `.env`
- `.env.example`
- `SUPABASE_POSTGRESQL_MIGRATION_REPORT.md`
- `PROJECT_KNOWLEDGE_BASE.md`
- `CHANGELOG_AI.md`

---

## [2026-09-05] — Complete Supabase Setup & Decommissioning of Cloudflare R2

### Task Description
Completed full Supabase Storage & PostgreSQL deployment and **100% decommissioned Cloudflare R2** from active application code, services, routers, settings, schemas, dependencies, and environment files.

### Added / Modified / Removed Features
- **Removed:** Decommissioned `boto3` dependency and Cloudflare R2 client initialization (`_get_boto_client()`).
- **Removed:** Removed all `R2_*` environment variables from `.env.example`, `config.py`, and Settings UI.
- **Refactored:** Refactored `storage_service.py` to use `SupabaseStorageService` exclusively (with `data/supabase_storage/` offline dev fallback).
- **Added:** [SUPABASE_INSTALLATION_REQUIREMENTS.md](file:///c:/Hack/AutoTransAI/SUPABASE_INSTALLATION_REQUIREMENTS.md), [SUPABASE_SETUP_GUIDE.md](file:///c:/Hack/AutoTransAI/SUPABASE_SETUP_GUIDE.md), [R2_REMOVAL_AUDIT.md](file:///c:/Hack/AutoTransAI/R2_REMOVAL_AUDIT.md), and [SUPABASE_SETUP_AND_R2_REMOVAL_REPORT.md](file:///c:/Hack/AutoTransAI/SUPABASE_SETUP_AND_R2_REMOVAL_REPORT.md).

### Affected Files
- `backend/requirements.txt`
- `backend/app/config.py`
- `backend/app/services/storage_service.py`
- `backend/app/services/cleanup_service.py`
- `backend/app/services/settings_service.py`
- `backend/app/schemas/settings_schema.py`
- `backend/app/api/routes/settings.py`
- `frontend/src/pages/Settings.jsx`
- `frontend/src/pages/Dashboard.jsx`
- `.env.example`
- `PROJECT_KNOWLEDGE_BASE.md`
- `CHANGELOG_AI.md`

---

## [2026-09-05] — Settings & AI Provider Management System & Gemini STT Policy

### Task Description
Developed and verified the **Settings & AI Provider Management System** for AutoTransAI on Supabase PostgreSQL, incorporating API Key pool rotation, key masking security (`AIza****XXXX`), custom model definitions, social media account management, and strict **Google Gemini-only Speech-to-Text (STT)** execution.

### Added / Modified / Removed Features
- **Added:** Unit tests in [test_settings_and_stt.py](file:///c:/Hack/AutoTransAI/backend/tests/unit/test_settings_and_stt.py) verifying Settings CRUD, key masking, custom models, and Gemini STT failure policy.
- **Added:** [SETTINGS_AI_IMPLEMENTATION_PLAN.md](file:///c:/Hack/AutoTransAI/SETTINGS_AI_IMPLEMENTATION_PLAN.md) and [SETTINGS_AI_IMPLEMENTATION_FINAL_REPORT.md](file:///c:/Hack/AutoTransAI/SETTINGS_AI_IMPLEMENTATION_FINAL_REPORT.md).
- **Enforced:** Gemini-only Speech-to-Text policy in `translator_service.py` (pipeline stops on Gemini failure without calling OpenAI/Whisper when fallback is disabled).
- **Enhanced:** Settings Studio UI in [Settings.jsx](file:///c:/Hack/AutoTransAI/frontend/src/pages/Settings.jsx) with 8 management tabs.

### Affected Files
- `frontend/src/pages/Settings.jsx`
- `backend/app/services/settings_service.py`
- `backend/app/services/video_translator/translator_service.py`
- `backend/tests/unit/test_settings_and_stt.py`
- `SETTINGS_AI_IMPLEMENTATION_PLAN.md`
- `SETTINGS_AI_IMPLEMENTATION_FINAL_REPORT.md`
- `PROJECT_KNOWLEDGE_BASE.md`
- `CHANGELOG_AI.md`

### Knowledge Base Updates
- Updated `PROJECT_KNOWLEDGE_BASE.md` feature inventory and STT description to record Gemini-only STT policy and Settings Studio architecture.

---

## [2026-09-05] — Supabase Database & File Storage Migration

### Task Description
Migrated the entire database and file storage infrastructure to **Supabase PostgreSQL** and **Supabase Storage**, establishing a cloud-native, scalable storage system while preserving 100% backward-compatible fallback to local SQLite and persistent storage.

### Added / Modified / Removed Features
- **Added:** `SupabaseStorageService` abstraction supporting private (`autotransai-private`) and public (`autotransai-public`) buckets, signed URLs, public URLs, and prefix-scoped project file cleanup.
- **Added:** Database & Storage Migration Runner script [migrate_to_supabase.py](file:///c:/Hack/AutoTransAI/backend/scripts/migrate_to_supabase.py) for schema creation and data transfer across all 23 database tables.
- **Modified:** Database layer [database.py](file:///c:/Hack/AutoTransAI/backend/app/database.py) to support `postgresql+asyncpg://` dialect, connection pool pre-pinging, and SSL settings.
- **Modified:** Application Settings [config.py](file:///c:/Hack/AutoTransAI/backend/app/config.py) to parse Supabase database URLs and storage settings.

### Affected Files
- `backend/requirements.txt`
- `backend/app/config.py`
- `backend/app/database.py`
- `backend/app/services/storage_service.py`
- `backend/scripts/migrate_to_supabase.py`
- `SUPABASE_MIGRATION_PLAN.md`
- `SUPABASE_MIGRATION_VERIFICATION_REPORT.md`
- `SUPABASE_MIGRATION_FINAL_REPORT.md`
- `PROJECT_KNOWLEDGE_BASE.md`
- `CHANGELOG_AI.md`

### Database / API / Configuration Changes
- Added dependencies: `asyncpg>=0.29.0`, `supabase>=2.7.0`.
- Added environment variables: `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_DATABASE_URL`, `SUPABASE_STORAGE_BUCKET_PRIVATE`, `SUPABASE_STORAGE_BUCKET_PUBLIC`.

### Knowledge Base Updates
- Updated `PROJECT_KNOWLEDGE_BASE.md` sections for Database & ORM and Storage & Media Processing to document Supabase PostgreSQL and Supabase Storage integration.
