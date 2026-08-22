import asyncio
import sys
import os
import json
import re

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.database import async_session_factory
from app.models.video_translator import VideoTranslationSegment
from app.providers.llm.gemini_provider import GeminiLLMProvider
from sqlalchemy import select

async def test_job_segments():
    async with async_session_factory() as session:
        res = await session.execute(
            select(VideoTranslationSegment)
            .where(VideoTranslationSegment.job_id == "VT-7800EB")
            .order_by(VideoTranslationSegment.segment_number)
        )
        segments = res.scalars().all()
        print(f"Loaded {len(segments)} segments for VT-7800EB")
        
        test_texts = [s.original_text for s in segments]

    gemini = GeminiLLMProvider()
    prompt = (
        "Hãy dịch các câu văn sau sang Tiếng Việt. "
        "Giữ nguyên thứ tự câu và phong cách tự nhiên để lồng tiếng video. "
        "Trả về một mảng JSON thuần túy (không markdown) chứa các chuỗi dịch tương ứng:\n"
        f"{json.dumps(test_texts, ensure_ascii=False)}"
    )
    
    print(f"Prompt length: {len(prompt)} chars, sending {len(test_texts)} sentences to Gemini...")
    
    try:
        raw_resp = await gemini.generate_text(prompt)
        print(f"\nRAW RESP (first 500 chars):\n{raw_resp[:500]}\n...")
        print(f"RAW RESP (last 500 chars):\n...{raw_resp[-500:]}\n")
        
        json_str = re.sub(r"^```json\s*", "", raw_resp, flags=re.MULTILINE)
        json_str = re.sub(r"```$", "", json_str, flags=re.MULTILINE).strip()
        parsed = json.loads(json_str)
        print(f"Parsed type: {type(parsed)}, length: {len(parsed) if isinstance(parsed, list) else 'N/A'}")
        
        if isinstance(parsed, list):
            print("\nFirst 10 items in parsed result:")
            for i, (orig, trans) in enumerate(zip(test_texts[:10], parsed[:10])):
                print(f"[{i+1}] Orig: {orig}")
                print(f"     Trans: {trans}")
    except Exception as e:
        print(f"Error testing: {e}")

if __name__ == "__main__":
    asyncio.run(test_job_segments())
