# Local Translation Storage Audit & R2 Storage Migration Analysis

## Overview

This document provides a comprehensive audit of local storage usage in the `Video Translator` pipeline (`data/translator/`), comparing permanent storage in **Cloudflare R2** vs temporary local processing files.

---

## 1. Directory Structure Audit (`data/translator/`)

Currently, local files are stored under `data/translator/` in two main subdirectories:

```text
data/
└── translator/
    ├── assets/
    │   └── {asset_id}/
    │       ├── raw_input_{asset_id}.mp4   (Duplicate raw download/upload file)
    │       └── input_source.mp4          (Standardized input video)
    └── jobs/
        └── {job_id}/
            ├── job.log                   (Real-time structured event log)
            ├── extracted_audio.wav       (Extracted 16kHz mono audio track)
            ├── tts/                      (Raw TTS audio segments seg_XXX.wav)
            ├── synced/                   (Time-stretched audio segments seg_XXX_synced.wav)
            ├── work/                     (FFmpeg concatenation & render work dir)
            └── final_dubbed_video.mp4    (Final output dubbed video)
```

---

## 2. File Lifecycle Trace

| File Path | Created By | Primary Consumer | Uploaded to R2? | Cleanup Status | Local Retention Needed? |
|---|---|---|---|---|---|
| `assets/{asset_id}/raw_input_*.mp4` | Ingest Route | FFmpeg standardize | NO | NEVER DELETED | **NO** (Duplicate file) |
| `assets/{asset_id}/input_source.mp4` | Ingest Route | Audio Extraction | YES (`translator/assets/{id}/...`) | Permanent local | **NO** (R2 is source of truth; download on-demand) |
| `jobs/{job_id}/extracted_audio.wav` | Audio Extraction | STT Service | NO | NOT DELETED (Typo bug `.mp3` vs `.wav`) | **NO** (Temporary processing) |
| `jobs/{job_id}/tts/seg_*.wav` | TTS Service | Audio Sync Service | NO | Deleted on success, kept on failure | **NO** (Temporary processing) |
| `jobs/{job_id}/synced/seg_*_synced.wav` | Sync Service | FFmpeg Render | NO | Deleted on success, kept on failure | **NO** (Temporary processing) |
| `jobs/{job_id}/work/*` | Render Service | FFmpeg process | NO | Deleted on success, kept on failure | **NO** (Temporary processing) |
| `jobs/{job_id}/final_dubbed_video.mp4` | Render Service | Frontend Player | YES (`translator/jobs/{id}/...`) | KEPT LOCALLY | **NO** (R2 is source of truth; stream from R2) |
| `jobs/{job_id}/job.log` | Job Logger | Frontend Progress Log | NO | Kept for audit | **YES** (Lightweight text log) |

---

## 3. Identification of Storage Flaws & Bugs

### Flaw A: Extension Typo in Cleanup Routine
In [`backend/app/api/routes/video_translator.py`](file:///c:/Hack/WorkflowVdAi/backend/app/api/routes/video_translator.py#L885):
```python
extracted_audio = job_dir / "extracted_audio.mp3"
if extracted_audio.exists():
    extracted_audio.unlink(missing_ok=True)
```
The audio extraction step produces `extracted_audio.wav`. Because the cleanup routine looks for `extracted_audio.mp3`, the temporary WAV file (~70MB for a 38-minute video) is **never deleted**, accumulating disk space over time.

### Flaw B: Duplicate Ingest Video Asset File
When a video is uploaded or downloaded from a URL, both `raw_input_{asset_id}.mp4` and `input_source.mp4` are saved in `data/translator/assets/{asset_id}/`. `raw_input_*` is never deleted after `input_source.mp4` is created.

### Flaw C: Permanent Local Copy of Rendered Output Video
`final_dubbed_video.mp4` is uploaded to Cloudflare R2 (`storage_service.upload_file`), but the local file is left permanently on disk in `data/translator/jobs/{job_id}/final_dubbed_video.mp4`.

### Flaw D: Failed/Cancelled Job Orphaning
If a job fails or is cancelled mid-pipeline, no cleanup routine is executed, leaving all intermediate TTS segments (`tts/`), time-stretched audio (`synced/`), and FFmpeg temporary files (`work/`) on disk.

---

## 4. Target Architecture & Storage Strategy

```text
                                ┌───────────────────┐
                                │    Cloudflare R2  │
                                │ (Source of Truth) │
                                └─────────┬─────────┘
                                          │
                   ┌──────────────────────┴──────────────────────┐
                   │                                             │
                   ▼                                             ▼
        translator/assets/{id}/                        translator/jobs/{id}/
           input_source.mp4                           final_dubbed_video.mp4
                   │                                             ▲
                   │ (Download on-demand if needed)              │ (Upload on finish)
                   ▼                                             │
      ┌──────────────────────────────────────────────────────────┴────────┐
      │                   Local Temporary Workspace                       │
      │                  (data/translator/jobs/{job_id}/)                 │
      │                                                                   │
      │  - extracted_audio.wav   (Temporary)                              │
      │  - tts/*.wav             (Temporary)                              │
      │  - synced/*.wav          (Temporary)                              │
      │  - work/*                (Temporary)                              │
      │  - job.log               (Persistent text log)                    │
      └───────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
                             AUTOMATIC CLEANUP ON FINISH/FAIL
```

---

## 5. Action Items & Cleanup Policy

1. **Fix Audio Cleanup Typo**: Change `"extracted_audio.mp3"` to `"extracted_audio.wav"` in pipeline cleanup.
2. **Clean Duplicate Raw Input**: Delete `raw_input_{asset_id}.mp4` immediately after FFmpeg standardization finishes.
3. **Purge Intermediate Processing Files**: Ensure `extracted_audio.wav`, `tts/`, `synced/`, `work/`, and local `final_dubbed_video.mp4` are deleted after R2 upload succeeds.
4. **Implement Global Job Cleanup Utility**: Create `cleanup_job_workspace(job_id, keep_log=True)` to clean up failed/cancelled jobs as well as completed jobs.
5. **Run Storage Maintenance Script**: Provide a script to purge legacy temporary files from active/completed test jobs.
