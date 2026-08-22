"""
Standalone CLI script to sync database schema across SQLite and MySQL/MariaDB.

Executes dialect-agnostic column inspection against active DATABASE_URL
and automatically creates any missing columns declared in SQLAlchemy ORM models.
"""

from __future__ import annotations

import asyncio
import sys

# Ensure backend root is on Python path
from pathlib import Path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))
sys.stdout.reconfigure(encoding='utf-8')

from app.config import get_settings
from app.database import init_db, engine
from sqlalchemy import inspect, text

settings = get_settings()


async def run_sync():
    print(f"=== STARTING SCHEMA SYNC FOR {settings.DB_URL} ===")
    await init_db()
    
    # Inspect final schema result
    async with engine.begin() as conn:
        def _inspect(sync_conn):
            inspector = inspect(sync_conn)
            tables = inspector.get_table_names()
            print(f"✓ Found {len(tables)} tables in database.")
            for t in sorted(tables):
                cols = [c["name"] for c in inspector.get_columns(t)]
                print(f"  - {t} ({len(cols)} columns): {cols}")

        await conn.run_sync(_inspect)

    print("✓ SCHEMA SYNC COMPLETE!")


if __name__ == "__main__":
    asyncio.run(run_sync())
