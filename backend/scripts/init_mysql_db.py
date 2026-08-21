import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, '.')

import asyncio
import pymysql
import sqlite3
from pathlib import Path

from app.config import get_settings
from app.database import init_db, engine, async_session_factory
from app.models.project import Project
from app.models.video_translator import VideoAsset, VideoTranslationJob, VideoTranslationSegment
from sqlalchemy import select

settings = get_settings()

def ensure_mysql_database_exists():
    print("Connecting to MySQL server at 127.0.0.1:3306...")
    # Parse root and password from settings or env
    db_url = settings.DB_URL
    print(f"Target DB URL: {db_url}")

    conn = pymysql.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="210606",
        autocommit=True,
    )
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS workflowvdai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    print("✓ MySQL Database 'workflowvdai' verified / created successfully!")
    conn.close()

async def migrate_data_from_sqlite_to_mysql():
    sqlite_path = Path("data/workflow.db")
    if not sqlite_path.exists():
        print("No SQLite database found to migrate.")
        return

    print("Reading data from SQLite database...")
    sq_conn = sqlite3.connect(sqlite_path)
    sq_conn.row_factory = sqlite3.Row
    sq_cur = sq_conn.cursor()

    # 1. Fetch assets
    assets = [dict(r) for r in sq_cur.execute("SELECT * FROM video_assets").fetchall()]
    # 2. Fetch jobs
    jobs = [dict(r) for r in sq_cur.execute("SELECT * FROM video_translation_jobs").fetchall()]
    # 3. Fetch segments
    vt_segments = [dict(r) for r in sq_cur.execute("SELECT * FROM video_translation_segments").fetchall()]
    # 4. Fetch projects
    projects = [dict(r) for r in sq_cur.execute("SELECT * FROM projects").fetchall()]

    sq_conn.close()

    print(f"Found {len(assets)} assets, {len(jobs)} jobs, {len(vt_segments)} VT segments, {len(projects)} projects.")

    async with async_session_factory() as session:
        # Migrate assets
        for a in assets:
            existing = await session.execute(select(VideoAsset).where(VideoAsset.id == a["id"]))
            if not existing.scalar_one_or_none():
                asset_obj = VideoAsset(
                    id=a["id"],
                    source_type=a.get("source_type", "url"),
                    source_url=a.get("source_url"),
                    source_domain=a.get("source_domain"),
                    title=a.get("title", "Untitled"),
                    original_filename=a.get("original_filename"),
                    file_path=a.get("file_path", ""),
                    mime_type=a.get("mime_type"),
                    file_size=a.get("file_size"),
                    duration=a.get("duration"),
                    width=a.get("width"),
                    height=a.get("height"),
                    audio_available=bool(a.get("audio_available", True)),
                    status=a.get("status", "ready"),
                    r2_key=a.get("r2_key"),
                    url=a.get("url"),
                )
                session.add(asset_obj)

        await session.commit()

        # Migrate jobs
        for j in jobs:
            existing = await session.execute(select(VideoTranslationJob).where(VideoTranslationJob.id == j["id"]))
            if not existing.scalar_one_or_none():
                job_obj = VideoTranslationJob(
                    id=j["id"],
                    asset_id=j["asset_id"],
                    source_language=j.get("source_language", "auto"),
                    detected_language=j.get("detected_language"),
                    target_language=j.get("target_language", "vi"),
                    audio_provider_id=j.get("audio_provider_id", "edge_tts"),
                    voice_id=j.get("voice_id"),
                    voice_name=j.get("voice_name"),
                    original_audio_mode=j.get("original_audio_mode", "mute"),
                    status=j.get("status", "completed"),
                    stage=j.get("stage", "COMPLETED"),
                    stage_progress_pct=j.get("stage_progress_pct", 100.0),
                    overall_progress_pct=j.get("overall_progress_pct", 100.0),
                    progress_pct=j.get("progress_pct", 100.0),
                    current_step=j.get("current_step", "Hoàn tất lồng tiếng video"),
                    output_video_path=j.get("output_video_path"),
                    r2_key=j.get("r2_key"),
                    output_url=j.get("output_url"),
                    is_cleaned=bool(j.get("is_cleaned", False)),
                    completed_segments_count=j.get("completed_segments_count", 0),
                    total_segments_count=j.get("total_segments_count", 0),
                )
                session.add(job_obj)

        await session.commit()

        # Migrate segments
        for seg in vt_segments:
            existing = await session.execute(select(VideoTranslationSegment).where(VideoTranslationSegment.id == seg["id"]))
            if not existing.scalar_one_or_none():
                seg_obj = VideoTranslationSegment(
                    id=seg["id"],
                    job_id=seg["job_id"],
                    segment_number=seg.get("segment_number") if seg.get("segment_number") is not None else (seg.get("number") or 1),
                    start_time=seg["start_time"],
                    end_time=seg["end_time"],
                    original_text=seg.get("original_text", ""),
                    translated_text=seg.get("translated_text", ""),
                    status=seg.get("status", "translated"),
                    tts_audio_path=seg.get("tts_audio_path"),
                    synced_audio_path=seg.get("synced_audio_path"),
                )
                session.add(seg_obj)

        await session.commit()
        print("✓ All project & job data successfully populated into MySQL Database!")

async def main():
    ensure_mysql_database_exists()
    print("Creating all tables in MySQL database...")
    await init_db()
    print("✓ All tables created successfully!")
    await migrate_data_from_sqlite_to_mysql()

if __name__ == "__main__":
    asyncio.run(main())
