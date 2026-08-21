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
    update_job_segments,
    render_final_translated_video,
    CreateJobRequest,
    UpdateSegmentsRequest,
    SegmentUpdateItem,
)

class DummyBackgroundTasks:
    def __init__(self):
        self.tasks = []
    def add_task(self, func, *args, **kwargs):
        task = asyncio.create_task(func(*args, **kwargs))
        self.tasks.append(task)

async def main():
    print("=== STARTING FULL END-TO-END PIPELINE (PHASE 1 + PHASE 2) TEST ===")
    asset_id = "12f0bd95"
    
    async with async_session_factory() as session:
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

        bg_tasks = DummyBackgroundTasks()
        res_start = await start_translation_pipeline(job_id, background_tasks=bg_tasks, session=session)
        print(f"2. Phase 1 Pipeline Started: {res_start}")

    # 1. Poll Phase 1
    print("3. Waiting for Phase 1 (SEGMENT_EDITING) to complete...")
    start_p1 = time.time()
    last_p1_stage = None

    while time.time() - start_p1 < 120:
        await asyncio.sleep(2.0)
        async with async_session_factory() as session:
            status_res = await get_translation_job(job_id, session=session)
            data = status_res["data"]
            stage = data["stage"]
            status = data["status"]

            if stage != last_p1_stage:
                last_p1_stage = stage
                print(f"   [{time.strftime('%H:%M:%S')}] Phase 1 Stage: {stage:<15} | Status: {status:<15} | Progress: {data['overall_progress_pct']}%")

            if status == "segment_editing":
                print(f"✓ Phase 1 Complete! Total segments loaded: {len(data['segments'])}")
                break

    # 2. Update Segment #1
    async with async_session_factory() as session:
        status_res = await get_translation_job(job_id, session=session)
        segments = status_res["data"]["segments"]
        if not segments:
            print("❌ ERROR: No segments found!")
            sys.exit(1)

        seg_1 = segments[0]
        new_text = seg_1["translated_text"] + " (Đã chỉnh sửa bởi User E2E Test)"
        update_req = UpdateSegmentsRequest(segments=[SegmentUpdateItem(id=seg_1["id"], translated_text=new_text)])
        res_update = await update_job_segments(job_id, update_req, session=session)
        print(f"4. Updated Segment #{seg_1['number']} via API: {res_update}")

        # 3. Start Phase 2 (Render)
        bg_tasks_p2 = DummyBackgroundTasks()
        res_render = await render_final_translated_video(job_id, background_tasks=bg_tasks_p2, session=session)
        print(f"5. Phase 2 Render Started: {res_render}")

    # 4. Await Phase 2 Background Task to finish completely
    print("6. Executing Phase 2 Render Task to completion...")
    for t in bg_tasks_p2.tasks:
        await t

    # 5. Final Status Verification
    async with async_session_factory() as session:
        status_res = await get_translation_job(job_id, session=session)
        data = status_res["data"]
        print("\n=== E2E FINAL JOB SNAPSHOT ===")
        print(json.dumps(data, indent=2, ensure_ascii=False))

        output_path = data.get("output_video_path")
        if output_path and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            print(f"\n🎉 E2E TEST PASSED SUCCESSFULY!")
            print(f"   Output Video Path: {output_path}")
            print(f"   File Size: {round(os.path.getsize(output_path) / (1024*1024), 2)} MB")
        else:
            print(f"\n❌ E2E TEST FAILED: Output video file missing or empty! Path: {output_path}")

if __name__ == "__main__":
    asyncio.run(main())
