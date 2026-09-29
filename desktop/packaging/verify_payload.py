"""Fail closed if a desktop distribution contains private or unexpected payloads."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

INVENTORY = 'payload-sha256.json'
FORBIDDEN_PARTS = {'.git', '.venv', 'venv', 'node_modules', '.worktrees', 'storage', 'logs', 'tests'}
FORBIDDEN_SUFFIXES = {'.db', '.sqlite', '.sqlite3', '.pem', '.key', '.pfx', '.p12', '.log'}
REQUIRED = tuple(json.loads((Path(__file__).resolve().parent / 'runtime-manifest.json').read_text())['required_files'])


def audit_paths(root: Path) -> None:
    for path in root.rglob('*'):
        relative = path.relative_to(root)
        parts = {part.lower() for part in relative.parts}
        name = path.name.lower()
        # Legitimate third-party packages contain directories named data. Only
        # reject application-owned runtime data locations, not package resources.
        application_data = relative.as_posix().lower().startswith(('data/', 'backend/data/', '_internal/data/', '_internal/backend/data/'))
        if (path.is_symlink() or parts & FORBIDDEN_PARTS or application_data or
                name.startswith('.env') or name in {'desktop.env', 'api_keys.json', 'encryption.key'} or
                path.suffix.lower() in FORBIDDEN_SUFFIXES):
            # certifi's public CA bundle is a required trusted runtime resource.
            if relative.as_posix() == '_internal/certifi/cacert.pem' and not path.is_symlink():
                continue
            raise ValueError(f'Forbidden payload path: {relative}')


def hashes(root: Path) -> dict[str, str]:
    result = {}
    for path in sorted(root.rglob('*')):
        if path.is_file() and path.relative_to(root).as_posix() != INVENTORY:
            with path.open('rb') as stream:
                result[path.relative_to(root).as_posix()] = hashlib.file_digest(stream, 'sha256').hexdigest()
    return result


def write_inventory(root: Path) -> None:
    audit_paths(root)
    (root / INVENTORY).write_text(json.dumps(hashes(root), indent=2, sort_keys=True) + '\n')


def verify_inventory(root: Path) -> None:
    expected = json.loads((root / INVENTORY).read_text())
    if expected != hashes(root):
        raise ValueError('Payload inventory mismatch (added, removed or changed file)')


def verify(root: Path) -> None:
    audit_paths(root)
    for name in REQUIRED:
        if not (root / name).is_file():
            raise ValueError(f'Required payload file missing: {name}')
    # Each native WebView2 integration component must actually be packaged.
    loader = root / '_internal/webview/lib/runtimes/win-x64/native/WebView2Loader.dll'
    if not loader.is_file():
        raise ValueError('Required win-x64 WebView2Loader.dll missing')
    for name in ('Microsoft.Web.WebView2.Core.dll', 'Microsoft.Web.WebView2.WinForms.dll', 'Python.Runtime.dll'):
        if not any(root.rglob(name)):
            raise ValueError(f'Required native renderer component missing: {name}')
    verify_inventory(root)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('--write', action='store_true', help='Generate inventory before verification')
    args = parser.parse_args()
    if args.write:
        write_inventory(args.directory)
    verify(args.directory)
    print('Desktop payload inventory and private-data audit passed.')
