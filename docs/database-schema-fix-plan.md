# Database Schema Fix Plan

**Date:** 2026-08-22  
**System:** WorkflowVdAi  
**File Location:** `docs/database-schema-fix-plan.md`  

---

## Step 1: Update `backend/app/database.py` with Dialect-Agnostic Inspection
Refactor `init_db()` in `backend/app/database.py` to use SQLAlchemy `inspect(conn)` (or `run_sync(inspect)`):
- Inspect all tables declared in `Base.metadata.tables`.
- Compare ORM columns against database engine columns.
- Automatically execute `ALTER TABLE {table_name} ADD COLUMN ...` for any missing columns regardless of whether the active database engine is SQLite, MySQL, MariaDB, or PostgreSQL.

---

## Step 2: Create Alembic Migration File
Create `backend/alembic/versions/20260822_sync_schema.py`:
- Add explicit Alembic `op.add_column('video_translation_jobs', sa.Column('llm_provider_id', sa.String(length=50), nullable=True, server_default='openai'))`.
- Include columns for `r2_key`, `output_url`, `is_cleaned`, `media_url`, `stage`, `overall_progress_pct`, `pid`, `last_heartbeat`, `ffmpeg_stats_json`.

---

## Step 3: Standalone Migration CLI Script
Create `backend/scripts/sync_db_schema.py`:
- Run schema verification and column sync on startup or manually via `python backend/scripts/sync_db_schema.py`.

---

## Step 4: Verification & Test Execution
- Run unit test suite: `python -m pytest backend/tests/unit/`.
- Run integration test suite: `python -m pytest backend/tests/integration/`.
- Verify MySQL database column list (`DESCRIBE video_translation_jobs`).
- Verify Job Creation API `POST /api/video-translator/jobs` on both SQLite and MySQL databases.
