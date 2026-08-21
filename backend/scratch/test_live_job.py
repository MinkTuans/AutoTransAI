import asyncio
import json
import sys
import os
import time

sys.path.insert(0, os.path.abspath("."))
sys.stdout.reconfigure(encoding='utf-8')

from app.database import async_session_factory
from app.api.routes.video_translator import (
    create_translation_job,
    start_translation_pipeline,
    get_translation_job,
    CreateJobRequest,
)

class DummyBackgroundTasks:
    def __init__(self):
        self.tasks = []
    def add_task(self, func, *args, **kwargs):
        task = asyncio.create_task(func(*args, **kwargs))
        self.tasks.append(task)

async def main():
    print("=== STARTING LIVE END-TO-END PIPELINE TEST FOR 第一集怪异诡谲.mp4 ===")
    asset_id = "12f0bd95"
    
    async with async_session_factory() as session:
        # Create Job
        req = CreateJobRequest(
            asset_id=asset_id,
            source_language="auto",
            target_language="vi",
            audio_provider_id="edge_tts",
            voice_id="vi-VN-HoaiMyNeural",
            original_audio_mode="duck"
        )
        res_create = await create_translation_job(req, session=session)
        job_id = res_create["data"]["job_id"]
        print(f"1. Job Created: {job_id}")

        # Start Job Pipeline
        bg_tasks = DummyBackgroundTasks()
        res_start = await start_translation_pipeline(job_id, background_tasks=bg_tasks, session=session)
        print(f"2. Job Pipeline Started: {res_start}")

    # Poll Job Status until Phase 1 (SEGMENT_EDITING) completes
    print("3. Polling Job Status...")
    start_time = time.time()
    last_stage = None

    while time.time() - start_time < 120:
        await asyncio.sleep(2.0)
        async with async_session_factory() as session:
            status_res = await get_translation_job(job_id, session=session)
            data = status_res["data"]
            stage = data["stage"]
            status = data["status"]
            overall_pct = data["overall_progress_pct"]
            stage_pct = data["stage_progress_pct"]
            hb_active = data["heartbeat"]["active"]
            proc_status = data["process"]["status"]
            stt_status = data["stt"]["status"]
            trans_status = data["translation"]["status"]
            seg_count = len(data["segments"])

            if stage != last_stage or time.time() - start_time % 10 < 2:
                last_stage = stage
                print(
                    f"[{time.strftime('%H:%M:%S')}] Job: {job_id} | Stage: {stage:<15} | Status: {status:<15} | "
                    f"Overall: {overall_pct:>5.1f}% | StagePct: {stage_pct:>5.1f}% | HB Active: {str(hb_active):<5} | "
                    f"FFmpeg: {proc_status:<9} | STT: {stt_status:<9} | Trans: {trans_status:<9} | Segments: {seg_count}"
                )

            if status in ["segment_editing", "completed", "failed", "cancelled"]:
                print("\n=== FINAL TEST SNAPSHOT ===")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                break

    # Verify background task finished without unhandled exceptions
    for task in bg_tasks.tasks:
        if not task.done():
            await task

if __name__ == "__main__":
    asyncio.run(main())
