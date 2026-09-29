"""The package boundary rejects developer data and verifies all shipped bytes."""
import importlib.util
import json
from pathlib import Path
import zipfile

import pytest

ROOT = Path(__file__).resolve().parents[2]


def helper(name):
    path = ROOT / 'desktop' / 'packaging' / (name + '.py')
    assert path.exists(), f'{name} package boundary is required'
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_vendor_checksum_rejects_modified_download(tmp_path):
    vendor = helper('prepare_vendor')
    path = tmp_path / 'download'
    path.write_bytes(b'changed')
    with pytest.raises(ValueError, match='checksum'):
        vendor.verify_hash(path, '0' * 64)


def test_vendor_extracts_only_requested_members(tmp_path):
    vendor = helper('prepare_vendor')
    archive = tmp_path / 'tools.zip'
    with zipfile.ZipFile(archive, 'w') as handle:
        handle.writestr('build/bin/ffmpeg.exe', b'MZbinary')
        handle.writestr('../../escape.exe', b'untrusted')
    target = tmp_path / 'ffmpeg.exe'
    vendor.extract_member(archive, 'bin/ffmpeg.exe', target)
    assert target.read_bytes() == b'MZbinary'
    assert not (tmp_path.parent / 'escape.exe').exists()


def test_vendor_extract_rejects_ambiguous_member(tmp_path):
    vendor = helper('prepare_vendor')
    archive = tmp_path / 'tools.zip'
    with zipfile.ZipFile(archive, 'w') as handle:
        handle.writestr('a/deno.exe', b'a')
        handle.writestr('b/deno.exe', b'b')
    with pytest.raises(ValueError, match='exactly one'):
        vendor.extract_member(archive, 'deno.exe', tmp_path / 'deno.exe')


@pytest.mark.parametrize('name', ['.env', '.env.production', 'desktop.env', '_internal/desktop.env', 'data/workflow.db', 'storage/video.mp4', 'api_keys.json', 'private.pem', '.git/config', 'backend/tests/test_secret.py'])
def test_payload_audit_rejects_developer_files(tmp_path, name):
    audit = helper('verify_payload')
    path = tmp_path / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('not a real secret')
    with pytest.raises(ValueError, match='Forbidden'):
        audit.audit_paths(tmp_path)


def test_payload_inventory_detects_tampering(tmp_path):
    audit = helper('verify_payload')
    (tmp_path / 'AutoTransAI.exe').write_bytes(b'MZapp')
    audit.write_inventory(tmp_path)
    audit.verify_inventory(tmp_path)
    (tmp_path / 'AutoTransAI.exe').write_bytes(b'MZchanged')
    with pytest.raises(ValueError, match='mismatch'):
        audit.verify_inventory(tmp_path)


def test_vendor_lock_has_pinned_release_and_verified_digest():
    lock = json.loads((ROOT / 'desktop/packaging/vendor-lock.json').read_text())
    assert len(lock['assets']) == 3
    for item in lock['assets']:
        assert '/latest/' not in item['url']
        assert len(item['sha256']) == 64
        assert item['provenance'].startswith('https://api.github.com/repos/')


def test_dependency_license_export_keeps_license_text_only(tmp_path):
    exporter = helper('export_notices')
    package = tmp_path / 'package'
    package.mkdir()
    (package / 'LICENSE').write_text('MIT terms')
    (package / '.env').write_text('sensitive')
    (package / 'index.js').write_text('source')
    destination = tmp_path / 'notices'
    copied = exporter.copy_licenses(package, destination)
    assert copied == ['LICENSE']
    assert (destination / 'LICENSE').read_text() == 'MIT terms'
    assert not (destination / '.env').exists()


def test_payload_requires_x64_webview_loader(tmp_path):
    audit = helper('verify_payload')
    for name in audit.REQUIRED:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b'fixture')
    for name in ['_internal/webview/lib/Microsoft.Web.WebView2.Core.dll',
                 '_internal/webview/lib/Microsoft.Web.WebView2.WinForms.dll',
                 '_internal/pythonnet/runtime/Python.Runtime.dll',
                 '_internal/webview/lib/runtimes/win-x86/native/WebView2Loader.dll']:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b'fixture')
    audit.write_inventory(tmp_path)
    with pytest.raises(ValueError, match='win-x64'):
        audit.verify(tmp_path)


