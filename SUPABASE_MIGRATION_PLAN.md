# SUPABASE MIGRATION PLAN: AUTO TRANS AI

## 1. Current Architecture
Current system: Local-First Script-to-Video & AI Video Translation & Dubbing Pipeline with 6-Stage Unified Workflow Engine.
- **Frontend:** React 18 SPA + Vite 5 (Port 5173).
- **Backend:** FastAPI (Python 3.12, Async/Await).
- **Database:** SQLite 3 (`data/workflow.db`) using SQLAlchemy 2.0 async engine (`aiosqlite`) + dynamic DDL schema listener.
- **Storage:** Local file system (`data/projects/`, `data/translator/`) + Cloudflare R2 object storage (boto3 S3 API) with fallback to local `data/r2_storage/`.

---

## 2. Current Database
- **Engine:** SQLite 3 (WAL mode) / MySQL URL compatible.
- **Driver:** `aiosqlite`
- **ORM:** SQLAlchemy 2.0.30
- **Migration System:** Dynamic DDL Inspector (`_sync_schema_sync` in `database.py`) & Alembic 1.13.0.
- **Database URL Pattern:** `sqlite+aiosqlite:///data/workflow.db`
- **Current Tables (23 Total):** `projects`, `segments`, `jobs`, `assets`, `providers`, `usage_snapshots`, `errors`, `video_assets`, `video_translation_jobs`, `video_translation_segments`, `video_edit_configs`, `qc_reports`, `youtube_channels`, `youtube_publications`, `project_glossaries`, `speaker_voice_mappings`, `workflow_executions`, `workflow_stage_executions`, `workflow_step_executions`, `system_settings`, `ai_function_configs`, `ai_models`, `social_accounts`.

---

## 3. Current Storage
- **Local Persistent Directories:**
  - `data/projects/{project_id}/`: Audio clips, segment assets, combined video.
  - `data/translator/assets/`: Raw source video files (`video_assets`).
  - `data/translator/jobs/{job_id}/`: Audio extracted files, segment TTS audio files, synced audio files, final translated video output.
  - `data/r2_storage/`: Fallback directory when R2 boto3 client credentials are missing.
- **Cloud Storage:** Cloudflare R2 via `boto3` (`R2StorageService`).
- **Temporary Processing Storage:** Local temp folder (`temp/` / system temp) for FFmpeg filtergraphs, chunking, and intermediate stream files.

---

## 4. All Tables
| Table Name | Purpose | Primary Key | Foreign Keys | Key Columns | Indexes / Constraints |
|---|---|---|---|---|---|
| `projects` | Script-to-video project record | `id` (String 36) | None | `title`, `workflow_status`, `script_raw`, `output_video_path` | PK `id` |
| `segments` | Script-to-video segment | `id` (Integer Auto) | `project_id -> projects.id` | `segment_number`, `text_content`, `audio_path`, `video_path` | FK `project_id`, Index `project_id` |
| `jobs` | Script-to-video job | `id` (String 36) | `project_id`, `segment_id` | `job_type`, `status`, `output_path` | FK `project_id`, `segment_id` |
| `assets` | Script-to-video asset | `id` (String 36) | `project_id`, `segment_id` | `asset_type`, `file_path`, `file_format`, `file_size` | FK `project_id`, `segment_id` |
| `providers` | AI Provider config & quota | `id` (String 50) | None | `name`, `provider_type`, `is_active`, `api_key_primary` | PK `id` |
| `usage_snapshots` | AI resource consumption | `id` (Integer Auto) | `provider_id -> providers.id` | `resource_type`, `used`, `limit_val`, `cost` | FK `provider_id` |
| `errors` | Diagnostic error traceback log | `id` (Integer Auto) | `job_id -> jobs.id` | `error_type`, `http_status`, `message`, `traceback` | FK `job_id` |
| `video_assets` | Video Translator source video | `id` (String 36) | None | `source_type`, `source_url`, `file_path`, `r2_key`, `url` | PK `id` |
| `video_translation_jobs` | Video Translator pipeline job | `id` (String 36) | `asset_id -> video_assets.id` | `status`, `stage`, `output_video_path`, `r2_key`, `output_url` | FK `asset_id`, Index `asset_id` |
| `video_translation_segments` | Timestamped transcript segment | `id` (Integer Auto) | `job_id -> video_translation_jobs.id` | `segment_number`, `original_text`, `translated_text`, `tts_audio_path`, `synced_audio_path` | FK `job_id`, Index `job_id` |
| `video_edit_configs` | Studio editing parameters | `id` (String 36) | None | `job_id`, `project_id`, `target_aspect_ratio`, `logo_path`, `bgm_path` | PK `id` |
| `qc_reports` | Quality control report | `id` (String 36) | None | `job_id`, `project_id`, `audio_lufs`, `sync_drift_ms`, `pass_status` | PK `id` |
| `youtube_channels` | YouTube OAuth channel binding | `id` (String 36) | None | `channel_name`, `channel_id`, `credentials_json` | PK `id` |
| `youtube_publications` | YouTube video upload log | `id` (String 36) | `channel_id -> youtube_channels.id` | `job_id`, `video_id`, `video_url`, `privacy_status` | FK `channel_id` |
| `project_glossaries` | Project domain terminology | `id` (String 36) | `project_id -> projects.id` | `source_term`, `translated_term`, `term_type` | FK `project_id` |
| `speaker_voice_mappings` | Character voice mapping | `id` (String 36) | `project_id -> projects.id` | `speaker_id`, `speaker_name`, `voice_provider`, `voice_id` | FK `project_id` |
| `workflow_executions` | 6-Stage Workflow execution | `id` (String 36) | `project_id -> projects.id` | `workflow_type`, `status`, `current_stage` | FK `project_id` |
| `workflow_stage_executions` | Stage status tracking | `id` (String 36) | `workflow_execution_id -> workflow_executions.id` | `stage_name`, `status`, `error` | FK `workflow_execution_id` |
| `workflow_step_executions` | Step status tracking | `id` (String 36) | `stage_execution_id -> workflow_stage_executions.id` | `step_name`, `status`, `input_data`, `output_data` | FK `stage_execution_id` |
| `system_settings` | Infrastructure settings KV | `key` (String 100) | None | `value`, `category`, `description` | PK `key` |
| `ai_function_configs` | AI function capability binding | `function_id` (String 50) | None | `function_name`, `capability`, `primary_provider_id`, `model_id` | PK `function_id` |
| `ai_models` | Catalog of AI models | `id` (String 100) | None | `provider_id`, `model_name`, `capabilities`, `is_default` | PK `id` |
| `social_accounts` | Social account integration | `id` (String 50) | None | `platform`, `account_name`, `status`, `credentials_json` | PK `id` |

