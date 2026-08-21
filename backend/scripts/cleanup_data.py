import sqlite3
import os
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = "data/workflow.db"
TARGET_JOB_ID = "VT-9B1B32"

def cleanup():
    print(f"=== STARTING PROJECT CLEANUP (KEEPING ONLY {TARGET_JOB_ID}) ===")
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Get asset_id for TARGET_JOB_ID
    target_job = cur.execute("SELECT * FROM video_translation_jobs WHERE id = ?", (TARGET_JOB_ID,)).fetchone()
    if not target_job:
        print(f"ERROR: Target job {TARGET_JOB_ID} not found in DB!")
        return
    
    target_asset_id = target_job["asset_id"]
    print(f"Target Job Found: {target_job['id']} | Asset ID: {target_asset_id}")

    # 1. Delete all non-target jobs from video_translation_jobs
    cur.execute("DELETE FROM video_translation_jobs WHERE id != ?", (TARGET_JOB_ID,))
    deleted_jobs = cur.rowcount
    print(f"Deleted {deleted_jobs} legacy jobs from video_translation_jobs DB table.")

    # 2. Delete all non-target segments from video_translation_segments
    cur.execute("DELETE FROM video_translation_segments WHERE job_id != ?", (TARGET_JOB_ID,))
    deleted_segments = cur.rowcount
    print(f"Deleted {deleted_segments} legacy segments from video_translation_segments DB table.")

    # 3. Delete all non-target assets from video_assets
    cur.execute("DELETE FROM video_assets WHERE id != ?", (target_asset_id,))
    deleted_assets = cur.rowcount
    print(f"Deleted {deleted_assets} legacy assets from video_assets DB table.")

    # 4. Clear all rows from projects table
    try:
        cur.execute("DELETE FROM projects")
        deleted_projects = cur.rowcount
        print(f"Deleted {deleted_projects} rows from projects DB table.")
    except Exception as e:
        print("Projects table deletion note:", e)

    # 5. Clear all rows from segments table (standard projects segments)
    try:
        cur.execute("DELETE FROM segments")
        deleted_std_segments = cur.rowcount
        print(f"Deleted {deleted_std_segments} rows from segments DB table.")
    except Exception as e:
        print("Segments table deletion note:", e)

    conn.commit()
    conn.close()

    # 6. Clean disk directories
    jobs_dir = "data/translator/jobs"
    if os.path.exists(jobs_dir):
        for item in os.listdir(jobs_dir):
            if item != TARGET_JOB_ID:
                path = os.path.join(jobs_dir, item)
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                print(f"Deleted disk job dir: {path}")

    assets_dir = "data/translator/assets"
    if os.path.exists(assets_dir):
        for item in os.listdir(assets_dir):
            if item != target_asset_id:
                path = os.path.join(assets_dir, item)
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                print(f"Deleted disk asset dir: {path}")

    projects_dir = "data/projects"
    if os.path.exists(projects_dir):
        for item in os.listdir(projects_dir):
            path = os.path.join(projects_dir, item)
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            print(f"Deleted disk project dir: {path}")

    print("\n✓ PROJECT CLEANUP COMPLETE!")

if __name__ == "__main__":
    cleanup()
