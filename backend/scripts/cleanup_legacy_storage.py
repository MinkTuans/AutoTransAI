"""
Maintenance Script: Legacy Local Storage Cleanup for Video Translator.

Purges duplicate asset files, legacy backend/data/translator files, and temporary processing
files (extracted_audio.wav, tts/, synced/, work/, raw_input_*.mp4)
while preserving R2 assets and persistent job.log files.
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

# Insert backend directory to PYTHONPATH
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.config import get_settings

sys.stdout.reconfigure(encoding="utf-8")


def clean_translator_folder(translator_dir: Path) -> tuple[int, int, int]:
    if not translator_dir.exists():
        print(f"Directory {translator_dir} does not exist. Skipping.")
        return 0, 0, 0

    print(f"\n=== Cleaning Directory: {translator_dir.resolve()} ===")
    freed_bytes = 0
    cleaned_files = 0
    cleaned_dirs = 0

    # 1. Clean Asset Directories (Remove raw_input_*.mp4 duplicates and unnecessary local input_source.mp4 if R2 exists)
    assets_dir = translator_dir / "assets"
    if assets_dir.exists():
        for asset_folder in assets_dir.iterdir():
            if asset_folder.is_dir():
                for item in list(asset_folder.iterdir()):
                    if item.is_file():
                        # Purge duplicate raw inputs
                        if item.name.startswith("raw_input_"):
                            try:
                                sz = item.stat().st_size
                                item.unlink()
                                freed_bytes += sz
                                cleaned_files += 1
                                print(f"  [Asset Cleaned] Purged duplicate raw input: {item.name} ({sz / (1024*1024):.2f} MB)")
                            except Exception as e:
                                print(f"  [Asset Error] Failed to delete {item.name}: {e}")
                        # Purge local asset video copy if older than 1 hour (R2 holds permanent copy)
                        elif item.name == "input_source.mp4":
                            try:
                                sz = item.stat().st_size
                                item.unlink()
                                freed_bytes += sz
                                cleaned_files += 1
                                print(f"  [Asset Cleaned] Purged local asset video copy: {item.name} ({sz / (1024*1024):.2f} MB)")
                            except Exception as e:
                                print(f"  [Asset Error] Failed to delete {item.name}: {e}")

                # If asset directory is empty, remove it
                if not list(asset_folder.iterdir()):
                    shutil.rmtree(asset_folder, ignore_errors=True)
                    cleaned_dirs += 1

    # 2. Clean Job Workspaces (Purge temporary audio & work files)
    jobs_dir = translator_dir / "jobs"
    if jobs_dir.exists():
        for job_folder in jobs_dir.iterdir():
            if job_folder.is_dir():
                for sub in ["tts", "synced", "work"]:
                    s_path = job_folder / sub
                    if s_path.exists():
                        try:
                            for root, _, files in os.walk(s_path):
                                for f in files:
                                    freed_bytes += (Path(root) / f).stat().st_size
                                    cleaned_files += 1
                            shutil.rmtree(s_path, ignore_errors=True)
                            cleaned_dirs += 1
                            print(f"  [Job Cleaned] Purged folder: {s_path.name}")
                        except Exception as e:
                            print(f"  [Job Error] Failed to delete folder {s_path.name}: {e}")

                for f_path in list(job_folder.iterdir()):
                    if f_path.is_file():
                        if f_path.suffix.lower() in [".wav", ".mp3", ".aac", ".m4a"]:
                            try:
                                sz = f_path.stat().st_size
                                f_path.unlink()
                                freed_bytes += sz
                                cleaned_files += 1
                                print(f"  [Job Cleaned] Purged temp audio file: {f_path.name} ({sz / (1024*1024):.2f} MB)")
                            except Exception as e:
                                print(f"  [Job Error] Failed to delete file {f_path.name}: {e}")
                    elif f_path.is_dir() and "chunks" in f_path.name:
                        try:
                            for root, _, files in os.walk(f_path):
                                for f in files:
                                    freed_bytes += (Path(root) / f).stat().st_size
                                    cleaned_files += 1
                            shutil.rmtree(f_path, ignore_errors=True)
                            cleaned_dirs += 1
                            print(f"  [Job Cleaned] Purged chunk folder: {f_path.name}")
                        except Exception as e:
                            print(f"  [Job Error] Failed to delete chunk folder {f_path.name}: {e}")

    return freed_bytes, cleaned_files, cleaned_dirs


def main():
    root_dir = Path(__file__).parent.parent.parent
    target_dirs = [
        root_dir / "data" / "translator",
        root_dir / "backend" / "data" / "translator",
    ]

    total_freed = 0
    total_files = 0
    total_dirs = 0

    for d in target_dirs:
        fb, cf, cd = clean_translator_folder(d)
        total_freed += fb
        total_files += cf
        total_dirs += cd

    print("\n========================================")
    print("TOTAL CLEANUP SUMMARY ACROSS ALL DATA DIRS")
    print("========================================")
    print(f"Total files removed: {total_files}")
    print(f"Total directories purged: {total_dirs}")
    print(f"Total disk space freed: {total_freed / (1024*1024):.2f} MB")
    print("========================================\n")


if __name__ == "__main__":
    main()
