import asyncio
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
os.environ['DATABASE_URL']='mysql+aiomysql://root:210606@127.0.0.1:3306/autotransai'

from app.database import async_session_factory
from sqlalchemy import text

async def main():
    async with async_session_factory() as db:
        res = await db.execute(text("SELECT segment_number, speaker_id, voice_id, start_time, end_time, original_start, original_end, scheduled_start, scheduled_end, tts_duration, schedule_action, overlap_with FROM video_translation_segments WHERE job_id = 'd9de33ee' ORDER BY segment_number"))
        rows = res.fetchall()
        for r in rows:
            print(r)

asyncio.run(main())
