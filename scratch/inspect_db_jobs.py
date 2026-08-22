import asyncio
import sys
import os
import json

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.database import async_session_factory
from app.models.video_translator import VideoTranslationJob, VideoTranslationSegment
from sqlalchemy import select

async def inspect_jobs():
    async with async_session_factory() as session:
        result = await session.execute(
            select(VideoTranslationJob).order_by(VideoTranslationJob.created_at.desc()).limit(10)
        )
        jobs = result.scalars().all()
        print(f"Found {len(jobs)} recent jobs in database:")
        for j in jobs:
            print(f"\n--- Job ID: {j.id} ---")
            print(f"Status: {j.status}, Stage: {j.stage}, SourceLang: {j.source_language}, DetectedLang: {j.detected_language}, TargetLang: {j.target_language}, LLMProvider: {j.llm_provider_id}")
            
            # Fetch segments
            seg_res = await session.execute(
                select(VideoTranslationSegment).where(VideoTranslationSegment.job_id == j.id).order_by(VideoTranslationSegment.segment_number)
            )
            segments = seg_res.scalars().all()
            print(f"Total Segments: {len(segments)}")
            for s in segments[:5]:
                print(f"  Seg #{s.segment_number} ({s.start_time:.1f}s - {s.end_time:.1f}s):")
                print(f"    Original  : {s.original_text}")
                print(f"    Translated: {s.translated_text}")

if __name__ == "__main__":
    asyncio.run(inspect_jobs())
