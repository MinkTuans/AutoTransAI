import sqlite3
import os

db_path = "data/workflow.db"
if not os.path.exists(db_path):
    print("DB file does not exist at", db_path)
else:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    tables = [t[0] for t in c.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()]
    print("Found tables:", len(tables))
    for t in tables:
        count = c.execute(f"SELECT count(*) FROM `{t}`").fetchone()[0]
        schema = c.execute(f"PRAGMA table_info(`{t}`)").fetchall()
        cols = [col[1] for col in schema]
        print(f"Table: {t} | Rows: {count} | Columns: {len(cols)} ({', '.join(cols[:5])}...)")
    conn.close()
