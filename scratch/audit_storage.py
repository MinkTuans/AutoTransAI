import re
import os
from pathlib import Path

backend_dir = Path("backend")
matches = []

patterns = [
    r'data/[a-zA-Z0-9_\-/]+',
    r'storage_service',
    r'upload_file',
    r'download_file',
    r'delete_file',
    r'get_url',
    r'R2StorageService',
    r'PROJECTS_DIR',
    r'DATA_DIR',
]

for root, dirs, files in os.walk(backend_dir):
    for f in files:
        if f.endswith(".py"):
            fp = Path(root) / f
            content = fp.read_text(encoding="utf-8", errors="ignore")
            for p in patterns:
                found = re.findall(p, content)
                if found:
                    matches.append((str(fp), p, len(found)))

for fp, pat, cnt in matches:
    print(f"{fp} => Pattern '{pat}': {cnt} matches")
