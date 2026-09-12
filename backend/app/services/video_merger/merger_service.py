"""
Video Merger Service.

Handles video preflight validation, thumbnail extraction, FFmpeg concat & normalization execution,
and background progress tracking for VideoMergeJob execution.
"""

from __future__ import annotations

import os
import shutil
import asyncio
import json
import uuid
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

from sqlalchemy import select, update
from app.config import get_settings
from app.core import get_logger
from app.database import async_session_factory
from app.models.video_merger import VideoMergeJob, MergeJobStatus
from app.media.ffprobe import (
    probe_media_info_async,
    get_video_metadata_async,
    is_ffmpeg_installed,
    get_ffmpeg_executable,
)
from app.media.ffmpeg_process import run_ffmpeg_with_progress_async, FFmpegExecutionError
from app.services.storage_service import LocalStorageService
from app.core.security import safe_subprocess_run_async

logger = get_logger(__name__)
settings = get_settings()


class VideoMergerService:
    """Core domain service orchestrating Video Merger operations."""

    @staticmethod
    def get_merger_storage_dir() -> Path:
        """Get root local directory for Video Merger storage."""
        root = getattr(settings, "STORAGE_ROOT", None) or (settings.DATA_DIR / "storage")
        p = root / "merger"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @classmethod
    async def extract_thumbnail_async(cls, video_path: Path, thumb_filename: str) -> Optional[str]:
        """Extract a single frame thumbnail from a video file using FFmpeg."""
        video_path = Path(video_path)
        if not video_path.exists() or not is_ffmpeg_installed():
            return None

        thumbs_dir = cls.get_merger_storage_dir() / "thumbnails"
        thumbs_dir.mkdir(parents=True, exist_ok=True)
        thumb_path = thumbs_dir / thumb_filename

        try:
            ffmpeg_bin = get_ffmpeg_executable()
            res = await safe_subprocess_run_async(
                [
                    ffmpeg_bin, "-y",
                    "-ss", "00:00:01",
                    "-i", str(video_path),
                    "-vframes", "1",
                    "-q:v", "2",
                    str(thumb_path),
                ],
                timeout=15,
                check=False,
            )
            if res.returncode == 0 and thumb_path.exists() and thumb_path.stat().st_size > 0:
                rel_key = f"merger/thumbnails/{thumb_filename}"
                return LocalStorageService.get_url(rel_key)
        except Exception as e:
            logger.warning("Thumbnail extraction failed", error=str(e), path=str(video_path))

        return None

    @classmethod
    async def validate_input_videos(
        cls, video_items: List[Dict[str, Any]]
    ) -> Tuple[bool, str, List[Dict[str, Any]]]:
        """
        Preflight validation for input videos.
        Checks existence, video streams, audio streams, codecs, duration, dimensions.
        """
        validated_items: List[Dict[str, Any]] = []

        if not video_items or len(video_items) == 0:
            return False, "❌ Không có video nào được chọn để ghép.", []

        for idx, item in enumerate(video_items):
            file_path_str = item.get("file_path")
            if not file_path_str:
                return False, f"❌ Video #{idx + 1} ({item.get('original_filename', 'N/A')}) thiếu đường dẫn file.", []

            fpath = Path(file_path_str)
            if not fpath.exists():
                return False, f"❌ File video #{idx + 1} không tồn tại trên hệ thống: {fpath.name}", []

            if not fpath.is_file() or fpath.stat().st_size == 0:
                return False, f"❌ File video #{idx + 1} bị rỗng hoặc không thể đọc được: {fpath.name}", []

            try:
                probe_info = await probe_media_info_async(fpath)
            except Exception as ex:
                return False, f"❌ Không thể đọc cấu trúc media của video #{idx + 1} ({fpath.name}): {str(ex)}", []

            streams = probe_info.get("streams", [])
            fmt = probe_info.get("format", {})

            v_stream = next((s for s in streams if s.get("codec_type") == "video"), None)
            if not v_stream:
                return False, f"❌ File #{idx + 1} ({fpath.name}) không chứa luồng dữ liệu Video (video stream).", []

            a_stream = next((s for s in streams if s.get("codec_type") == "audio"), None)

            # Extract stream metadata
            width = int(v_stream.get("width", 0))
            height = int(v_stream.get("height", 0))
            duration = float(fmt.get("duration", 0.0))
            if duration <= 0:
                duration = float(v_stream.get("duration", 0.0))

            if duration <= 0:
                return False, f"❌ Video #{idx + 1} ({fpath.name}) có thời lượng không hợp lệ (duration <= 0).", []

            v_codec = v_stream.get("codec_name", "unknown")
            a_codec = a_stream.get("codec_name", "none") if a_stream else "none"

            # Parse frame rate
            fps = 30.0
            r_fps = v_stream.get("r_frame_rate", "30/1")
            if "/" in r_fps:
                try:
                    num, den = r_fps.split("/")
                    if float(den) > 0:
                        fps = round(float(num) / float(den), 2)
                except Exception:
                    pass

            item_data = dict(item)
            item_data.update(
                {
                    "file_path": str(fpath.resolve()),
                    "duration": round(duration, 3),
                    "width": width,
                    "height": height,
                    "fps": fps,
                    "video_codec": v_codec,
                    "audio_codec": a_codec,
                    "has_audio": bool(a_stream),
                    "file_size": fpath.stat().st_size,
                }
            )
            validated_items.append(item_data)

        return True, "OK", validated_items

    @classmethod
    async def execute_merge_job(
        cls, job_id: str, input_items: List[Dict[str, Any]], custom_title: Optional[str] = None
    ) -> None:
        """
        Background task worker to merge multiple video items into a single output video.
        Uses real-time FFmpeg progress tracking and updates DB state cleanly.
        """
        logger.info("Starting Video Merge Job background task", job_id=job_id, input_count=len(input_items))

        async with async_session_factory() as session:
            # Update status to PREPARING
            await session.execute(
                update(VideoMergeJob)
                .where(VideoMergeJob.id == job_id)
                .values(status=MergeJobStatus.PREPARING.value, progress=2.0)
            )
            await session.commit()

        # Step 1: Preflight Validation
        is_valid, err_msg, validated_items = await cls.validate_input_videos(input_items)
        if not is_valid:
            logger.error("Preflight validation failed for merge job", job_id=job_id, error=err_msg)
            async with async_session_factory() as session:
                await session.execute(
                    update(VideoMergeJob)
                    .where(VideoMergeJob.id == job_id)
                    .values(
                        status=MergeJobStatus.FAILED.value,
                        error_message=err_msg,
                        progress=0.0,
                    )
                )
                await session.commit()
            return

        total_duration = sum(item["duration"] for item in validated_items)
        logger.info("Preflight validation passed", job_id=job_id, total_duration=total_duration)

        # Output preparation
        job_dir = cls.get_merger_storage_dir() / "outputs" / job_id
        job_dir.mkdir(parents=True, exist_ok=True)

        output_filename = f"merged_{job_id[:8]}.mp4"
        output_path = job_dir / output_filename
        tmp_dir = cls.get_merger_storage_dir() / "tmp" / job_id
        tmp_dir.mkdir(parents=True, exist_ok=True)

        async with async_session_factory() as session:
            await session.execute(
                update(VideoMergeJob)
                .where(VideoMergeJob.id == job_id)
                .values(
                    status=MergeJobStatus.PROCESSING.value,
                    total_duration=round(total_duration, 2),
                    progress=5.0,
                    input_files_json=json.dumps(validated_items, ensure_ascii=False),
                )
            )
            await session.commit()

        # Step 2: Check Concat Strategy
        # Determine if all videos have identical parameters (width, height, fps, v_codec, a_codec, has_audio)
        first = validated_items[0]
        can_fast_concat = (
            len(validated_items) > 1
            and all(
                i["width"] == first["width"]
                and i["height"] == first["height"]
                and abs(i["fps"] - first["fps"]) < 0.5
                and i["video_codec"] == first["video_codec"]
                and i["audio_codec"] == first["audio_codec"]
                and i["has_audio"] is True
                for i in validated_items
            )
        )

        # Fast concat attempt if parameters match
        fast_concat_success = False
        if can_fast_concat:
            logger.info("Attempting fast concat (-c copy) for identical video parameters", job_id=job_id)
            concat_list_path = tmp_dir / "concat_list.txt"
            with open(concat_list_path, "w", encoding="utf-8") as f:
                for item in validated_items:
                    escaped_p = item["file_path"].replace("\\", "/").replace("'", "'\\''")
                    f.write(f"file '{escaped_p}'\n")

            cmd_fast = [
                "ffmpeg", "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", str(concat_list_path),
                "-c", "copy",
                str(output_path),
            ]

            last_progress_pct = 5.0

            def _on_fast_progress(snap: dict):
                nonlocal last_progress_pct
                pct = min(99.0, max(5.0, snap.get("progress_pct", 0.0)))
                if pct - last_progress_pct >= 2.0 or pct >= 99.0:
                    last_progress_pct = pct
                    asyncio.create_task(cls._update_job_progress(job_id, pct, snap.get("processed_seconds", 0.0)))

            try:
                await run_ffmpeg_with_progress_async(
                    cmd_fast,
                    total_duration=total_duration,
                    on_progress=_on_fast_progress,
                    timeout=600,
                )
                if output_path.exists() and output_path.stat().st_size > 0:
                    fast_concat_success = True
                    logger.info("Fast concat succeeded!", job_id=job_id, output=str(output_path))
            except Exception as ex:
                logger.warning("Fast concat copy failed, falling back to full filter normalization", job_id=job_id, error=str(ex))
                if output_path.exists():
                    output_path.unlink(missing_ok=True)

        # Step 3: Complex Filter Normalization (if fast concat not applicable or failed)
        if not fast_concat_success:
            logger.info("Executing FFmpeg Filter Complex Normalization engine", job_id=job_id)

            # 1. Determine target resolution (max width, max height rounded to even integers)
            target_w = max(i["width"] for i in validated_items) or 1920
            target_h = max(i["height"] for i in validated_items) or 1080
            target_w = target_w if target_w % 2 == 0 else target_w + 1
            target_h = target_h if target_h % 2 == 0 else target_h + 1
            target_fps = 30

            # Build command inputs and filter graph
            cmd_args: List[str] = ["ffmpeg", "-y"]
            filter_parts: List[str] = []
            concat_inputs: List[str] = []

            for idx, item in enumerate(validated_items):
                cmd_args.extend(["-i", item["file_path"]])

                # Video filter graph for item idx
                # Rescale while maintaining aspect ratio, pad with black background, force sar=1, fps=30, format=yuv420p
                v_label = f"v{idx}"
                v_filter = (
                    f"[{idx}:v]scale={target_w}:{target_h}:force_original_aspect_ratio=decrease,"
                    f"pad={target_w}:{target_h}:({target_w}-iw)/2:({target_h}-ih)/2:color=black,"
                    f"setsar=1,fps={target_fps},format=yuv420p[{v_label}]"
                )
                filter_parts.append(v_filter)

                # Audio filter graph for item idx
                a_label = f"a{idx}"
                if item["has_audio"]:
                    a_filter = f"[{idx}:a]aformat=sample_rates=44100:channel_layouts=stereo[{a_label}]"
                else:
                    # Generate silent audio matching video duration for silent videos
                    a_filter = f"anullsrc=r=44100:cl=stereo:d={item['duration']}[{a_label}]"
                filter_parts.append(a_filter)

                concat_inputs.append(f"[{v_label}][{a_label}]")

            # Concat filter string
            N = len(validated_items)
            concat_filter = f"{''.join(concat_inputs)}concat=n={N}:v=1:a=1[outv][outa]"
            filter_parts.append(concat_filter)

            full_filter_complex = ";".join(filter_parts)

            cmd_args.extend(
                [
                    "-filter_complex", full_filter_complex,
                    "-map", "[outv]",
                    "-map", "[outa]",
                    "-c:v", "libx264",
                    "-preset", "fast",
                    "-crf", "23",
                    "-c:a", "aac",
                    "-b:a", "192k",
                    str(output_path),
                ]
            )

            last_progress_pct = 5.0

            def _on_norm_progress(snap: dict):
                nonlocal last_progress_pct
                pct = min(99.0, max(5.0, snap.get("progress_pct", 0.0)))
                if pct - last_progress_pct >= 1.5 or pct >= 99.0:
                    last_progress_pct = pct
                    asyncio.create_task(cls._update_job_progress(job_id, pct, snap.get("processed_seconds", 0.0)))

            try:
                await run_ffmpeg_with_progress_async(
                    cmd_args,
                    total_duration=total_duration,
                    on_progress=_on_norm_progress,
                    timeout=1800,  # 30 minutes max timeout for long video renders
                )
            except FFmpegExecutionError as f_err:
                logger.error("FFmpeg normalization execution failed", job_id=job_id, error=str(f_err))
                err_text = f_err.stderr_text or str(f_err)
                clean_err = f"❌ Ghép video thất bại do lỗi FFmpeg: {err_text[:300]}"
                await cls._mark_job_failed(job_id, clean_err)
                cls._cleanup_tmp_dir(tmp_dir)
                return
            except Exception as ex:
                logger.error("Unexpected error during video merge execution", job_id=job_id, error=str(ex))
                await cls._mark_job_failed(job_id, f"❌ Lỗi hệ thống trong quá trình ghép video: {str(ex)}")
                cls._cleanup_tmp_dir(tmp_dir)
                return

        # Step 4: Finalize Job and Store Output
        if not output_path.exists() or output_path.stat().st_size == 0:
            await cls._mark_job_failed(job_id, "❌ File output ghép video không được tạo ra hoặc có kích thước 0 byte.")
            cls._cleanup_tmp_dir(tmp_dir)
            return

        # Store merged video in persistent local storage
        object_key = f"merger/jobs/{job_id}/{output_filename}"
        stored_key, access_url = await LocalStorageService.upload_file(output_path, object_key)

        # Generate thumbnail for the output video
        output_thumb_name = f"thumb_{job_id[:8]}.jpg"
        output_thumb_url = await cls.extract_thumbnail_async(output_path, output_thumb_name)

        async with async_session_factory() as session:
            await session.execute(
                update(VideoMergeJob)
                .where(VideoMergeJob.id == job_id)
                .values(
                    status=MergeJobStatus.COMPLETED.value,
                    progress=100.0,
                    output_video_path=str(output_path.resolve()),
                    output_relative_url=access_url,
                    output_filename=output_filename,
                    processed_duration=round(total_duration, 2),
                    error_message=None,
                )
            )
            await session.commit()

        logger.info("Video Merge Job completed successfully!", job_id=job_id, output_url=access_url)
        cls._cleanup_tmp_dir(tmp_dir)

    @classmethod
    async def _update_job_progress(cls, job_id: str, progress: float, processed_seconds: float) -> None:
        """Helper to update real-time progress in database."""
        try:
            async with async_session_factory() as session:
                await session.execute(
                    update(VideoMergeJob)
                    .where(VideoMergeJob.id == job_id)
                    .values(
                        progress=round(progress, 1),
                        processed_duration=round(processed_seconds, 2),
                    )
                )
                await session.commit()
        except Exception:
            pass

    @classmethod
    async def _mark_job_failed(cls, job_id: str, error_msg: str) -> None:
        """Helper to mark job as failed with error details."""
        try:
            async with async_session_factory() as session:
                await session.execute(
                    update(VideoMergeJob)
                    .where(VideoMergeJob.id == job_id)
                    .values(
                        status=MergeJobStatus.FAILED.value,
                        error_message=error_msg,
                    )
                )
                await session.commit()
        except Exception:
            pass

    @classmethod
    def _cleanup_tmp_dir(cls, tmp_dir: Path) -> None:
        """Helper to remove temporary working directory."""
        if tmp_dir.exists():
            try:
                shutil.rmtree(tmp_dir, ignore_errors=True)
            except Exception:
                pass