@pytest.mark.parametrize('license_state', ['valid', 'missing', 'modified'])
def test_notice_export_uses_hash_verified_vendor_license_without_cli(tmp_path, monkeypatch, license_state):
    """Deno 2.9.7 has no --license flag; retain its pinned source notice."""
    import hashlib

    exporter = helper('export_notices')
    root = tmp_path / 'repo'
    packaging = root / 'desktop/packaging'
    packaging.mkdir(parents=True)
    for name in ('requirements.lock', 'python-artifacts.json', 'runtime-manifest.json', 'version.txt'):
        (packaging / name).write_text('{}')
    license_bytes = b'MIT license fixture\n'
    (packaging / 'vendor-lock.json').write_text(json.dumps({'license_files': [{
        'name': 'deno-LICENSE.txt', 'sha256': hashlib.sha256(license_bytes).hexdigest(),
    }]}))
    frontend = root / 'frontend'
    frontend.mkdir()
    (frontend / 'package-lock.json').write_text('{"packages": {}}')
    interpreter = tmp_path / 'interpreter'
    interpreter.mkdir()
    (interpreter / 'LICENSE.txt').write_text('CPython license fixture')
    destination = tmp_path / 'notices'
    destination.mkdir()
    if license_state != 'missing':
        (destination / 'deno-LICENSE.txt').write_bytes(
            license_bytes if license_state == 'valid' else b'tampered')
    monkeypatch.setattr(exporter, 'ROOT', root)
    monkeypatch.setattr(exporter.sys, 'base_prefix', str(interpreter))
    monkeypatch.setattr(exporter.importlib.metadata, 'distributions', lambda: [])
    if license_state == 'valid':
        exporter.export(destination)
        assert (destination / 'deno-LICENSE.txt').read_bytes() == license_bytes
        assert json.loads((destination / 'python-inventory.json').read_text()) == []
    elif license_state == 'missing':
        with pytest.raises(FileNotFoundError, match='deno-LICENSE'):
            exporter.export(destination)
    else:
        with pytest.raises(ValueError, match='Vendor license checksum mismatch'):
            exporter.export(destination)


def test_frozen_smoke_preserves_bounded_failure_log_before_temp_cleanup(tmp_path, monkeypatch, capsys):
    smoke = helper('smoke_frozen')
    monkeypatch.setattr(smoke.sys, 'platform', 'win32')
    stopped = []

    class FailingManager:
        def __init__(self, command, resources, data):
            self.log_dir = data / 'logs'
            self.log_dir.mkdir()
            (self.log_dir / 'backend.log').write_text('old log\n' * 1000 + 'diagnostic tail\n')

        def start(self):
            raise RuntimeError('failed readiness')

        def stop(self):
            stopped.append(True)

        def is_running(self):
            return False

    monkeypatch.setattr(smoke, 'BackendManager', FailingManager)
    with pytest.raises(RuntimeError, match='failed readiness'):
        smoke.main(tmp_path)
    output = capsys.readouterr().out
    assert 'diagnostic tail' in output
    assert len(output) < 4500
    assert stopped


@pytest.mark.parametrize('dialect_name', ['sqlite.aiosqlite', 'mysql.aiomysql', 'mysql.pymysql'])
def test_freezer_includes_dbapi_loaded_dynamically_by_sqlalchemy(monkeypatch, dialect_name):
    """Check the spec against actual dialect imports; native smoke remains required."""
    import ast
    import builtins
    import importlib
    import sys

    dialect = importlib.import_module('sqlalchemy.dialects.' + dialect_name).dialect
    loader = dialect.import_dbapi.__func__
    direct_imports = set()
    original_import = builtins.__import__

    def track_import(name, *args, **kwargs):
        if sys._getframe(1).f_code is loader.__code__:
            direct_imports.add(name)
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, '__import__', track_import)
    dialect.import_dbapi()
    external_drivers = direct_imports - sys.stdlib_module_names
    assert external_drivers, 'Dialect no longer uses this dynamic-import contract'
    spec = ast.parse((ROOT / 'desktop/packaging/autotransai.spec').read_text())
    explicit_imports = set()
    for node in spec.body:
        if isinstance(node, ast.AugAssign) and isinstance(node.target, ast.Name) and node.target.id == 'hiddenimports':
            explicit_imports.update(ast.literal_eval(node.value))
    assert external_drivers <= explicit_imports, f'Unbundled dynamic DBAPI: {external_drivers - explicit_imports}'
