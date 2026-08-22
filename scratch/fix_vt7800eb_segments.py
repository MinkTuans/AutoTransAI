import asyncio
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.database import async_session_factory
from app.models.video_translator import VideoTranslationJob, VideoTranslationSegment
from app.services.video_translator.translator_service import translate_transcript_segments
from sqlalchemy import select

async def fix_job_vt7800eb():
    async with async_session_factory() as session:
        job_res = await session.execute(
            select(VideoTranslationJob).where(VideoTranslationJob.id == "VT-7800EB")
        )
        job = job_res.scalar_one_or_none()
        if not job:
            print("Job VT-7800EB not found!")
            return

        print(f"Loaded Job {job.id}: SourceLang={job.source_language}, DetectedLang={job.detected_language}, TargetLang={job.target_language}, LLMProvider={job.llm_provider_id}")

        seg_res = await session.execute(
            select(VideoTranslationSegment)
            .where(VideoTranslationSegment.job_id == "VT-7800EB")
            .order_by(VideoTranslationSegment.segment_number)
        )
        db_segments = seg_res.scalars().all()
        print(f"Loaded {len(db_segments)} segments from database.")

        # Convert DB segments to dict format expected by translate_transcript_segments
        dict_segments = [
            {
                "number": s.segment_number,
                "start_time": s.start_time,
                "end_time": s.end_time,
                "text": s.original_text,
            }
            for s in db_segments
        ]

        print(f"Translating {len(dict_segments)} segments using new translate_transcript_segments pipeline...")
        translated_segs = await translate_transcript_segments(
            segments=dict_segments,
            source_language=job.detected_language or "Chinese",
            target_language=job.target_language or "vi",
            job_id=job.id,
            llm_provider_id="gemini",
            batch_size=30,
        )

        print("Updating database segment records with translated text...")
        for db_seg, trans_seg in zip(db_segments, translated_segs):
            db_seg.translated_text = trans_seg.get("translated_text", db_seg.original_text)

        await session.commit()
        print(f"✓ Successfully updated all {len(db_segments)} segments for Job VT-7800EB in MySQL database!")

        # Print first 10 segments as verification
        print("\nVerification - First 10 segments after translation fix:")
        for s in db_segments[:10]:
            print(f"  [Seg #{s.segment_number}] Gốc (Chinese): {s.original_text}")
            print(f"              Dịch (VI):      {s.translated_text}")

if __name__ == "__main__":
    asyncio.run(fix_job_vt7800eb())
