"""
CLI Tool: Scan and Clean Orphan Storage Files & R2 Objects.

Scans local filesystem (`data/`) and Cloudflare R2 storage (or local emulator) for orphan files
and directories that are no longer referenced in the database.

Usage:
    # Dry-run scan (default - reports orphans without deleting)
    python scripts/scan_orphan_files.py --dry-run

    # Perform actual cleanup of orphans older than 24 hours
    python scripts/scan_orphan_files.py --cleanup --age-hours 24

    # Custom age threshold
    python scripts/scan_orphan_files.py --dry-run --age-hours 48
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

sys.stdout.reconfigure(encoding="utf-8")

from app.database import async_session_factory
from app.services.cleanup_service import FileCleanupService


async def main():
    parser = argparse.ArgumentParser(description="WorkflowVdAi Orphan File Scanner & Cleanup Tool")
    parser.add_argument("--cleanup", action="store_true", help="Perform actual deletion of orphan files (default is dry-run)")
    parser.add_argument("--dry-run", action="store_true", help="Scan and report orphans without deleting (default)")
    parser.add_argument("--age-hours", type=float, default=24.0, help="Minimum age in hours for a file to be considered orphan (default: 24.0)")

    args = parser.parse_args()

    # Default to dry-run unless --cleanup is explicitly specified
    is_dry_run = not args.cleanup or args.dry_run

    print("\n========================================")
    print("WORKFLOWVDAI ORPHAN STORAGE SCANNER")
    print("========================================")
    print(f"Mode: {'DRY RUN (No files deleted)' if is_dry_run else 'CLEANUP MODE (Deleting orphans)'}")
    print(f"Age Threshold: {args.age_hours} hours")
    print("========================================\n")

    async with async_session_factory() as session:
        res = await FileCleanupService.scan_orphan_files(
            session=session,
            dry_run=is_dry_run,
            age_hours=args.age_hours,
        )

    from app.database import engine
    await engine.dispose()

    print("\n========================================")
    print("SCAN RESULT SUMMARY")
    print("========================================")
    print(f"Active DB Jobs:         {res['valid_jobs_count']}")
    print(f"Active DB Assets:       {res['valid_assets_count']}")
    print(f"Active DB Projects:     {res['valid_projects_count']}")
    print("----------------------------------------")
    print(f"Orphan Files Found:     {res['orphan_files_count']}")
    print(f"Orphan Directories:     {res['orphan_dirs_count']}")
    print(f"Orphan R2 Keys:         {res['orphan_r2_keys_count']}")
    print(f"Reclaimable Storage:    {res['reclaimable_mb']} MB ({res['reclaimable_bytes']} bytes)")

    if res.get("orphan_files"):
        print("\n--- SAMPLE ORPHAN FILES ---")
        for idx, item in enumerate(res["orphan_files"][:20], 1):
            sz_mb = item['size'] / (1024 * 1024)
            print(f"  {idx:02d}. [{item['reason']}] {item['path']} ({sz_mb:.2f} MB)")
        if len(res["orphan_files"]) > 20:
            print(f"  ... and {len(res['orphan_files']) - 20} more files.")

    if not is_dry_run:
        print(f"\n✅ CLEANUP COMPLETE: Deleted {res.get('deleted_dirs_count', 0)} orphan directories.")
    else:
        print("\nℹ️ Dry-run completed. To purge orphan files, run with '--cleanup'.")
    print("========================================\n")


if __name__ == "__main__":
    asyncio.run(main())
