import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

def main():
    db_path = 'backend/data/workflow.db'
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("=== SEARCHING FOR JOB VT-A49FCA ===")
    job = cursor.execute("SELECT * FROM video_translation_jobs WHERE id = ?", ("VT-A49FCA",)).fetchone()
    if job:
        print("JOB FOUND:")
        for k in job.keys():
            print(f"  {k}: {job[k]}")
    else:
        print("JOB VT-A49FCA NOT FOUND!")

    print("\n=== SEGMENTS FOR VT-A49FCA ===")
    segs = cursor.execute("SELECT * FROM video_translation_segments WHERE job_id = ? ORDER BY segment_number", ("VT-A49FCA",)).fetchall()
    print(f"Total segments count in table: {len(segs)}")
    for s in segs[:5]:
        print(f"  Seg #{s['segment_number']}: [{s['start_time']}s-{s['end_time']}s] orig='{s['original_text'][:30]}' trans='{s['translated_text'][:30]}'")

    print("\n=== MOST RECENT 5 JOBS ===")
    recent = cursor.execute("SELECT id, status, stage, overall_progress_pct, stage_progress_pct, current_step, updated_at FROM video_translation_jobs ORDER BY created_at DESC LIMIT 5").fetchall()
    for r in recent:
        print(dict(r))

if __name__ == "__main__":
    main()
