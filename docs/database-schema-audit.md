# Database Schema Audit Report

**Date:** 2026-08-22  
**System:** WorkflowVdAi  
**File Location:** `docs/database-schema-audit.md`  

---

## 1. Executive Summary

A 3-way schema audit (**Model ↔ Migration ↔ Database**) was conducted across the codebase, Alembic version history, SQLite database (`data/workflow.db`), and MySQL/MariaDB database (`workflowvdai`).

A critical schema mismatch was identified:
- **Root Symptom:** `[pymysql.err.OperationalError] (1054, "Unknown column 'llm_provider_id' in 'field list'")` during job insertion on MySQL.
- **Root Cause:** 
  1. `init_db()` in `backend/app/database.py` used SQLite-specific `PRAGMA table_info(...)` queries to apply column alterations. When connected to MySQL/MariaDB, `PRAGMA` queries threw syntax errors caught by empty `except Exception:` blocks, skipping column creation.
  2. Alembic migration version `202da08bcdd8_initial_schema.py` was an empty stub (`pass`).
  3. `Base.metadata.create_all` creates new missing tables but does not alter existing tables to add newly declared ORM columns (`llm_provider_id`, `r2_key`, `output_url`, `is_cleaned`, `media_url`, etc.).

---

## 2. 3-Way Audit Matrix (Models vs Alembic vs SQLite vs MySQL)

| Table | Column | Model | Alembic | SQLite DB | MySQL DB | Status / Mismatch |
|-------|--------|-------|---------|-----------|----------|-------------------|
| `video_translation_jobs` | `id` | YES | YES | YES | YES | MATCH |
| `video_translation_jobs` | `asset_id` | YES | YES | YES | YES | MATCH |
| `video_translation_jobs` | `source_language` | YES | YES | YES | YES | MATCH |
| `video_translation_jobs` | `detected_language` | YES | YES | YES | YES | MATCH |
| `video_translation_jobs` | `target_language` | YES | YES | YES | YES | MATCH |
| `video_translation_jobs` | `audio_provider_id` | YES | YES | YES | YES | MATCH |
| `video_translation_jobs` | `llm_provider_id` | **YES** | **STUB** | **YES** | **NO ❌** | **CRITICAL MISMATCH (Missing in MySQL)** |
| `video_translation_jobs` | `voice_id` | YES | YES | YES | YES | MATCH |
| `video_translation_jobs` | `voice_name` | YES | YES | YES | YES | MATCH |
| `video_translation_jobs` | `original_audio_mode` | YES | YES | YES | YES | MATCH |
| `video_translation_jobs` | `status` | YES | YES | YES | YES | MATCH |
| `video_translation_jobs` | `stage` | YES | YES | YES | YES | MATCH |
| `video_translation_jobs` | `stage_progress_pct` | YES | YES | YES | YES | MATCH |
| `video_translation_jobs` | `overall_progress_pct` | YES | YES | YES | YES | MATCH |
| `video_translation_jobs` | `progress_pct` | YES | YES | YES | YES | MATCH |
| `video_translation_jobs` | `current_step` | YES | YES | YES | YES | MATCH |
| `video_translation_jobs` | `pid` | YES | YES | YES | YES | MATCH |
| `video_translation_jobs` | `last_heartbeat` | YES | YES | YES | YES | MATCH |
| `video_translation_jobs` | `ffmpeg_stats_json` | YES | YES | YES | YES | MATCH |
| `video_translation_jobs` | `completed_segments_count` | YES | YES | YES | YES | MATCH |
| `video_translation_jobs` | `total_segments_count` | YES | YES | YES | YES | MATCH |
| `video_translation_jobs` | `output_video_path` | YES | YES | YES | YES | MATCH |
| `video_translation_jobs` | `r2_key` | YES | YES | YES | YES | MATCH |
| `video_translation_jobs` | `output_url` | YES | YES | YES | YES | MATCH |
| `video_translation_jobs` | `is_cleaned` | YES | YES | YES | YES | MATCH |
| `video_translation_jobs` | `error_message` | YES | YES | YES | YES | MATCH |
| `video_translation_jobs` | `created_at` | YES | YES | YES | YES | MATCH |
| `video_translation_jobs` | `updated_at` | YES | YES | YES | YES | MATCH |

*All other 9 tables (`video_assets`, `video_translation_segments`, `projects`, `segments`, `jobs`, `assets`, `providers`, `usage_snapshots`, `errors`) have 100% column parity across SQLite and MySQL.*

---

## 3. Schema Mismatch Classification

- **Type C Mismatch (Database Missing Column):** `video_translation_jobs.llm_provider_id` is declared in SQLAlchemy Model `VideoTranslationJob` and present in SQLite, but missing in MySQL database table `video_translation_jobs`.
- **Engine Lock-in (PRAGMA usage):** `backend/app/database.py` `init_db()` relies on SQLite `PRAGMA table_info` instead of dialect-agnostic SQLAlchemy inspection tools.

---

## 4. Proposed Resolution Strategy

1. **Dialect-Agnostic Automatic Schema Sync in `init_db()` (`app/database.py`):**
   - Replace SQLite-specific `PRAGMA table_info` queries with SQLAlchemy `inspect(conn)` database column reflection.
   - Dynamically inspect existing database tables across any database engine (SQLite, MySQL, PostgreSQL) and automatically issue `ALTER TABLE {table} ADD COLUMN {column}` for any missing ORM columns.
2. **Alembic Migration Script (`alembic/versions/20260822_sync_schema.py`):**
   - Create explicit Alembic migration containing all table definitions and column additions for `llm_provider_id`, `r2_key`, `stage`, `overall_progress_pct`, `pid`, `last_heartbeat`, `ffmpeg_stats_json`, etc.
3. **Database Schema Sync Script (`scripts/sync_db_schema.py`):**
   - Provide standalone CLI script to run schema sync against active database engine.
