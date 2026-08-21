import asyncio
import json
import sys
import os
import time

sys.path.insert(0, os.path.abspath("."))
sys.stdout.reconfigure(encoding='utf-8')

from app.database import async_session_factory
from app.api.routes.video_translator import (
    render_final_translated_video,
    get_translation_job,
)

class DummyBackgroundTasks:
    def __init__(self):
        self.tasks = []
    def add_task(self, func, *args, **kwargs):
        task = asyncio.create_task(func(*args, **kwargs))
        self.tasks.append(task)

async def main():
    job_id = "VT-848257"
    print(f"=== DIRECT PHASE 2 TEST ON JOB {job_id} ===")
    
    bg_tasks = DummyBackgroundTasks()
    async with async_session_factory() as session:
        res = await render_final_translated_video(job_id, background_tasks=bg_tasks, session=session)
        print(f"Render API Response: {res}")

    start_time = time.time()
    while time.time() - start_time < 300:
        await asyncio.sleep(3.0)
        async with async_session_factory() as session:
            status_res = await get_translation_job(job_id, session=session)
            data = status_res["data"]
            stage = data["stage"]
            status = data["status"]
            overall_pct = data["overall_progress_pct"]
            stage_pct = data["stage_progress_pct"]
            step = data["current_step"]

            print(f"[{time.strftime('%H:%M:%S')}] Stage: {stage:<15} | Status: {status:<15} | Overall: {overall_pct:>5.1f}% | StagePct: {stage_pct:>5.1f}% | Step: {step}")

            if status in ["completed", "failed", "cancelled"]:
                print("\n=== FINAL RENDER SNAPSHOT ===")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                break

    # Keep loop running so background heartbeat/render task finishes
    for task in bg_tasks.tasks:
        await task

if __name__ == "__main__":
    asyncio.run(main())
