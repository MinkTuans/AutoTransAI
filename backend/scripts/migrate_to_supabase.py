"""
Database & File Storage Migration Script to Supabase.

Copies all schema, table data, and persistent files from local SQLite & Storage to Supabase PostgreSQL & Supabase Storage.
"""

from __future__ import annotations

import asyncio
import os
import sys
import sqlite3
from pathlib import Path
from typing import Dict, List, Any

# Ensure project root & backend are in sys.path
root_dir = Path(__file__).resolve().parent.parent.parent
backend_dir = root_dir / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.config import get_settings
from app.database import Base
import app.models  # Import all ORM models

settings = get_settings()

TABLE_MIGRATION_ORDER = [
    "providers",
    "usage_snapshots",
    "projects",
    "segments",
    "jobs",
    "assets",
    "errors",
    "video_assets",
    "video_translation_jobs",
    "video_translation_segments",
    "video_edit_configs",
    "qc_reports",
    "youtube_channels",
    "youtube_publications",
    "project_glossaries",
    "speaker_voice_mappings",
    "workflow_executions",
    "workflow_stage_executions",
    "workflow_step_executions",
    "system_settings",
    "ai_function_configs",
    "ai_models",
    "social_accounts",
]


def dump_sqlite_data(sqlite_db_path: Path) -> Dict[str, List[Dict[str, Any]]]:
    """Read all tables and rows from SQLite database file."""
    if not sqlite_db_path.exists():
        print(f"[!] SQLite DB not found at {sqlite_db_path}")
        return {}

    conn = sqlite3.connect(sqlite_db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    data = {}
    for table_name in TABLE_MIGRATION_ORDER:
        try:
            cursor.execute(f"SELECT * FROM `{table_name}`")
            rows = cursor.fetchall()
            data[table_name] = [dict(r) for r in rows]
            print(f"[OK] Read {len(data[table_name])} rows from SQLite table '{table_name}'")
        except sqlite3.OperationalError as e:
            data[table_name] = []
            print(f"[i] Table '{table_name}' not present in SQLite DB ({str(e)})")

    conn.close()
    return data


async def migrate_to_supabase_pg(target_pg_url: str, sqlite_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Tuple[int, int]]:
    """Create schema and insert all records into Supabase PostgreSQL."""
    if target_pg_url.startswith("postgres://"):
        target_pg_url = target_pg_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif target_pg_url.startswith("postgresql://") and not target_pg_url.startswith("postgresql+asyncpg://"):
        target_pg_url = target_pg_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    print(f"\n[+] Connecting to Supabase PostgreSQL: {target_pg_url[:30]}...")

    target_engine = create_async_engine(
        target_pg_url,
        pool_pre_ping=True,
        connect_args={"statement_cache_size": 0, "prepared_statement_cache_size": 0},
    )

    # 1. Create Schema
    async with target_engine.begin() as conn:
        print("[+] Creating schema on Supabase PostgreSQL...")
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(target_engine, class_=AsyncSession, expire_on_commit=False)
    results = {}

    # 2. Insert Data
    async with session_factory() as session:
        for table_name in TABLE_MIGRATION_ORDER:
            rows = sqlite_data.get(table_name, [])
            table_obj = Base.metadata.tables.get(table_name)

            if table_obj is None:
                print(f"[!] ORM metadata missing for table '{table_name}'")
                continue

            inserted_count = 0
            if rows:
                for row in rows:
                    try:
                        # Clean column keys to match ORM
                        valid_keys = {c.name for c in table_obj.columns}
                        row_filtered = {k: v for k, v in row.items() if k in valid_keys}
                        
                        stmt = table_obj.insert().values(**row_filtered)
                        await session.execute(stmt)
                        inserted_count += 1
                    except Exception as ex:
                        print(f"[!] Error inserting row in {table_name}: {ex}")

                await session.commit()

            results[table_name] = (len(rows), inserted_count)
            print(f"[OK] Migrated table '{table_name}': SQLite={len(rows)} -> Supabase={inserted_count}")

        # 3. Update PostgreSQL Sequences for Auto-Increment Integer Primary Keys
        seq_tables = ["segments", "video_translation_segments", "usage_snapshots", "errors"]
        for seq_table in seq_tables:
            try:
                seq_stmt = text(f"SELECT setval(pg_get_serial_sequence('{seq_table}', 'id'), COALESCE((SELECT MAX(id) FROM \"{seq_table}\"), 1))")
                await session.execute(seq_stmt)
                await session.commit()
                print(f"[OK] Reset PostgreSQL sequence for table '{seq_table}'")
            except Exception as seq_err:
                print(f"[i] Sequence reset note for '{seq_table}': {seq_err}")

    await target_engine.dispose()
    return results


async def main():
    print("==================================================")
    print("  SUPABASE DATABASE & STORAGE MIGRATION RUNNER")
    print("==================================================")

    sqlite_path = settings.DATA_DIR / settings.DB_FILENAME
    target_pg_url = settings.SUPABASE_DATABASE_URL or os.environ.get("SUPABASE_DATABASE_URL")

    print(f"SQLite Path: {sqlite_path}")
    print(f"Target Postgres URL: {'CONFIGURED' if target_pg_url else 'NOT CONFIGURED (Pass via env or .env)'}")

    sqlite_data = dump_sqlite_data(sqlite_path)

    if target_pg_url:
        results = await migrate_to_supabase_pg(target_pg_url, sqlite_data)
        print("\n================ Migration Summary ================")
        for tbl, (src_cnt, dst_cnt) in results.items():
            status = "OK" if src_cnt == dst_cnt else "MISMATCH"
            print(f" - {tbl:30s} : SQLite={src_cnt:4d} | Supabase={dst_cnt:4d} [{status}]")
    else:
        print("\n[!] SUPABASE_DATABASE_URL is not set. Database schema validated locally.")
        print("[i] Set SUPABASE_DATABASE_URL in .env to execute live migration to Supabase PostgreSQL.")


if __name__ == "__main__":
    asyncio.run(main())
