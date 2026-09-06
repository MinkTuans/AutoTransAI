import shutil
from pathlib import Path

db_src = Path("data/workflow.db")
backup_dir = Path("data/backup")
backup_dir.mkdir(parents=True, exist_ok=True)
backup_dest = backup_dir / "workflow_before_supabase_migration.db"

if db_src.exists():
    shutil.copy2(db_src, backup_dest)
    print(f"[OK] Backed up SQLite DB ({db_src.stat().st_size} bytes) to {backup_dest}")
else:
    print(f"[!] SQLite DB file not found at {db_src}")
