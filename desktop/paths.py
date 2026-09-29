"""Immutable payload and private per-user directories for desktop mode."""
from __future__ import annotations

import os
from pathlib import Path
import sys


def resource_root() -> Path:
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS).resolve()
    return Path(__file__).resolve().parents[1]


def data_root() -> Path:
    local = os.environ.get('LOCALAPPDATA')
    if not local:
        raise RuntimeError('LOCALAPPDATA is unavailable; desktop requires a Windows user profile')
    return Path(local).resolve() / 'AutoTransAI'


def configure_environment(resources: Path, writable: Path) -> None:
    """Run once in the dedicated child, before any backend imports.

    Preserve only OS runtime inputs. Inherited application settings, numbered API
    keys, dotenv paths and database URLs must never configure a desktop install.
    """
    resources, writable = resources.resolve(), writable.resolve()
    keep = {'SYSTEMROOT', 'WINDIR', 'COMSPEC', 'SYSTEMDRIVE', 'TEMP', 'TMP',
            'USERPROFILE', 'APPDATA', 'LOCALAPPDATA', 'PROGRAMDATA', 'PROGRAMFILES',
            'PROGRAMFILES(X86)', 'COMMONPROGRAMFILES', 'PATH', 'PATHEXT',
            'LANG', 'LC_ALL', 'LC_CTYPE', 'HOME'}
    for name in list(os.environ):
        if name.upper() not in keep:
            del os.environ[name]
    os.environ.update(AUTOTRANSAI_DESKTOP='1',
                      AUTOTRANSAI_RESOURCE_ROOT=str(resources),
                      AUTOTRANSAI_DATA_ROOT=str(writable))
    os.environ['PATH'] = str(resources / 'bin') + os.pathsep + os.environ.get('PATH', '')
    for name in ('data', 'storage', 'logs', 'webview'):
        (writable / name).mkdir(parents=True, exist_ok=True)
    os.environ.update(load_oauth_config(writable / 'data' / 'desktop.env'))


def load_oauth_config(path: Path) -> dict[str, str]:
    """Read only explicit private OAuth settings, without interpolation or search.

    Unknown/malformed entries fail closed. Values never appear in errors.
    Database, filesystem roots, redirects, ports and provider keys are excluded.
    """
    if not path.exists():
        return {}
    import io
    from dotenv.parser import parse_stream
    allowed = {'YOUTUBE_CLIENT_ID', 'YOUTUBE_CLIENT_SECRET', 'TIKTOK_CLIENT_KEY',
               'TIKTOK_CLIENT_SECRET', 'TIKTOK_SCOPES'}
    try:
        with path.open('rb') as stream:
            raw = stream.read(16385)
        if len(raw) > 16384:
            raise ValueError
        result = {}
        for entry in parse_stream(io.StringIO(raw.decode('utf-8-sig'))):
            if entry.error:
                raise ValueError
            if entry.key is None:
                continue
            if entry.key not in allowed or entry.key in result or entry.value is None or '\x00' in entry.value:
                raise ValueError
            result[entry.key] = entry.value
        return result
    except (OSError, UnicodeError, ValueError):
        raise ValueError('Invalid private data/desktop.env. Use only the documented OAuth client settings.') from None
