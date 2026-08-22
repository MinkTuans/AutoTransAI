import asyncio
import sys
import os
import json

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.config import get_settings
from app.database import async_session_factory
from app.models.video_translator import VideoTranslationJob
from app.providers.registry import get_registry
from app.services.video_translator.translator_service import translate_transcript_segments
from sqlalchemy import select

async def test_routing():
    print("=== END-TO-END PROVIDER ROUTING AUDIT ===")
    settings = get_settings()
    print(f"GEMINI_API_KEY configured: {bool(settings.GEMINI_API_KEY)}")
    print(f"OPENAI_API_KEY configured: {bool(settings.OPENAI_API_KEY)}")
    
    registry = get_registry()
    gemini = registry.get_llm("gemini")
    openai = registry.get_llm("openai")
    print(f"Registry get_llm('gemini'): {gemini.provider_name if gemini else None}")
    print(f"Registry get_llm('openai'): {openai.provider_name if openai else None}")

    # Check recent DB jobs
    async with async_session_factory() as session:
        res = await session.execute(
            select(VideoTranslationJob).order_by(VideoTranslationJob.created_at.desc()).limit(5)
        )
        jobs = res.scalars().all()
        print(f"\nRecent Jobs in Database ({len(jobs)}):")
        for j in jobs:
            print(f"  Job {j.id}: llm_provider_id='{j.llm_provider_id}', status='{j.status}', stage='{j.stage}'")

    test_segments = [
        {"number": 1, "start_time": 0.0, "end_time": 4.0, "text": "你好，欢迎来到这个视频。"}
    ]

    print("\n--- Testing translate_transcript_segments with configured llm_provider_id='gemini' ---")
    try:
        segs = await translate_transcript_segments(
            segments=[s.copy() for s in test_segments],
            source_language="Chinese",
            target_language="vi",
            job_id="TEST-ROUTING-GEMINI",
            llm_provider_id="gemini"
        )
        print("RESULT:")
        for s in segs:
            print(f"  Orig: {s['text']}")
            print(f"  Trans: {s.get('translated_text')}")
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_routing())
