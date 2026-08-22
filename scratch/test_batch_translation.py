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

async def test_batching():
    async with async_session_factory() as session:
        res = await session.execute(
            select(VideoTranslationSegment)
            .where(VideoTranslationSegment.job_id == "VT-7800EB")
            .order_by(VideoTranslationSegment.segment_number)
        )
        segments = res.scalars().all()
        test_texts = [s.original_text for s in segments]

    gemini = GeminiLLMProvider()

    print("\n=======================================================")
    print("TEST 1: Improved prompt with source/target lang specified, but 442 items all-at-once")
    print("=======================================================")
    prompt_all = (
        "Bạn là một dịch giả phim chuyên nghiệp.\n"
        "Nhiệm vụ: Dịch chính xác danh sách câu thoại bên dưới từ tiếng Trung (Chinese) sang tiếng Việt (Vietnamese).\n"
        "Yêu cầu tuyệt đối:\n"
        "- Phải dịch toàn bộ sang tiếng Việt tự nhiên, hợp ngữ cảnh lồng tiếng phim.\n"
        "- KHÔNG ĐƯỢC giữ nguyên tiếng Trung ngoại trừ tên riêng nếu thực sự cần thiết.\n"
        "- Trả về duy nhất một mảng JSON chứa các câu đã dịch sang tiếng Việt theo đúng thứ tự.\n\n"
        f"Input (Chinese):\n{json.dumps(test_texts, ensure_ascii=False)}"
    )
    resp_all = await gemini.generate_text(prompt_all)
    parsed_all = json.loads(re.sub(r"^```json\s*", "", re.sub(r"```$", "", resp_all, flags=re.MULTILINE).strip()))
    print("Sample 1-5 output all-at-once:")
    for orig, trans in zip(test_texts[:5], parsed_all[:5]):
        print(f"  Orig: {orig}\n  Trans: {trans}")

    print("\n=======================================================")
    print("TEST 2: Batched translation (Batch size = 25 segments)")
    print("=======================================================")
    batch_size = 25
    translated_all = []
    
    for i in range(0, len(test_texts), batch_size):
        batch = test_texts[i:i + batch_size]
        prompt_batch = (
            "Bạn là dịch giả phim chuyên nghiệp. Dịch danh sách các câu thoại sau từ tiếng Trung sang tiếng Việt.\n"
            "Yêu cầu:\n"
            "1. Dịch chuẩn xác sang tiếng Việt tự nhiên để lồng tiếng video.\n"
            "2. Tuyệt đối KHÔNG trả về nguyên văn tiếng Trung.\n"
            "3. Trả về đúng mảng JSON chứa kết quả dịch sang tiếng Việt.\n\n"
            f"Danh sách câu gốc (Chinese):\n{json.dumps(batch, ensure_ascii=False)}"
        )
        resp_b = await gemini.generate_text(prompt_batch)
        json_clean = re.sub(r"^```json\s*", "", resp_b, flags=re.MULTILINE)
        json_clean = re.sub(r"```$", "", json_clean, flags=re.MULTILINE).strip()
        parsed_b = json.loads(json_clean)
        translated_all.extend(parsed_b)
        print(f"Batch {i//batch_size + 1}/{(len(test_texts)+batch_size-1)//batch_size} done ({len(parsed_b)} items)")

    print(f"\nTotal batched translated: {len(translated_all)} / {len(test_texts)}")
    print("\nFirst 10 items in batched result:")
    for idx, (orig, trans) in enumerate(zip(test_texts[:10], translated_all[:10])):
        print(f"[{idx+1}] Orig: {orig}")
        print(f"     Trans: {trans}")

if __name__ == "__main__":
    asyncio.run(test_batching())
