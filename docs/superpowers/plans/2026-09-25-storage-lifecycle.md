# Storage Lifecycle Implementation Plan

## Goal

Keep resumable inputs and workspaces while translation is incomplete. After a verified final result is persisted, retain the result and referenced thumbnails while removing the job workspace, logs, extracted audio, and source media no longer needed by another unfinished job. Deleting a project must delete its linked translation jobs and files. Runtime storage must not be committed to Git.

## Tasks

1. Add focused tests for completed cleanup, shared source preservation, and project deletion with linked jobs. Run them red.
2. Put translated output outside the disposable job workspace, update the stored result path, and clean the workspace only after output and optional thumbnail processing finish.
3. Extend project deletion to remove linked translation jobs. Keep existing asset reference counting and thumbnail references safe.
4. Ignore runtime storage paths; remove already tracked runtime files from Git. Back up existing local files, then delete only DB-unreferenced directories.
5. Run focused and regression tests, update the knowledge base and changelog, inspect the final diff and storage inventory.

## Safety rules

- Never delete a source while an unfinished job references it.
- Never delete a completed result until its parent project or job is deleted.
- Do not use folder age alone as proof of an orphan; check database references and preserve current project data.
- Avoid changing the current DATA_DIR/STORAGE_ROOT defaults while existing data is still stored at those paths.
