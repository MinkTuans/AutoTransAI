import asyncio
import json
import sys
import os

sys.path.insert(0, os.path.abspath("."))
sys.stdout.reconfigure(encoding='utf-8')

from app.database import async_session_factory
from app.api.routes.video_translator import get_translation_job

async def main():
    async with async_session_factory() as session:
        res = await get_translation_job("VT-A49FCA", session=session)
        print("=== STATUS API RESPONSE FOR VT-A49FCA ===")
        print(json.dumps(res, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())