---

## 5. All File Types
1. **Source Video (`video_assets`):** Original downloaded or uploaded MP4/MKV/WEBM source files.
2. **Extracted Audio (`video_translation_jobs`):** WAV/AAC 44.1kHz audio extracted from source video for STT analysis.
3. **TTS Audio Segments (`video_translation_segments` / `segments`):** Generated speech clips per segment (WAV/MP3).
4. **Synced Audio Segments (`video_translation_segments`):** Time-stretched / compressed audio segments matching visual timestamps.
5. **Final Rendered Video (`video_translation_jobs` / `projects`):** Output MP4 video with dubbed audio & subtitles.
6. **Watermark / Logo (`video_edit_configs`):** PNG/JPG overlay images for video editor studio.
7. **Background Music (BGM) (`video_edit_configs`):** MP3/WAV audio tracks for background music ducking.
8. **QC Reports & Subtitle Files (`qc_reports`):** JSON / ASS / SRT subtitle files.

---

## 6. Data Relationship Mapping
- **`projects` (1) ── (N) `segments` (1) ── (N) `assets`**
  - Project output video referenced by `projects.output_video_path`.
  - Segment audio/video clips referenced by `segments.audio_path` and `segments.video_path`.
- **`video_assets` (1) ── (N) `video_translation_jobs` (1) ── (N) `video_translation_segments`**
  - Source video file referenced by `video_assets.file_path` & `video_assets.r2_key`.
  - Extracted audio & final video referenced by `video_translation_jobs.output_video_path` & `video_translation_jobs.r2_key`.
  - Segment TTS audio & synced audio referenced by `video_translation_segments.tts_audio_path` & `synced_audio_path`.
- **`video_edit_configs` (1) ── (1) `video_translation_jobs` / `projects`**
  - Assets referenced by `video_edit_configs.logo_path` & `video_edit_configs.bgm_path`.

---

## 7. Target Supabase Architecture

```text
                               FASTAPI BACKEND
                                      │
              ┌───────────────────────┴───────────────────────┐
              ▼                                               ▼
   SUPABASE POSTGRESQL DB                             SUPABASE STORAGE
   (SQLAlchemy 2.0 + asyncpg)                     (Supabase Storage API)
              │                                               │
   ├── 23 Relational Tables                           ├── Bucket: autotransai-private (Private)
   ├── Foreign Keys & Indexes                         │   ├── projects/{id}/...
   ├── Cascading Deletes                              │   ├── translator/assets/{id}/...
   └── JSON/Text Fields                               │   └── translator/jobs/{id}/...
                                                      └── Bucket: autotransai-public (Public)
                                                          └── publications/...
```

---

## 8. Database Migration Plan
1. **Database Engine & Driver:** Switch engine to PostgreSQL (`postgresql+asyncpg://...`).
2. **Schema Creation:** Execute `Base.metadata.create_all()` via async engine connected to Supabase PostgreSQL.
3. **Data Dump & Load:** Script `scripts/migrate_to_supabase.py` reads existing SQLite data from `data/workflow.db` and inserts into Supabase PostgreSQL, preserving all UUID Primary Keys, Auto-Increment IDs, Timestamps, and Foreign Key constraints.
4. **Verification:** Compare record counts and FK consistency between SQLite and Supabase PostgreSQL.

