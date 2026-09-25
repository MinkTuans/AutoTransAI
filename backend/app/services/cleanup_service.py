"""
Centralized Storage Lifecycle & File Cleanup Service.

Provides unified abstractions for:
- Job workspace cleanup (post-render success or failure)
- Project & job deletion with dependency cascading & R2 sync
- Asset reference counting for shared source video assets
- Local & Cloudflare R2 orphan scanner with dry-run and age thresholds
- Safe Windows file handle unlinking & error handling
"""

from __future__ import annotations

import os
import shutil
import asyncio
import time
from pathlib import Path
from typing import Optional, Dict, Any, List, Set, Tuple

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core import get_logger
from app.core.job_logger import log_job_event
from app.services.storage_service import storage_service
from app.models import (
    Project,
    Segment,
    VideoAsset,
    VideoTranslationJob,
    VideoTranslationSegment,
    VideoThumbnail,
    VideoMergeJob,
    VideoMergeAsset,
)

logger = get_logger(__name__)
settings = get_settings()


class FileCleanupService:
    """
    Centralized service for file lifecycle management, directory cleanup,
    R2 storage syncing, and orphan file scanning.
    """

    @staticmethod
    def safe_remove_file(file_path: Path) -> bool:
        """Safely delete a single file with Windows handle retry logic."""
        file_path = Path(file_path)
        if not file_path.exists():
            return True

        for attempt in range(3):
            try:
                file_path.unlink(missing_ok=True)
                return True
            except PermissionError as pe:
                logger.warning(f"File locked, retrying unlink attempt {attempt+1}/3: {file_path} ({pe})")
                time.sleep(0.2)
            except Exception as e:
                logger.warning(f"Failed to unlink file {file_path}: {e}")
                break
        return False

    @staticmethod
    def safe_remove_dir(dir_path: Path) -> bool:
        """Safely delete a directory and all subcontents."""
        dir_path = Path(dir_path)
        if not dir_path.exists():
            return True

        try:
            shutil.rmtree(dir_path, ignore_errors=True)
            return not dir_path.exists()
        except Exception as e:
            logger.warning(f"Failed to remove directory {dir_path}: {e}")
            return False

    @classmethod
    def cleanup_job_workspace(
        cls,
        job_id: str,
        keep_logs: bool = True,
        keep_final_video: bool = True,
    ) -> Dict[str, Any]:
        """
        Clean temporary processing files in a Video Translation job workspace.
        
        Preserves:
        - job.log (if keep_logs=True)
        - final_dubbed_video.mp4 (if keep_final_video=True)
        
        Purges:
        - extracted_audio.wav
        - chunks/ (Gemini & Whisper STT chunks)
        - tts/ (Raw TTS WAVs)
        - synced/ (Time-stretched WAVs)
        - work/ (Combined PCM timeline WAV)
        - Any temporary .wav, .mp3, .aac, .m4a files in job root
        """
        job_dirs = [
            settings.STORAGE_ROOT / "translator" / "jobs" / job_id,
            settings.DATA_DIR / "translator" / "jobs" / job_id,
        ]
        target_dirs = [d for d in job_dirs if d.exists()]
        if not target_dirs:
            return {"deleted_files": 0, "failed_files": 0, "bytes_freed": 0, "status": "job_dir_not_found"}

        deleted_files = 0
        failed_files = 0
        bytes_freed = 0

        for job_dir in target_dirs:
            # Purge temporary subdirectories
            temp_subs = ["chunks", "tts", "synced", "work"]
            for sub in temp_subs:
                sub_path = job_dir / sub
                if sub_path.exists():
                    for root, _, files in os.walk(sub_path):
                        for f in files:
                            fp = Path(root) / f
                            try:
                                bytes_freed += fp.stat().st_size
                                deleted_files += 1
                            except Exception:
                                pass
                    if not cls.safe_remove_dir(sub_path):
                        failed_files += 1

            # Also purge legacy chunk directories inside job_dir if present
            for item in list(job_dir.iterdir()):
                if item.is_dir() and ("chunks" in item.name or "temp" in item.name or "work" in item.name):
                    for root, _, files in os.walk(item):
                        for f in files:
                            fp = Path(root) / f
                            try:
                                bytes_freed += fp.stat().st_size
                                deleted_files += 1
                            except Exception:
                                pass
                    if not cls.safe_remove_dir(item):
                        failed_files += 1
                elif item.is_file():
                    filename = item.name.lower()
                    is_log = (filename == "job.log")
                    is_final = (filename == "final_dubbed_video.mp4")

                    if (is_log and keep_logs) or (is_final and keep_final_video):
                        continue

                    if filename.endswith((".wav", ".mp3", ".aac", ".m4a", ".tmp")) or filename == "extracted_audio.wav":
                        try:
                            sz = item.stat().st_size
                            if cls.safe_remove_file(item):
                                bytes_freed += sz
                                deleted_files += 1
                            else:
                                failed_files += 1
                        except Exception:
                            failed_files += 1

        res = {
            "job_id": job_id,
            "deleted_files": deleted_files,
            "failed_files": failed_files,
            "bytes_freed": bytes_freed,
            "status": "success",
        }
        logger.info(f"[CLEANUP] Job workspace cleaned ({job_id}): {deleted_files} files, {bytes_freed / (1024*1024):.2f} MB freed")
        return res

    @classmethod
    async def cleanup_completed_translation(
        cls, job_id: str, session: AsyncSession,
    ) -> Dict[str, Any]:
        """Discard a finished job's private workspace after its durable result exists."""
        job = await session.get(VideoTranslationJob, job_id)
        if job is None or job.status != "completed":
            return {"status": "not_completed"}

        storage_root = settings.STORAGE_ROOT.resolve()
        result = Path(job.output_video_path or "").resolve()
        job_dirs = [
            settings.STORAGE_ROOT / "translator" / "jobs" / job_id,
            settings.DATA_DIR / "translator" / "jobs" / job_id,
        ]
        if (not job.output_video_path or not result.is_file() or result.stat().st_size == 0
                or not result.is_relative_to(storage_root)
                or any(result.is_relative_to(path.resolve()) for path in job_dirs)):
            return {"status": "result_not_durable"}

        legacy_thumbnail_prefix = f"translator/jobs/{job_id}/"
        thumbnail_keys = [job.thumbnail_r2_key]
        thumbnail_keys.extend((await session.execute(
            select(VideoThumbnail.r2_key).where(VideoThumbnail.job_id == job_id)
        )).scalars().all())
        if any(key and key.lstrip("/\\").replace("\\", "/").startswith(legacy_thumbnail_prefix)
               for key in thumbnail_keys):
            return {"status": "referenced_workspace_file"}

        for path in job_dirs:
            if not cls.safe_remove_dir(path):
                return {"status": "workspace_cleanup_failed", "path": str(path)}

        asset = await session.get(VideoAsset, job.asset_id)
        if asset is not None:
            statuses = (await session.execute(
                select(VideoTranslationJob.status).where(VideoTranslationJob.asset_id == asset.id)
            )).scalars().all()
            if statuses and all(status == "completed" for status in statuses):
                asset_dirs = [
                    settings.STORAGE_ROOT / "translator" / "assets" / asset.id,
                    settings.DATA_DIR / "translator" / "assets" / asset.id,
                ]
                # Uploaded media belongs to the asset directory. Never remove an
                # arbitrary external path supplied by a historical DB record.
                source = Path(asset.file_path).resolve()
                if any(source.is_relative_to(path.resolve()) for path in asset_dirs):
                    for asset_dir in asset_dirs:
                        if asset_dir.is_dir():
                            for child in asset_dir.iterdir():
                                if child.name == "thumbnails":
                                    continue
                                if child.is_dir():
                                    if not cls.safe_remove_dir(child):
                                        return {"status": "source_cleanup_failed"}
                                elif not cls.safe_remove_file(child):
                                    return {"status": "source_cleanup_failed"}
                    asset.status = "archived"
                    asset.r2_key = None
                    asset.url = None

        job.is_cleaned = True
        await session.commit()
        return {"status": "success"}

    @classmethod
    async def cleanup_project(
        cls,
        item_id: str,
        session: AsyncSession,
    ) -> Dict[str, Any]:
        """
        Delete a single Project or VideoTranslationJob with DB cascade,
        R2 object deletion, and asset reference counting safety.
        """
        res_info = {
            "item_id": item_id,
            "type": "unknown",
            "deleted_r2_keys": [],
            "deleted_local_dirs": [],
            "status": "not_found",
        }

        # 1. Check if Standard Project
        std_res = await session.execute(select(Project).where(Project.id == item_id))
        std_proj = std_res.scalar_one_or_none()
        if std_proj:
            res_info["type"] = "standard_project"
            linked_jobs = (await session.execute(
                select(VideoTranslationJob.id).where(VideoTranslationJob.project_id == item_id)
            )).scalars().all()
            for linked_job_id in linked_jobs:
                linked_result = await cls.cleanup_project(linked_job_id, session)
                if linked_result["status"] != "success":
                    return {**res_info, "status": "linked_job_cleanup_failed", "job_id": linked_job_id}
            if std_proj.r2_key:
                await storage_service.delete_file(std_proj.r2_key)
                res_info["deleted_r2_keys"].append(std_proj.r2_key)

            await session.execute(delete(Segment).where(Segment.project_id == item_id))
            await session.delete(std_proj)
            await session.commit()

            proj_dir = settings.PROJECTS_DIR / item_id
            if proj_dir.exists():
                cls.safe_remove_dir(proj_dir)
                res_info["deleted_local_dirs"].append(str(proj_dir))

            # Backward compatibility: Clean legacy directory in backend/storage/projects
            legacy_proj_dir = Path(settings.ROOT_DIR) / "backend" / "storage" / "projects" / item_id
            if legacy_proj_dir.exists():
                cls.safe_remove_dir(legacy_proj_dir)
                res_info["deleted_local_dirs"].append(str(legacy_proj_dir))

            # Also delete from local storage service
            await storage_service.delete_project_files(item_id)

            res_info["status"] = "success"
            return res_info

        # 2. Check if Video Translation Job
        vt_res = await session.execute(select(VideoTranslationJob).where(VideoTranslationJob.id == item_id))
        vt_job = vt_res.scalar_one_or_none()
        if vt_job:
            res_info["type"] = "video_translation_job"
            asset_id = vt_job.asset_id

            if vt_job.r2_key:
                await storage_service.delete_file(vt_job.r2_key)
                res_info["deleted_r2_keys"].append(vt_job.r2_key)

            # Purge job R2 final video key
            job_r2_video_key = f"translator/jobs/{item_id}/final_dubbed_video.mp4"
            await storage_service.delete_file(job_r2_video_key)
            res_info["deleted_r2_keys"].append(job_r2_video_key)

            # Delete DB segments and job record
            await session.execute(
                delete(VideoTranslationSegment)
                .where(VideoTranslationSegment.job_id == item_id)
                .execution_options(synchronize_session=False)
            )
            await session.delete(vt_job)
            await session.commit()

            # Asset Reference Counting: Only delete VideoAsset if NO other jobs reference it
            other_jobs = await session.execute(
                select(func.count(VideoTranslationJob.id)).where(VideoTranslationJob.asset_id == asset_id)
            )
            job_count = other_jobs.scalar() or 0
            if job_count == 0 and asset_id:
                asset_res = await session.execute(select(VideoAsset).where(VideoAsset.id == asset_id))
                asset = asset_res.scalar_one_or_none()
                if asset:
                    if asset.r2_key:
                        await storage_service.delete_file(asset.r2_key)
                        res_info["deleted_r2_keys"].append(asset.r2_key)
                    await session.delete(asset)
                    await session.commit()

                    # Check unified STORAGE_ROOT translator assets
                    asset_disk = settings.STORAGE_ROOT / "translator" / "assets" / asset_id
                    if asset_disk.exists():
                        cls.safe_remove_dir(asset_disk)
                        res_info["deleted_local_dirs"].append(str(asset_disk))

                    # Check legacy DATA_DIR translator assets
                    legacy_asset_disk = settings.DATA_DIR / "translator" / "assets" / asset_id
                    if legacy_asset_disk.exists():
                        cls.safe_remove_dir(legacy_asset_disk)
                        res_info["deleted_local_dirs"].append(str(legacy_asset_disk))

            # Delete job workspace local directory (check unified STORAGE_ROOT and legacy DATA_DIR)
            job_disk = settings.STORAGE_ROOT / "translator" / "jobs" / item_id
            if job_disk.exists():
                cls.safe_remove_dir(job_disk)
                res_info["deleted_local_dirs"].append(str(job_disk))

            legacy_job_disk = settings.DATA_DIR / "translator" / "jobs" / item_id
            if legacy_job_disk.exists():
                cls.safe_remove_dir(legacy_job_disk)
                res_info["deleted_local_dirs"].append(str(legacy_job_disk))

            # Backward compatibility check for legacy backend/storage/projects
            legacy_proj_dir = Path(settings.ROOT_DIR) / "backend" / "storage" / "projects" / item_id
            if legacy_proj_dir.exists():
                cls.safe_remove_dir(legacy_proj_dir)
                res_info["deleted_local_dirs"].append(str(legacy_proj_dir))

            # Ensure all objects under translator/jobs/{item_id} or projects/{item_id} are deleted
            await storage_service.delete_project_files(item_id)

            res_info["status"] = "success"
            return res_info

        return res_info

    @classmethod
    async def scan_orphan_files(
        cls,
        session: AsyncSession,
        dry_run: bool = True,
        age_hours: float = 24.0,
    ) -> Dict[str, Any]:
        """
        Scan local storage and Cloudflare R2 / emulator storage for orphan files
        not referenced by any active DB records.
        """
        now = time.time()
        max_age_sec = age_hours * 3600.0

        # Collect valid DB references
        valid_job_ids: Set[str] = set()
        valid_asset_ids: Set[str] = set()
        valid_proj_ids: Set[str] = set()
        valid_r2_keys: Set[str] = set()

        # Jobs
        job_rows = await session.execute(select(
            VideoTranslationJob.id, VideoTranslationJob.r2_key,
            VideoTranslationJob.output_video_path, VideoTranslationJob.thumbnail_r2_key,
        ))
        for j_id, j_r2, j_output, j_thumbnail in job_rows.fetchall():
            if j_id:
                valid_job_ids.add(j_id)
            for key in (j_r2, j_thumbnail):
                if key:
                    normalized = key.lstrip("/\\").replace("\\", "/")
                    valid_r2_keys.add(normalized)
                    parts = normalized.split("/")
                    if len(parts) > 2 and parts[0] == "projects":
                        valid_proj_ids.add(parts[1])
            if j_output:
                try:
                    rel_output = Path(j_output).resolve().relative_to(settings.STORAGE_ROOT.resolve())
                    if len(rel_output.parts) > 2 and rel_output.parts[0] == "projects":
                        valid_proj_ids.add(rel_output.parts[1])
                except ValueError:
                    pass

        # Assets
        asset_rows = await session.execute(select(VideoAsset.id, VideoAsset.r2_key))
        for a_id, a_r2 in asset_rows.fetchall():
            if a_id:
                valid_asset_ids.add(a_id)
            if a_r2:
                valid_r2_keys.add(a_r2.lstrip("/\\").replace("\\", "/"))

        # Standard Projects
        proj_rows = await session.execute(select(Project.id, Project.r2_key))
        for p_id, p_r2 in proj_rows.fetchall():
            if p_id:
                valid_proj_ids.add(p_id)
            if p_r2:
                valid_r2_keys.add(p_r2.lstrip("/\\").replace("\\", "/"))

        # Video Merge Jobs & Assets
        valid_merge_job_ids: Set[str] = set()
        valid_disk_files: Set[str] = set()
        merge_job_rows = await session.execute(
            select(VideoMergeJob.id, VideoMergeJob.output_video_path, VideoMergeJob.output_relative_url)
        )
        for m_id, m_path, m_url in merge_job_rows.fetchall():
            if m_id:
                valid_merge_job_ids.add(m_id)
            if m_path:
                try:
                    valid_disk_files.add(str(Path(m_path).resolve()))
                except Exception:
                    pass
            if m_url:
                valid_r2_keys.add(m_url.lstrip("/\\").replace("\\", "/"))

        merge_asset_rows = await session.execute(select(VideoMergeAsset.file_path))
        for (ma_path,) in merge_asset_rows.fetchall():
            if ma_path:
                try:
                    valid_disk_files.add(str(Path(ma_path).resolve()))
                except Exception:
                    pass

        orphan_local_files: List[Dict[str, Any]] = []
        orphan_local_dirs: List[Path] = []
        orphan_r2_keys: List[str] = []
        reclaimable_bytes = 0

        # 1. Scan Jobs Directories (Unified and Legacy)
        jobs_dirs = [settings.STORAGE_ROOT / "translator" / "jobs", settings.DATA_DIR / "translator" / "jobs"]
        for jobs_dir in jobs_dirs:
            if jobs_dir.exists():
                for folder in jobs_dir.iterdir():
                    if folder.is_dir():
                        j_id = folder.name
                        if j_id not in valid_job_ids:
                            age = now - folder.stat().st_mtime
                            if age >= max_age_sec:
                                orphan_local_dirs.append(folder)
                                for root, _, files in os.walk(folder):
                                    for f in files:
                                        fp = Path(root) / f
                                        try:
                                            sz = fp.stat().st_size
                                            reclaimable_bytes += sz
                                            orphan_local_files.append({"path": str(fp), "size": sz, "reason": f"Orphan job folder: {j_id}"})
                                        except Exception:
                                            pass

        # 2. Scan Assets Directories (Unified and Legacy)
        assets_dirs = [settings.STORAGE_ROOT / "translator" / "assets", settings.DATA_DIR / "translator" / "assets"]
        for assets_dir in assets_dirs:
            if assets_dir.exists():
                for folder in assets_dir.iterdir():
                    if folder.is_dir():
                        a_id = folder.name
                        if a_id not in valid_asset_ids:
                            age = now - folder.stat().st_mtime
                            if age >= max_age_sec:
                                orphan_local_dirs.append(folder)
                                for root, _, files in os.walk(folder):
                                    for f in files:
                                        fp = Path(root) / f
                                        try:
                                            sz = fp.stat().st_size
                                            reclaimable_bytes += sz
                                            orphan_local_files.append({"path": str(fp), "size": sz, "reason": f"Orphan asset folder: {a_id}"})
                                        except Exception:
                                            pass

        # 3. Scan Standard Projects Directories (Unified and Legacy)
        projects_dirs = [settings.PROJECTS_DIR, Path(settings.ROOT_DIR) / "backend" / "storage" / "projects"]
        for projects_dir in projects_dirs:
            if projects_dir.exists():
                for folder in projects_dir.iterdir():
                    if folder.is_dir():
                        p_id = folder.name
                        if p_id not in valid_proj_ids:
                            age = now - folder.stat().st_mtime
                            if age >= max_age_sec:
                                orphan_local_dirs.append(folder)
                                for root, _, files in os.walk(folder):
                                    for f in files:
                                        fp = Path(root) / f
                                        try:
                                            sz = fp.stat().st_size
                                            reclaimable_bytes += sz
                                            orphan_local_files.append({"path": str(fp), "size": sz, "reason": f"Orphan project folder: {p_id}"})
                                        except Exception:
                                            pass

        # 4. Scan Local Supabase Storage Fallback Emulator
        sub_local_dir = storage_service.get_local_storage_dir()
        if sub_local_dir.exists():
            for root, _, files in os.walk(sub_local_dir):
                for f in files:
                    fp = Path(root) / f
                    rel_key = str(fp.relative_to(sub_local_dir)).replace("\\", "/")
                    abs_path_str = ""
                    try:
                        abs_path_str = str(fp.resolve())
                    except Exception:
                        pass

                    is_valid_file = (
                        rel_key in valid_r2_keys
                        or abs_path_str in valid_disk_files
                        or any(rel_key.startswith(f"projects/{p}/") for p in valid_proj_ids)
                        or any(rel_key.startswith(f"translator/assets/{a}/") for a in valid_asset_ids)
                        or any(rel_key.startswith(f"translator/jobs/{j}/") for j in valid_job_ids)
                        or any(rel_key.startswith(f"merger/jobs/{j}/") for j in valid_merge_job_ids)
                    )

                    if not is_valid_file:
                        age = now - fp.stat().st_mtime
                        if age >= max_age_sec:
                            try:
                                sz = fp.stat().st_size
                                reclaimable_bytes += sz
                                orphan_local_files.append({"path": str(fp), "size": sz, "reason": f"Orphan local storage file: {rel_key}"})
                                orphan_r2_keys.append(rel_key)
                            except Exception:
                                pass

        report = {
            "dry_run": dry_run,
            "age_hours_threshold": age_hours,
            "valid_jobs_count": len(valid_job_ids),
            "valid_assets_count": len(valid_asset_ids),
            "valid_projects_count": len(valid_proj_ids),
            "valid_merge_jobs_count": len(valid_merge_job_ids),
            "orphan_files_count": len(orphan_local_files),
            "orphan_dirs_count": len(orphan_local_dirs),
            "orphan_r2_keys_count": len(orphan_r2_keys),
            "reclaimable_bytes": reclaimable_bytes,
            "reclaimable_mb": round(reclaimable_bytes / (1024 * 1024), 2),
            "orphan_files": orphan_local_files[:100],  # Limit sample list
        }

        if not dry_run:
            deleted_count = 0
            for d in orphan_local_dirs:
                if cls.safe_remove_dir(d):
                    deleted_count += 1
            for k in orphan_r2_keys:
                await storage_service.delete_file(k)
            report["deleted_dirs_count"] = deleted_count
            report["status"] = "cleaned"
        else:
            report["status"] = "scanned_dry_run"

        return report
