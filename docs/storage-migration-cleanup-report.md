# Storage Migration Cleanup Report

**Date:** 2026-08-22  
**System:** WorkflowVdAi (FastAPI + React + Cloudflare R2 Storage + SQLite/MySQL)  
**Report Location:** `docs/storage-migration-cleanup-report.md`  

---

## 1. Current Architecture

```text
 ┌────────────────────────────────────────────────────────┐
 │                      Web Frontend                      │
 └───────────────────────────┬────────────────────────────┘
                             │
                             ▼
 ┌────────────────────────────────────────────────────────┐
 │                    FastAPI Backend                     │
 └──────┬────────────────────┬────────────────────┬───────┘
        │                    │                    │
        ▼                    ▼                    ▼
┌──────────────┐    ┌────────────────┐   ┌─────────────────┐
│ Cloudflare   │    │ SQLite / MySQL │   │ Temporary Local │
│      R2      │    │  (Metadata &   │   │   Processing    │
│ (Object Store│    │   Job State)   │   │  (FFmpeg/TTS)   │
└──────────────┘    └────────────────┘   └─────────────────┘
```

- **Permanent Object Storage:** Cloudflare R2 via `R2StorageService` (`app/services/storage_service.py`).
- **Object Serving & Proxy:** `GET /api/storage/files/{file_path}` (`app/api/routes/storage.py`) serves R2 public URLs or local R2 emulator files.
- **Temporary Local Processing Storage:** `data/translator/jobs/{job_id}/`, `data/translator/assets/`, `data/projects/{project_id}/` used solely during active FFmpeg rendering, TTS generation, and audio extraction. Intermediate files are automatically purged (`is_cleaned=True`) upon job completion.

---

## 2. Classification of Files & Folders

### A. Definitely Unused / Obsolete (Scratch Scripts)
- `backend/scratch/inspect_current_state.py`
- `backend/scratch/poll_vt_848257.py`
- `backend/scratch/query_db.py`
- `backend/scratch/run_full_e2e.py`
- `backend/scratch/test_api_endpoints.py`
- `backend/scratch/test_api_response.py`
- `backend/scratch/test_live_job.py`
- `backend/scratch/test_mysql_fastapi_server.py`
- `backend/scratch/test_mysql_sync.py`
- `backend/scratch/test_phase2_direct.py`
- `backend/scratch/test_phase2_live.py`
> **Status:** Safe to delete (one-off debug scripts created during initial development).

### B. Legacy Frontend Fallbacks (To be Updated)
- `frontend/src/pages/VideoTranslator.jsx`: Video player and download button hardcoded `/media/` fallback without checking `job.output_url` first.
> **Status:** Update component to prioritize `job.output_url` (R2 URL).

### C. Required Services & Infrastructure (DO NOT DELETE)
- `backend/app/services/storage_service.py`: Core Cloudflare R2 storage client with local emulator fallback.
- `backend/app/api/routes/storage.py`: FastAPI route for R2 object streaming and local storage fallback.
- `backend/app/services/file_manager.py`: Temporary local workspace file manager for Standard Projects.
- `backend/app/services/video_source/`: Video download & URL resolution adapters.

### D. Temporary Local Processing Folders (DO NOT DELETE)
- `data/translator/assets/`
- `data/translator/jobs/`
- `data/projects/`
- `data/r2_storage/`
> **Status:** Keep. Required for active FFmpeg video muxing, audio extraction, TTS staging, and local R2 emulator.

---

## 3. Legacy Environment Variables
- `.env` & `.env.example` already feature R2 variables (`R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET_NAME`, `R2_ENDPOINT_URL`, `R2_PUBLIC_DOMAIN`).
- No legacy storage environment variables exist that require deletion.

---

## 4. Legacy Dependencies
- All python packages (`boto3`, `fastapi`, `sqlalchemy`, `httpx`, `aiosqlite`, `aiomysql`, `pydantic-settings`) and npm packages (`axios`, `react`, `react-dom`, `vite`) are actively required.
- No unused storage dependencies found.

---

## 5. Legacy Database Fields
- **Fields:** `file_path`, `output_video_path`
- **R2 Fields:** `r2_key`, `url`, `output_url`
- **Decision:** **KEEP ALL FIELDS**. `file_path` and `output_video_path` are required for local temporary processing paths during FFmpeg execution and backwards compatibility with historical job records.

---

## 6. Risk Assessment
- **Zero Risk:** Removing developer scratch scripts in `backend/scratch/` will not impact application runtime or automated tests.
- **Improved UX:** Updating `VideoTranslator.jsx` to prefer `job.output_url` completes end-to-end R2 cloud video streaming for users.
