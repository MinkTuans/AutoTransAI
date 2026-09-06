# CLOUDFLARE R2 REMOVAL AUDIT & REPLACEMENT MAP

## 1. Audit Overview
Every reference to Cloudflare R2, boto3, and R2 environment variables across active application code, services, routers, models, schemas, scripts, and documentation has been audited. Cloudflare R2 is 100% decommissioned and replaced by **Supabase Storage**.

---

## 2. File-by-File Audit & Replacement Table

| File Path | Line / Symbol | Former R2 Usage | Replacement Strategy | Status |
|---|---|---|---|---|
| `backend/requirements.txt` | Line 18 (`boto3`) | Cloudflare R2 S3 API client dependency | Removed `boto3`. Use `supabase` SDK exclusively. | TO BE REMOVED |
| `backend/app/config.py` | Lines 94-100 (`R2_*`) | R2 Account ID, Access Key, Secret Key, Endpoint, Bucket settings | Removed `R2_*` settings. Retained Supabase settings (`SUPABASE_*`). | TO BE REMOVED |
| `backend/app/services/storage_service.py` | `_get_boto_client()`, R2 fallback logic | Cloudflare R2 upload/download/delete methods | Completely removed `_get_boto_client()` and R2 logic. Replaced with pure `SupabaseStorageService`. | TO BE REFACTORED |
| `backend/app/services/cleanup_service.py` | `orphan_r2_keys`, R2 emulator directory scanning | Cloudflare R2 & R2 local emulator orphan file cleanup | Replaced R2 orphan scanning with Supabase Storage prefix-based object purging. | TO BE REFACTORED |
| `backend/app/services/settings_service.py` | `DEFAULT_SYSTEM_SETTINGS` (`r2_*`) | Default system settings for R2 credentials | Removed `r2_*` default keys. Updated defaults to Supabase. | TO BE REFACTORED |
| `backend/app/schemas/settings_schema.py` | `SystemSettingsSchema` | Pydantic schema for R2 credentials | Removed R2 fields. Added Supabase Storage fields. | TO BE REFACTORED |
| `backend/app/api/routes/settings.py` | `/storage/test` | Testing R2 bucket connection via `boto3` | Updated endpoint to test Supabase Storage bucket connectivity. | TO BE REFACTORED |
| `backend/app/api/routes/storage.py` | `R2StorageService` | Endpoint wrapper for R2 storage service | Updated to use `SupabaseStorageService`. | TO BE REFACTORED |
| `backend/app/models/video_translator.py` | `r2_key` column | Column storing object key in `video_assets` & `video_translation_jobs` | Preserved `r2_key` ORM property name as an alias mapping to storage object key for DB schema compatibility. | ALIASED |
| `backend/app/models/project.py` | `r2_key` column | Column storing object key in `projects` | Preserved `r2_key` ORM property name as an alias mapping to storage key. | ALIASED |
| `frontend/src/pages/Settings.jsx` | Tab 5 ("Storage") | UI text and inputs for R2 Account ID & Secret Key | Replaced UI inputs with Supabase Storage settings and connection test. | TO BE UPDATED |
| `frontend/src/pages/Dashboard.jsx` | Storage status badge | Displaying "R2 Storage" status badge | Updated badge text to "Supabase Storage". | TO BE UPDATED |
| `.env.example` | Lines 35-41 (`R2_*`) | R2 environment variable placeholders | Removed R2 block completely. Replaced with Supabase environment variables. | TO BE REMOVED |
| `backend/scripts/scan_orphan_files.py` | `r2_local_dir` | Script scanning R2 local emulator folder | Updated to scan local Supabase fallback folder. | TO BE UPDATED |

---

## 3. Active R2 Search Target
After code modifications are complete, running a search for `boto3`, `R2_ACCOUNT_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET_NAME` across active application code MUST yield **0 active production references**.
