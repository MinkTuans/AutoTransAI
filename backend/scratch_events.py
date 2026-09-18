import sys
import asyncio
from sqlalchemy import select
from pathlib import Path
sys.path.append('c:/Hack/AutoTransAI/backend')

from app.database import async_session_factory
from app.models.workflow_engine import VideoTranslationJobEvent

async def run():
    async with async_session_factory() as db:
        events = (await db.execute(select(VideoTranslationJobEvent).order_by(VideoTranslationJobEvent.timestamp.desc()).limit(100))).scalars().all()
        for e in events:
            if "Parse" in str(e.message) or "STT" in e.stage:
                print(f"[{e.timestamp}] {e.stage}: {e.message}")

if __name__ == "__main__":
    asyncio.run(run())