---

## 9. Storage Migration Plan
1. **Buckets Setup:**
   - `autotransai-private`: Private storage for source videos, audio extracts, TTS clips, intermediate assets. Access via Signed URLs.
   - `autotransai-public`: Public storage for final published clips and public assets.
2. **Storage Service Refactoring:**
   - Refactor `app/services/storage_service.py` into `SupabaseStorageService`.
   - Methods: `upload_file()`, `download_file()`, `delete_file()`, `get_url()`, `get_signed_url()`, `list_project_files()`, `delete_project_files()`.
   - Maintain full signature compatibility with legacy `R2StorageService`.
3. **File Migration:**
   - Iterate through local `data/` and `data/r2_storage/` directories.
   - Upload persistent files to Supabase Storage under structured path prefixes.
   - Update database record path & key references (`r2_key` / `file_path` / `url`).

---

## 10. Data Mapping
- SQLite SQLite Types ➔ Supabase PostgreSQL Types:
  - `VARCHAR / String(36)` ➔ `VARCHAR(36)` / `TEXT`
  - `INTEGER` ➔ `INTEGER` / `BIGINT`
  - `FLOAT` ➔ `DOUBLE PRECISION`
  - `BOOLEAN` ➔ `BOOLEAN`
  - `DATETIME` ➔ `TIMESTAMP WITH TIME ZONE`
  - `TEXT` ➔ `TEXT`

---

## 11. File Mapping
- Local Path `data/projects/{project_id}/{filename}` ➔ Supabase Path `projects/{project_id}/{filename}`
- Local Path `data/translator/assets/{asset_id}/{filename}` ➔ Supabase Path `translator/assets/{asset_id}/{filename}`
- Local Path `data/translator/jobs/{job_id}/{filename}` ➔ Supabase Path `translator/jobs/{job_id}/{filename}`

---

## 12. Environment Variable Changes
Add to `.env` and `app/config.py`:
```env
SUPABASE_URL=https://<your-supabase-project-ref>.supabase.co
SUPABASE_ANON_KEY=<your-anon-key>
SUPABASE_SERVICE_ROLE_KEY=<your-service-role-key>
SUPABASE_DATABASE_URL=postgresql+asyncpg://postgres:<password>@db.<your-supabase-project-ref>.supabase.co:5432/postgres
SUPABASE_STORAGE_BUCKET_PRIVATE=autotransai-private
SUPABASE_STORAGE_BUCKET_PUBLIC=autotransai-public
```

---

## 13. Required Code Changes
1. `backend/requirements.txt`: Add `asyncpg`, `supabase`.
2. `backend/app/config.py`: Add Supabase settings and update `DB_URL` logic to prioritize `SUPABASE_DATABASE_URL` or `DATABASE_URL`.
3. `backend/app/database.py`: Support `postgresql+asyncpg` dialect, ensure WAL/PRAGMA sqlite specifics execute conditionally.
4. `backend/app/services/storage_service.py`: Upgrade `R2StorageService` / `StorageService` to use Supabase Storage client while retaining fallback local store capability for offline development.
5. Routers & Pipeline Stages (`ingest_stage.py`, `produce_stage.py`, `video_translator.py`, `video_editor.py`, `cleanup_service.py`): Update storage service calls where necessary.

---

## 14. Testing Plan
1. **DB Connectivity Test:** Connect to Supabase PostgreSQL and verify schema creation & CRUD operations.
2. **Data Integrity Test:** Run `scripts/migrate_to_supabase.py` and verify 100% row match.
3. **Storage Test:** Upload test file to `autotransai-private` bucket, test signed URL generation, download, and deletion.
4. **Pipeline End-to-End Test:** Run full video translator workflow job and verify source upload ➔ audio extract ➔ STT ➔ TTS ➔ output video upload on Supabase.
5. **Project Cleanup Test:** Delete project / job and verify related database rows & Supabase storage files are deleted without leaving orphan files.

---

## 15. Rollback Plan
- Existing `data/workflow.db` and local `data/` files remain 100% intact.
- Reverting `.env` to `DATABASE_URL=sqlite+aiosqlite:///data/workflow.db` instantly restores original offline SQLite system.

---

## 16. Risks & Mitigation
- **Connection Latency / SSL for Supabase Postgres:** Use pooled connection string or direct port 5432 with `ssl=require`.
- **Supabase Storage Rate Limits:** Implement exponential backoff retries in `SupabaseStorageService`.
- **Orphan Files on Partial Deletion:** Scope files cleanly by `project_id` and `job_id` prefixes to enable batch prefix deletion `delete_project_files(project_id)`.
