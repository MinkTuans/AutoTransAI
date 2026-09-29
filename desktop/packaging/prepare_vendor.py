"""Fetch pinned Windows runtime tools; extract only explicitly named members."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import urllib.request
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def verify_hash(path: Path, expected: str) -> None:
    with path.open('rb') as stream:
        actual = hashlib.file_digest(stream, 'sha256').hexdigest()
    if actual != expected:
        raise ValueError(f'Vendor checksum mismatch: {path.name}')


def download(url: str, checksum: str, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists():
        temporary = destination.with_suffix(destination.suffix + '.part')
        request = urllib.request.Request(url, headers={'User-Agent': 'AutoTransAI-desktop-build/0.1'})
        with urllib.request.urlopen(request, timeout=120) as source, temporary.open('wb') as target:
            shutil.copyfileobj(source, target)
        verify_hash(temporary, checksum)
        temporary.replace(destination)
    verify_hash(destination, checksum)
    return destination


def extract_member(archive: Path, suffix: str, destination: Path) -> None:
    with zipfile.ZipFile(archive) as handle:
        names = [name for name in handle.namelist() if name == suffix or name.endswith('/' + suffix)]
        if len(names) != 1:
            raise ValueError(f'Expected exactly one {suffix} in {archive.name}')
        # No extractall: archive-controlled paths never become filesystem paths.
        destination.parent.mkdir(parents=True, exist_ok=True)
        with handle.open(names[0]) as source, destination.open('wb') as target:
            shutil.copyfileobj(source, target)


def prepare(bin_dir: Path, notices_dir: Path, cache: Path) -> None:
    lock = json.loads((HERE / 'vendor-lock.json').read_text())
    bin_dir.mkdir(parents=True, exist_ok=True)
    notices_dir.mkdir(parents=True, exist_ok=True)
    for asset in lock['assets']:
        filename = asset['url'].rsplit('/', 1)[-1]
        archive = download(asset['url'], asset['sha256'], cache / filename)
        if asset['name'] == 'codexffmpeg':
            for name in ('ffmpeg', 'ffprobe'):
                extract_member(archive, f'bin/{name}.exe', bin_dir / f'{name}.exe')
            extract_member(archive, 'LICENSE', notices_dir / 'ffmpeg-LICENSE.txt')
            extract_member(archive, 'README.txt', notices_dir / 'ffmpeg-README.txt')
        elif asset['name'] == 'deno':
            extract_member(archive, 'deno.exe', bin_dir / 'deno.exe')
        elif asset['name'] == 'yt-dlp':
            shutil.copyfile(archive, bin_dir / 'yt-dlp.exe')
        else:
            raise ValueError('Unrecognized vendor asset')
    for item in lock['license_files']:
        source = download(item['url'], item['sha256'], cache / item['name'])
        shutil.copyfile(source, notices_dir / item['name'])
    shutil.copyfile(HERE / 'vendor-lock.json', notices_dir / 'vendor-lock.json')
    shutil.copyfile(HERE / 'THIRD_PARTY_NOTICES.md', notices_dir / 'THIRD_PARTY_NOTICES.md')
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(bin_dir.glob('*.exe'))}
    (notices_dir / 'vendor-binaries.json').write_text(json.dumps(hashes, indent=2) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bin-dir', type=Path, default=ROOT / 'bin')
    parser.add_argument('--notices-dir', type=Path, default=ROOT / 'build/desktop/notices')
    parser.add_argument('--cache', type=Path, default=ROOT / '.desktop-cache')
    args = parser.parse_args()
    prepare(args.bin_dir, args.notices_dir, args.cache)
