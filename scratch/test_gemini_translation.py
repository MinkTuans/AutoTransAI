import asyncio
import json
import sys
import os
import re

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.config import get_settings
from app.providers.llm.gemini_provider import GeminiLLMProvider
from app.services.video_translator.translator_service import translate_transcript_segments

async def test_gemini_direct():
    settings = get_settings()
    print(f"GEMINI_API_KEY present: {bool(settings.GEMINI_API_KEY)}")
    
    test_segments = [
        {"number": 1, "start_time": 0.0, "end_time": 4.5, "text": "布莱克王,他怎么会出现在这里?"},
        {"number": 2, "start_time": 4.5, "end_time": 8.0, "text": "赛文,今天你的命就留在这吧."},
        {"number": 3, "start_time": 8.0, "end_time": 11.0, "text": "可恶,大意了没闪."},
        {"number": 4, "start_time": 11.0, "end_time": 14.0, "text": "布莱克王,给我干掉他."},
        {"number": 5, "start_time": 14.0, "end_time": 17.0, "text": "我是赛文奥特曼,"},
        {"number": 6, "start_time": 17.0, "end_time": 20.0, "text": "是奥特兄弟里的议员."},
        {"number": 7, "start_time": 20.0, "end_time": 23.0, "text": "我不是恒星观测员340号,"},
    ]

    print("\n--- 1. Testing GeminiLLMProvider generate_text directly ---")
    gemini = GeminiLLMProvider()
    
    texts_to_translate = [s["text"] for s in test_segments]
    
    lang_names = {
        "vi": "Tiếng Việt",
        "en": "English",
        "ja": "Tiếng Nhật",
        "ko": "Tiếng Hàn",
        "zh": "Tiếng Trung",
    }
    target_lang_name = lang_names.get("vi", "vi")
    
    prompt = (
        f"Hãy dịch các câu văn sau sang {target_lang_name}. "
        "Giữ nguyên thứ tự câu và phong cách tự nhiên để lồng tiếng video. "
        "Trả về một mảng JSON thuần túy (không markdown) chứa các chuỗi dịch tương ứng:\n"
        f"{json.dumps(texts_to_translate, ensure_ascii=False)}"
    )

    print(f"PROMPT SENT:\n{prompt}\n")

    try:
        resp = await gemini.generate_text(prompt)
        print(f"RAW RESP FROM GEMINI:\n{resp}\n")
        
        json_str = re.sub(r"^```json\s*", "", resp, flags=re.MULTILINE)
        json_str = re.sub(r"```$", "", json_str, flags=re.MULTILINE).strip()
        translated_list = json.loads(json_str)
        print(f"PARSED JSON ({len(translated_list)} items):\n{json.dumps(translated_list, ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"ERROR IN GENERATE_TEXT: {e}")

    print("\n--- 2. Testing translate_transcript_segments with Gemini ---")
    res_segs = await translate_transcript_segments(
        segments=[s.copy() for s in test_segments],
        source_language="Chinese",
        target_language="vi",
        job_id="TEST-JOB",
        llm_provider_id="gemini"
    )
    for s in res_segs:
        print(f"[{s['number']}] Source: {s['text']} -> Trans: {s.get('translated_text')}")

if __name__ == "__main__":
    asyncio.run(test_gemini_direct())
