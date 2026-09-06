import asyncio
import sys
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.database import Base, engine
import app.models  # load all models

print("SQLAlchemy ORM Metadata Table Count:", len(Base.metadata.tables))
print("Tables in Metadata:")
for t in sorted(Base.metadata.tables.keys()):
    tbl = Base.metadata.tables[t]
    pks = [c.name for c in tbl.primary_key]
    fks = [f"{c.name}->{list(c.foreign_keys)[0].target_fullname}" for c in tbl.columns if c.foreign_keys]
    print(f" - {t}: PK={pks}, FKs={fks}, Columns={len(tbl.columns)}")
