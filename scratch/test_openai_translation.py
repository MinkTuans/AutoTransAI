import asyncio
import sys
import os
import json
import re

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.config import get_settings
from app.providers.llm.openai_provider import OpenAILLMProvider
from app.services.video_translator.translator_service import translate_transcript_segments

async def test_openai_direct():
    settings = get_settings()
    print(f"=== OPENAI TRANSLATION DIRECT TEST ===")
    print(f"OPENAI_API_KEY present: {bool(settings.OPENAI_API_KEY)}")
    if settings.OPENAI_API_KEY:
        print(f"Key preview: {settings.OPENAI_API_KEY[:7]}...{settings.OPENAI_API_KEY[-4:]}")
    else:
        print("WARNING: OPENAI_API_KEY is EMPTY in .env!")

    test_segments = [
        {"number": 1, "start_time": 0.0, "end_time": 4.5, "text": "查理家，你这个巴巴尔，我是不会放过你的。"},
        {"number": 2, "start_time": 4.5, "end_time": 8.0, "text": "布莱克王,他怎么会出现在这里?"},
        {"number": 3, "start_time": 8.0, "end_time": 11.0, "text": "赛文,今天你的命就留在这吧."},
    ]

    print("\n--- 1. Testing OpenAILLMProvider generate_text directly ---")
    openai_prov = OpenAILLMProvider()
    
    texts_to_translate = [s["text"] for s in test_segments]
    
    source_lang_name = "Tiếng Trung"
    target_lang_name = "Tiếng Việt"
    
    prompt = (
        "Bạn là một dịch giả phim chuyên nghiệp.\n"
        f"Nhiệm vụ: Dịch chính xác danh sách câu thoại bên dưới từ {source_lang_name} sang {target_lang_name}.\n"
        "Yêu cầu bắt buộc:\n"
        f"1. Phải dịch TOÀN BỘ nội dung sang {target_lang_name} tự nhiên, hợp ngữ cảnh lồng tiếng video.\n"
        f"2. Tuyệt đối KHÔNG ĐƯỢC trả lại nguyên văn {source_lang_name} hay giữ lại văn bản chưa dịch (trừ tên riêng nếu có).\n"
        "3. Trả về duy nhất một mảng JSON thuần túy (không markdown, không giải thích) chứa các chuỗi dịch tương ứng theo đúng thứ tự.\n\n"
        f"Danh sách câu thoại gốc ({source_lang_name}):\n"
        f"{json.dumps(texts_to_translate, ensure_ascii=False)}"
    )

    print(f"[TRANSLATION_REQUEST]")
    print(f"provider=OpenAI")
    print(f"source_language=Chinese ({source_lang_name})")
    print(f"target_language=Vietnamese ({target_lang_name})")
    print(f"source_text_length={len(prompt)} chars")
    print(f"PROMPT SENT:\n{prompt}\n")

    try:
        raw_resp = await openai_prov.generate_text(prompt)
        print(f"RAW RESPONSE FROM OPENAI:\n{raw_resp}\n")
    except Exception as e:
        print(f"RAW OPENAI API EXCEPTION: {type(e).__name__}: {str(e)}\n")

    print("\n--- 2. Testing translate_transcript_segments with OpenAI provider ---")
    res_segs = await translate_transcript_segments(
        segments=[s.copy() for s in test_segments],
        source_language="Chinese",
        target_language="vi",
        job_id="TEST-JOB-OPENAI",
        llm_provider_id="openai"
    )
    for s in res_segs:
        print(f"[{s['number']}] Orig: {s['text']}")
        print(f"     Trans: {s.get('translated_text')}")

if __name__ == "__main__":
    asyncio.run(test_openai_direct())
