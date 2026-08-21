import sqlite3
import os

db_path = "data/workflow.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

tables = cur.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
print("=== DB TABLES ===")
for t in tables:
    name = t['name']
    count = cur.execute(f"SELECT count(*) FROM {name}").fetchone()[0]
    print(f"Table '{name}': {count} rows")

print("\n=== JOBS IN DB ===")
jobs = cur.execute("SELECT id, asset_id, status, stage, output_video_path FROM video_translation_jobs").fetchall()
for j in jobs:
    print(dict(j))

print("\n=== ASSETS IN DB ===")
assets = cur.execute("SELECT id, title, file_path FROM video_assets").fetchall()
for a in assets:
    print(dict(a))

print("\n=== PROJECTS IN DB ===")
try:
    projects = cur.execute("SELECT id, title, status FROM projects").fetchall()
    for p in projects:
        print(dict(p))
except Exception as e:
    print("No projects table or error:", e)

print("\n=== JOBS ON DISK ===")
jobs_dir = "data/translator/jobs"
if os.path.exists(jobs_dir):
    print(os.listdir(jobs_dir))

print("\n=== ASSETS ON DISK ===")
assets_dir = "data/translator/assets"
if os.path.exists(assets_dir):
    print(os.listdir(assets_dir))

print("\n=== PROJECTS ON DISK ===")
projects_dir = "data/projects"
if os.path.exists(projects_dir):
    print(os.listdir(projects_dir))
