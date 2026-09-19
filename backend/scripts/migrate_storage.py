"""
Storage Migration & Consolidation Utility.

Safely merges and migrates legacy storage folders into the unified STORAGE_ROOT:
1. Moves legacy 'backend/storage/projects/<id>' -> 'storage/projects/<id>'
2. Moves legacy 'data/translator/jobs/<id>' -> 'storage/translator/jobs/<id>'
3. Moves legacy 'data/translator/assets/<id>' -> 'storage/translator/assets/<id>'
4. Updates file path references across SQLite/MySQL database records.
5. Supports --dry-run for safety check and --rollback for reversible operations.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Ensure backend and project root are in sys.path
backend_dir = Path(__file__).resolve().parent.parent
project_root = backend_dir.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.config import get_settings
from app.database import async_session_factory
from app.models.project import Project
from app.models.video_translator import VideoTranslationJob, VideoAsset
from app.models.video_merger import VideoMergeJob, VideoMergeAsset
from sqlalchemy import select, update

settings = get_settings()

MANIFEST_PATH = settings.STORAGE_ROOT / "migration_manifest.json"


def merge_directories(src: Path, dst: Path, dry_run: bool = False) -> Tuple[int, int]:
    """
    Recursively move files from src to dst.
    Returns (files_moved, bytes_moved).
    """
    files_moved = 0
    bytes_moved = 0

    if not src.exists():
        return 0, 0

    if not dst.exists():
        if not dry_run:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
        for root, _, files in os.walk(src if dry_run else dst):
            for f in files:
                fp = Path(root) / f
                try:
                    bytes_moved += fp.stat().st_size
                    files_moved += 1
                except Exception:
                    pass
        return files_moved, bytes_moved

    # Destination exists, merge file by file
    for root, dirs, files in os.walk(src):
        rel_root = Path(root).relative_to(src)
        target_root = dst / rel_root
        if not dry_run:
            target_root.mkdir(parents=True, exist_ok=True)

        for f in files:
            src_file = Path(root) / f
            dst_file = target_root / f
            try:
                sz = src_file.stat().st_size
                if not dst_file.exists():
                    if not dry_run:
                        shutil.move(str(src_file), str(dst_file))
                    files_moved += 1
                    bytes_moved += sz
                else:
                    # File already exists at target
                    if src_file.stat().st_mtime > dst_file.stat().st_mtime:
                        if not dry_run:
                            dst_file.unlink(missing_ok=True)
                            shutil.move(str(src_file), str(dst_file))
                        files_moved += 1
                        bytes_moved += sz
            except Exception as e:
                print(f"    [Error] Failed to move {src_file}: {e}")

    # Remove remaining empty source tree
    if not dry_run:
        try:
            shutil.rmtree(src)
        except Exception:
            pass

    return files_moved, bytes_moved


async def migrate_all(dry_run: bool = False) -> Dict[str, Any]:
    print(f"\n{'[DRY RUN] ' if dry_run else ''}=== Starting Storage Consolidation & Migration ===")
    settings.STORAGE_ROOT.mkdir(parents=True, exist_ok=True)

    manifest_records: List[Dict[str, Any]] = []
    total_files = 0
    total_bytes = 0

    legacy_backend_storage_projects = Path(settings.ROOT_DIR) / "backend" / "storage" / "projects"
    target_projects = settings.STORAGE_ROOT / "projects"

    legacy_data_jobs = settings.DATA_DIR / "translator" / "jobs"
    target_jobs = settings.STORAGE_ROOT / "translator" / "jobs"

    legacy_data_assets = settings.DATA_DIR / "translator" / "assets"
    target_assets = settings.STORAGE_ROOT / "translator" / "assets"

    # 1. Migrate backend/storage/projects
    if legacy_backend_storage_projects.exists():
        print(f"\nScanning legacy backend projects: {legacy_backend_storage_projects}")
        for folder in list(legacy_backend_storage_projects.iterdir()):
            if folder.is_dir():
                target_dir = target_projects / folder.name
                f_count, b_count = merge_directories(folder, target_dir, dry_run=dry_run)
                if f_count > 0:
                    print(f"  -> Migrated project {folder.name}: {f_count} files ({b_count / (1024*1024):.2f} MB)")
                    total_files += f_count
                    total_bytes += b_count
                    manifest_records.append({
                        "type": "directory_move",
                        "src": str(folder),
                        "dst": str(target_dir),
                        "files": f_count,
                        "bytes": b_count,
                    })

    # 2. Migrate data/translator/jobs
    if legacy_data_jobs.exists():
        print(f"\nScanning legacy translator jobs: {legacy_data_jobs}")
        for folder in list(legacy_data_jobs.iterdir()):
            if folder.is_dir():
                target_dir = target_jobs / folder.name
                f_count, b_count = merge_directories(folder, target_dir, dry_run=dry_run)
                if f_count > 0:
                    print(f"  -> Migrated job {folder.name}: {f_count} files ({b_count / (1024*1024):.2f} MB)")
                    total_files += f_count
                    total_bytes += b_count
                    manifest_records.append({
                        "type": "directory_move",
                        "src": str(folder),
                        "dst": str(target_dir),
                        "files": f_count,
                        "bytes": b_count,
                    })

    # 3. Migrate data/translator/assets
    if legacy_data_assets.exists():
        print(f"\nScanning legacy translator assets: {legacy_data_assets}")
        for folder in list(legacy_data_assets.iterdir()):
            if folder.is_dir():
                target_dir = target_assets / folder.name
                f_count, b_count = merge_directories(folder, target_dir, dry_run=dry_run)
                if f_count > 0:
                    print(f"  -> Migrated asset {folder.name}: {f_count} files ({b_count / (1024*1024):.2f} MB)")
                    total_files += f_count
                    total_bytes += b_count
                    manifest_records.append({
                        "type": "directory_move",
                        "src": str(folder),
                        "dst": str(target_dir),
                        "files": f_count,
                        "bytes": b_count,
                    })

    # 4. Update Database path references
    print("\nUpdating Database path references...")
    db_updates = 0
    try:
        async with async_session_factory() as session:
            # VideoTranslationJob
            try:
                vt_jobs = (await session.execute(select(VideoTranslationJob))).scalars().all()
                for job in vt_jobs:
                    changed = False
                    if job.source_video_path and "data/translator" in job.source_video_path:
                        job.source_video_path = job.source_video_path.replace("data/translator", "storage/translator")
                        changed = True
                    if job.output_video_path and "data/translator" in job.output_video_path:
                        job.output_video_path = job.output_video_path.replace("data/translator", "storage/translator")
                        changed = True
                    if job.source_video_path and "backend/storage" in job.source_video_path:
                        job.source_video_path = job.source_video_path.replace("backend/storage", "storage")
                        changed = True
                    if job.output_video_path and "backend/storage" in job.output_video_path:
                        job.output_video_path = job.output_video_path.replace("backend/storage", "storage")
                        changed = True
                    if changed:
                        db_updates += 1
            except Exception as ex:
                print(f"  [Notice] Skipping VideoTranslationJob table: {ex}")

            # VideoAsset
            try:
                v_assets = (await session.execute(select(VideoAsset))).scalars().all()
                for asset in v_assets:
                    changed = False
                    if asset.file_path and "data/translator" in asset.file_path:
                        asset.file_path = asset.file_path.replace("data/translator", "storage/translator")
                        changed = True
                    if asset.thumbnail_path and "data/translator" in asset.thumbnail_path:
                        asset.thumbnail_path = asset.thumbnail_path.replace("data/translator", "storage/translator")
                        changed = True
                    if asset.file_path and "backend/storage" in asset.file_path:
                        asset.file_path = asset.file_path.replace("backend/storage", "storage")
                        changed = True
                    if changed:
                        db_updates += 1
            except Exception as ex:
                print(f"  [Notice] Skipping VideoAsset table: {ex}")

            # VideoMergeJob & VideoMergeAsset
            try:
                vm_jobs = (await session.execute(select(VideoMergeJob))).scalars().all()
                for mjob in vm_jobs:
                    if mjob.output_video_path and "backend/storage" in mjob.output_video_path:
                        mjob.output_video_path = mjob.output_video_path.replace("backend/storage", "storage")
                        db_updates += 1

                vm_assets = (await session.execute(select(VideoMergeAsset))).scalars().all()
                for masset in vm_assets:
                    if masset.file_path and "backend/storage" in masset.file_path:
                        masset.file_path = masset.file_path.replace("backend/storage", "storage")
                        db_updates += 1
            except Exception as ex:
                print(f"  [Notice] Skipping VideoMerge tables: {ex}")

            if not dry_run and db_updates > 0:
                await session.commit()
    except Exception as e:
        print(f"  [Warning] Database connection or session error: {e}")

    print(f"Database references updated: {db_updates} records")

    # Save manifest for rollback
    if not dry_run and manifest_records:
        MANIFEST_PATH.write_text(json.dumps(manifest_records, indent=2), encoding="utf-8")
        print(f"Migration manifest saved to: {MANIFEST_PATH}")

    summary = {
        "status": "success",
        "dry_run": dry_run,
        "total_files_migrated": total_files,
        "total_bytes_migrated": total_bytes,
        "db_records_updated": db_updates,
    }
    print(f"\nMigration Summary: {total_files} files ({total_bytes / (1024*1024):.2f} MB), {db_updates} DB rows updated.")
    return summary


async def rollback() -> None:
    print("\n=== Rolling back storage migration from manifest ===")
    if not MANIFEST_PATH.exists():
        print(f"❌ Manifest not found at {MANIFEST_PATH}. Nothing to roll back.")
        return

    manifest: List[Dict[str, Any]] = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    restored_dirs = 0

    for item in manifest:
        src = Path(item["src"])
        dst = Path(item["dst"])
        if dst.exists():
            print(f"  -> Restoring {dst} -> {src}")
            merge_directories(dst, src, dry_run=False)
            restored_dirs += 1

    # Revert DB path strings
    print("\nReverting database path strings...")
    db_reverts = 0
    async with async_session_factory() as session:
        vt_jobs = (await session.execute(select(VideoTranslationJob))).scalars().all()
        for job in vt_jobs:
            changed = False
            if job.source_video_path and "storage/translator" in job.source_video_path:
                job.source_video_path = job.source_video_path.replace("storage/translator", "data/translator")
                changed = True
            if job.output_video_path and "storage/translator" in job.output_video_path:
                job.output_video_path = job.output_video_path.replace("storage/translator", "data/translator")
                changed = True
            if changed:
                db_reverts += 1

        v_assets = (await session.execute(select(VideoAsset))).scalars().all()
        for asset in v_assets:
            changed = False
            if asset.file_path and "storage/translator" in asset.file_path:
                asset.file_path = asset.file_path.replace("storage/translator", "data/translator")
                changed = True
            if asset.thumbnail_path and "storage/translator" in asset.thumbnail_path:
                asset.thumbnail_path = asset.thumbnail_path.replace("storage/translator", "data/translator")
                changed = True
            if changed:
                db_reverts += 1

        await session.commit()

    MANIFEST_PATH.unlink(missing_ok=True)
    print(f"\nRollback complete: {restored_dirs} directories reverted, {db_reverts} DB records reverted.")


def main():
    parser = argparse.ArgumentParser(description="Storage Consolidation and Migration Tool")
    parser.add_argument("--dry-run", action="store_true", help="Simulate migration without modifying files or DB")
    parser.add_argument("--rollback", action="store_true", help="Revert migration using migration_manifest.json")
    args = parser.parse_args()

    if args.rollback:
        asyncio.run(rollback())
    else:
        asyncio.run(migrate_all(dry_run=args.dry_run))


if __name__ == "__main__":
    main()
