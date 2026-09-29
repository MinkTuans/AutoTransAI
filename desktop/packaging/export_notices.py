"""Export actual installed dependency metadata and licenses into the payload."""
from __future__ import annotations
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]


def is_license(path: Path) -> bool:
    return path.name.lower().startswith(('license', 'licence', 'copying', 'notice', 'authors'))


def copy_licenses(package: Path, destination: Path) -> list[str]:
    copied = []
    for path in sorted(package.iterdir()):
        if not is_license(path) or path.is_symlink():
            continue
        candidates = [path] if path.is_file() else sorted(path.rglob('*'))
        for source in candidates:
            if not source.is_file() or source.is_symlink():
                continue
            relative = source.relative_to(package)
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
            copied.append(relative.as_posix())
    return copied


def export(destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    python = []
    for dist in sorted(importlib.metadata.distributions(), key=lambda d: d.metadata['Name'].lower()):
        name = dist.metadata['Name']
        licenses = []
        for item in dist.files or []:
            if not any(is_license(Path(part)) for part in item.parts):
                continue
            source = Path(dist.locate_file(item))
            if not source.is_file():
                continue
            # Flatten distribution paths to avoid traversing outside notices.
            filename = '__'.join(part for part in item.parts if part not in ('.', '..'))
            target = destination / 'python-licenses' / name / filename
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
            licenses.append(target.relative_to(destination).as_posix())
        python.append({'name': name, 'version': dist.version,
                       'license': dist.metadata.get('License-Expression') or dist.metadata.get('License'),
                       'project_urls': dist.metadata.get_all('Project-URL', []), 'license_files': licenses})
    (destination / 'python-inventory.json').write_text(json.dumps(python, indent=2) + '\n')
    cpython_license = Path(sys.base_prefix) / 'LICENSE.txt'
    if not cpython_license.is_file():
        cpython_license = Path(sys.base_prefix) / 'LICENSE'
    if not cpython_license.is_file():
        raise ValueError('Build interpreter CPython license file not found')
    shutil.copyfile(cpython_license, destination / 'CPython-LICENSE.txt')
    frontend = []
    lock = json.loads((ROOT / 'frontend/package-lock.json').read_text())
    for path, info in sorted(lock['packages'].items()):
        if not path or info.get('dev'):
            continue
        package = ROOT / 'frontend' / path
        metadata = json.loads((package / 'package.json').read_text())
        name = metadata['name']
        license_files = copy_licenses(package, destination / 'frontend-licenses' / name)
        frontend.append({'name': name, 'version': info['version'], 'integrity': info.get('integrity'),
                         'resolved': info.get('resolved'), 'license': metadata.get('license'),
                         'license_files': license_files})
    (destination / 'frontend-inventory.json').write_text(json.dumps(frontend, indent=2) + '\n')
    for name in ('requirements.lock', 'python-artifacts.json', 'runtime-manifest.json', 'version.txt'):
        shutil.copyfile(ROOT / 'desktop/packaging' / name, destination / name)
    # Deno 2.9.7 does not expose --license. Vendor staging already supplies
    # pinned source notices; recheck them before exporting the candidate.
    lock = json.loads((ROOT / 'desktop/packaging/vendor-lock.json').read_text())
    for item in lock['license_files']:
        notice = destination / item['name']
        if hashlib.sha256(notice.read_bytes()).hexdigest() != item['sha256']:
            raise ValueError(f"Vendor license checksum mismatch: {item['name']}")



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'build/desktop/notices')
    export(parser.parse_args().output)
