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
        job_dir = settings.DATA_DIR / "translator" / "jobs" / job_id
        if not job_dir.exists():
            return {"deleted_files": 0, "failed_files": 0, "bytes_freed": 0, "status": "job_dir_not_found"}

        deleted_files = 0
        failed_files = 0
        bytes_freed = 0

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

                    asset_disk = settings.DATA_DIR / "translator" / "assets" / asset_id
                    if asset_disk.exists():
                        cls.safe_remove_dir(asset_disk)
                        res_info["deleted_local_dirs"].append(str(asset_disk))

            # Delete job workspace local directory
            job_disk = settings.DATA_DIR / "translator" / "jobs" / item_id
            if job_disk.exists():
                cls.safe_remove_dir(job_disk)
                res_info["deleted_local_dirs"].append(str(job_disk))

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
        job_rows = await session.execute(select(VideoTranslationJob.id, VideoTranslationJob.r2_key))
        for j_id, j_r2 in job_rows.fetchall():
            if j_id:
                valid_job_ids.add(j_id)
            if j_r2:
                valid_r2_keys.add(j_r2.lstrip("/\\").replace("\\", "/"))

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

        orphan_local_files: List[Dict[str, Any]] = []
        orphan_local_dirs: List[Path] = []
        orphan_r2_keys: List[str] = []
        reclaimable_bytes = 0

        # 1. Scan Jobs Directory
        jobs_dir = settings.DATA_DIR / "translator" / "jobs"
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

        # 2. Scan Assets Directory
        assets_dir = settings.DATA_DIR / "translator" / "assets"
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

        # 3. Scan Standard Projects Directory
        projects_dir = settings.PROJECTS_DIR
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

        # 4. Scan Local R2 Storage Emulator
        r2_local_dir = storage_service.get_local_storage_dir()
        if r2_local_dir.exists():
            for root, _, files in os.walk(r2_local_dir):
                for f in files:
                    fp = Path(root) / f
                    rel_key = str(fp.relative_to(r2_local_dir)).replace("\\", "/")
                    if rel_key not in valid_r2_keys and not any(rel_key.startswith(f"translator/jobs/{j}/") for j in valid_job_ids):
                        age = now - fp.stat().st_mtime
                        if age >= max_age_sec:
                            try:
                                sz = fp.stat().st_size
                                reclaimable_bytes += sz
                                orphan_local_files.append({"path": str(fp), "size": sz, "reason": f"Orphan R2 local file: {rel_key}"})
                                orphan_r2_keys.append(rel_key)
                            except Exception:
                                pass

        report = {
            "dry_run": dry_run,
            "age_hours_threshold": age_hours,
            "valid_jobs_count": len(valid_job_ids),
            "valid_assets_count": len(valid_asset_ids),
            "valid_projects_count": len(valid_proj_ids),
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
