import asyncio
import json
import sys
import os
import time

sys.path.insert(0, os.path.abspath("."))
sys.stdout.reconfigure(encoding='utf-8')

from app.database import async_session_factory
from app.api.routes.video_translator import get_translation_job

async def main():
    job_id = "VT-848257"
    print(f"=== MONITORING JOB {job_id} UNTIL COMPLETED ===")
    start_time = time.time()
    last_stage = None

    while time.time() - start_time < 180:
        await asyncio.sleep(3.0)
        async with async_session_factory() as session:
            status_res = await get_translation_job(job_id, session=session)
            data = status_res["data"]
            stage = data["stage"]
            status = data["status"]
            overall_pct = data["overall_progress_pct"]
            stage_pct = data["stage_progress_pct"]
            current_step = data["current_step"]
            proc_status = data["process"]["status"]

            print(f"[{time.strftime('%H:%M:%S')}] Job: {job_id} | Stage: {stage:<15} | Status: {status:<15} | Overall: {overall_pct:>5.1f}% | StagePct: {stage_pct:>5.1f}% | Step: {current_step}")

            if status in ["completed", "failed", "cancelled"]:
                print("\n=== FINAL RENDER SNAPSHOT ===")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                break

if __name__ == "__main__":
    asyncio.run(main())
