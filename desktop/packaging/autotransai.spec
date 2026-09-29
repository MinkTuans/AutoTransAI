# PyInstaller 6 onedir / windowed entrypoint; run from the repository root.
from pathlib import Path
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, copy_metadata

root = Path(SPECPATH).resolve().parents[1]
sys.path[:0] = [str(root), str(root / 'backend')]
# Hook discovery imports package modules. Give those subprocesses disposable
# desktop configuration before any app import; never discover source .env.
from desktop.paths import configure_environment
configure_environment(root, root / 'build/desktop/analysis-data')
version = (root / 'desktop/packaging/version.txt').read_text().strip()
notices = root / 'build/desktop/notices'
required = [root / 'frontend/dist/index.html', notices / 'python-inventory.json',
            notices / 'frontend-inventory.json']
required += [root / 'bin' / (name + '.exe') for name in ('ffmpeg', 'ffprobe', 'yt-dlp', 'deno')]
for path in required:
    if not path.is_file():
        raise SystemExit(f'Required build input missing: {path}')

def files_in(source, destination):
    # Only known immutable sources; never recurse through the repository itself.
    files = []
    for p in source.rglob('*'):
        if p.is_symlink():
            raise SystemExit(f'Symlink build input rejected: {p}')
        if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ('.pyc', '.pyo'):
            files.append((str(p), str(Path(destination) / p.relative_to(source).parent)))
    return files

datas = files_in(root / 'frontend/dist', 'frontend/dist')
datas += [(str(root / 'frontend/public/app-logo.ico'), 'frontend/public')]
# Frozen app.database is _internal/app/database.py; its sibling is /alembic.
# Resource-root backend/alembic is also retained for tooling and runtime contract.
datas += files_in(root / 'backend/alembic', 'alembic')
datas += files_in(root / 'backend/alembic', 'backend/alembic')
datas += files_in(notices, 'notices')
datas += collect_data_files('webview', includes=['lib/*', 'lib/**/*', 'js/*', 'js/**/*'])
datas += collect_data_files('googleapiclient', includes=['discovery_cache/documents/youtube.v3.json'])
for name in ('pywebview', 'pythonnet', 'edge-tts', 'google-api-python-client', 'sse-starlette'):
    datas += copy_metadata(name)
binaries = [(str(root / 'bin' / (name + '.exe')), 'bin')
            for name in ('ffmpeg', 'ffprobe', 'yt-dlp', 'deno')]
hiddenimports = collect_submodules('app') + collect_submodules('desktop', filter=lambda name: '.tests' not in name and '.packaging' not in name)
hiddenimports += ['webview.platforms.winforms', 'webview.platforms.edgechromium',
                  'uvicorn.logging', 'uvicorn.loops.asyncio', 'uvicorn.protocols.http.h11_impl',
                  'uvicorn.lifespan.on', 'sqlalchemy.dialects.sqlite.aiosqlite',
                  'sqlalchemy.dialects.mysql.aiomysql', 'sqlalchemy.dialects.mysql.pymysql',
                  # SQLAlchemy dialects load DBAPI packages through __import__.
                  'aiosqlite', 'aiomysql', 'pymysql',
                  'alembic', 'alembic.migration', 'alembic.operations', 'clr', 'pythonnet']
a = Analysis([str(root / 'desktop/__main__.py')], pathex=[str(root), str(root / 'backend')],
             binaries=binaries, datas=datas, hiddenimports=hiddenimports,
             hookspath=[], runtime_hooks=[], excludes=['pytest', 'tkinter', 'unittest', 'IPython'],
             noarchive=False)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name='AutoTransAI',
          debug=False, bootloader_ignore_signals=False, strip=False, upx=False,
          console=False, disable_windowed_traceback=False,
          icon=str(root / 'frontend/public/app-logo.ico'),
          version=str(root / 'build/desktop/version-info.txt'))
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name='AutoTransAI')
