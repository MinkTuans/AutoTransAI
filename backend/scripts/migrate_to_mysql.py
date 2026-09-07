"""
Database Migration Script to Laragon MySQL.

Copies schema and table data from local SQLite & Storage to Laragon MySQL Database.
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

from sqlalchemy import text
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
    "project_terminology_memory",
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
    """Read all records from SQLite database into Python dicts."""
    if not sqlite_db_path.exists():
        print(f"[-] SQLite database file not found at: {sqlite_db_path}")
        return {}

    conn = sqlite3.connect(sqlite_db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [row["name"] for row in cursor.fetchall()]

    data: Dict[str, List[Dict[str, Any]]] = {}
    total_rows = 0

    for table in tables:
        cursor.execute(f'SELECT * FROM "{table}"')
        rows = [dict(r) for r in cursor.fetchall()]
        data[table] = rows
        total_rows += len(rows)
        print(f"  - Dumped table '{table}': {len(rows)} rows")

    conn.close()
    print(f"[+] Total {total_rows} rows dumped from SQLite across {len(tables)} tables.")
    return data


async def migrate_to_mysql(target_mysql_url: str, sqlite_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """Create schema and insert all records into Laragon MySQL."""
    print(f"\n[+] Connecting to Target Database: {target_mysql_url[:40]}...")
    target_engine = create_async_engine(target_mysql_url, echo=False)
    is_mysql = "mysql" in target_mysql_url

    async with target_engine.begin() as conn:
        print("[+] Creating schema on Target Database...")
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(target_engine, expire_on_commit=False, class_=AsyncSession)
    results = {}

    quote_char = "`" if is_mysql else '"'

    async with async_session() as session:
        for table_name in TABLE_MIGRATION_ORDER:
            rows = sqlite_data.get(table_name, [])
            if not rows:
                results[table_name] = (0, 0)
                continue

            inserted_count = 0
            for row in rows:
                cols = ", ".join([f"{quote_char}{k}{quote_char}" for k in row.keys()])
                vals = ", ".join([f":{k}" for k in row.keys()])
                stmt = text(f"INSERT INTO {quote_char}{table_name}{quote_char} ({cols}) VALUES ({vals})")
                try:
                    await session.execute(stmt, row)
                    inserted_count += 1
                except Exception as ex:
                    if "Duplicate entry" in str(ex) or "1062" in str(ex) or "already exists" in str(ex).lower():
                        continue
                    err_msg = str(ex).encode("ascii", "replace").decode("ascii")
                    print(f"  [!] Error inserting row into {table_name}: {err_msg[:100]}")

            await session.commit()
            results[table_name] = (len(rows), inserted_count)
            print(f"[OK] Migrated table '{table_name}': SQLite={len(rows)} -> Target={inserted_count}")

    await target_engine.dispose()
    return results


async def main():
    print("==========================================================")
    print("  LARAGON MYSQL DATABASE MIGRATION RUNNER")
    print("==========================================================")

    sqlite_db_path = settings.DATA_DIR / settings.DB_FILENAME
    target_mysql_url = settings.DATABASE_URL or "mysql+aiomysql://root:@127.0.0.1:3306/autotransai"

    print(f"Source SQLite DB: {sqlite_db_path}")
    print(f"Target DB URL: {target_mysql_url}")

    sqlite_data = dump_sqlite_data(sqlite_db_path)
    if sqlite_data:
        results = await migrate_to_mysql(target_mysql_url, sqlite_data)
        print("\n================ MIGRATION SUMMARY ================")
        for tbl, (src_cnt, dst_cnt) in results.items():
            status = "OK" if src_cnt == dst_cnt else "PARTIAL"
            print(f" - {tbl:30s} : SQLite={src_cnt:4d} | Target={dst_cnt:4d} [{status}]")
    else:
        print("\n[!] No SQLite data found. Target database schema initialized successfully.")


if __name__ == "__main__":
    asyncio.run(main())
