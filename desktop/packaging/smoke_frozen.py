"""Windows-only real frozen backend lifecycle smoke test using disposable data.

This proves neither GUI rendering nor installer acceptance. The supervisor's
Windows Job Object is exercised; no existing server is attached to or killed.
"""
from pathlib import Path
import argparse
import http.cookiejar
import tempfile
import urllib.error
import urllib.request
import sys
import json
import os
import sqlite3
import socket
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from desktop.process_manager import BackendManager


def validate_data_root(root: Path, temporary: Path) -> Path:
    root = root.resolve()
    workspace = root.parent.parent
    if (not workspace.is_relative_to(temporary.resolve()) or workspace == temporary.resolve()
            or not workspace.name.startswith('AutoTransAI installed ')
            or root.relative_to(workspace).as_posix() != 'profile/AutoTransAI'
            or not (workspace / '.installed-smoke').is_file()
            or (workspace / '.installed-smoke').read_text().strip() != 'AutoTransAI installed acceptance'):
        raise ValueError('Expected explicitly disposable installed-smoke data root')
    return root


def run_cycle(payload: Path, data: Path, previous_client=None):
    manager = BackendManager([str(payload / 'AutoTransAI.exe')], payload / '_internal', data)
    owned = None
    try:
        started = time.monotonic()
        url = manager.start()
        startup = time.monotonic() - started
        owned = manager._process
        if previous_client is not None:
            try:
                previous_client.open('http://127.0.0.1:8000/api/system/health', timeout=5)
                raise AssertionError('Previous session survived restart')
            except urllib.error.HTTPError as error:
                assert error.code == 401
        try:
            urllib.request.urlopen('http://127.0.0.1:8000/', timeout=5)
            raise AssertionError('Anonymous UI request was allowed')
        except urllib.error.HTTPError as error:
            assert error.code == 401
        client = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        with client.open(url, timeout=10) as response:
            assert response.status == 200
            assert b'<html' in response.read().lower()
        with client.open('http://127.0.0.1:8000/api/system/health', timeout=5) as response:
            assert response.status == 200
        assert manager.is_running()
    except Exception:
        # Disposable smoke data only. The supervisor redacts handshake tokens
        # before writing this log; preserve a bounded tail before temp cleanup.
        log = manager.log_dir / 'backend.log'
        try:
            with log.open('rb') as stream:
                stream.seek(max(0, log.stat().st_size - 2048))
                print('Frozen backend log tail:', stream.read(2048).decode('utf-8', errors='replace'))
        except OSError:
            print('Frozen backend log unavailable.')
        raise
    finally:
        stopping = time.monotonic()
        manager.stop()
        shutdown = time.monotonic() - stopping
        if owned is not None and owned.poll() is None:
            raise AssertionError("Owned process survived shutdown")
        if manager.is_running():
            raise AssertionError('Owned frozen backend survived shutdown')
    return {'startup_seconds': startup, 'shutdown_seconds': shutdown,
            'owned_backend_exited': True}, client


def run_failure_checks(payload: Path, data: Path):
    # Bind the same loopback port ourselves; never attach to an arbitrary listener.
    listener = socket.socket()
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
    listener.bind(('127.0.0.1', 8000))
    listener.listen(1)
    manager = BackendManager([str(payload / 'AutoTransAI.exe')], payload / '_internal', data)
    try:
        try:
            manager.start()
        except Exception:
            pass
        else:
            raise AssertionError('Foreign owned listener was accepted')
        with socket.create_connection(('127.0.0.1', 8000), timeout=2):
            connection, _ = listener.accept()
            connection.close()
    finally:
        manager.stop()
        listener.close()
    # A crash of our exact backend process is reaped by the supervisor.
    manager = BackendManager([str(payload / 'AutoTransAI.exe')], payload / '_internal', data)
    try:
        manager.start()
        process = manager._process
        process.kill()
        process.wait(timeout=10)
        assert not manager.is_running()
    finally:
        manager.stop()
    assert process.poll() is not None
    return {'owned_port_conflict_rejected_listener_survived': True,
            'owned_backend_crash_detected_cleanup': True,
            'scope': 'installed backend manager; no shell error-page or active-media descendant assertion'}


def main(payload: Path, data_root: Path | None = None, evidence: Path | None = None) -> None:
    if sys.platform != 'win32':
        raise SystemExit('Frozen Windows smoke test requires Windows')
    payload = payload.resolve()
    if data_root is None:
        with tempfile.TemporaryDirectory(prefix='AutoTransAI smoke ü ') as temporary:
            run_cycle(payload, Path(temporary))
    else:
        data = validate_data_root(data_root, Path(os.environ['RUNNER_TEMP']))
        first, previous_client = run_cycle(payload, data)
        samples = [first]
        database = data / 'data' / 'workflow.db'
        assert database.is_file(), 'Installed backend did not initialize SQLite'
        # A test-only marker in the disposable database proves reuse across restart.
        with sqlite3.connect(database) as db:
            db.execute('CREATE TABLE installed_smoke_marker (value TEXT NOT NULL)')
            db.execute('INSERT INTO installed_smoke_marker VALUES (?)', ('retained',))
        sentinel = data / 'storage' / 'installed-smoke-sentinel.txt'
        sentinel.write_text('retained disposable user data')
        second, _ = run_cycle(payload, data, previous_client)
        samples.append(second)
        with sqlite3.connect(database) as db:
            assert db.execute('SELECT value FROM installed_smoke_marker').fetchall() == [('retained',)]
        assert sentinel.read_text() == 'retained disposable user data'
        failures = run_failure_checks(payload, data)
        print('::notice title=Installed failure evidence::Owned port conflict rejected; listener survived; owned backend crash detected and reaped. No GUI error-page assertion.')
        if evidence:
            evidence.write_text(json.dumps({'scope': 'one CI run, two sequential installed backend launches; not p95',
                                            'failures': failures, 'samples': samples, 'restart_data_retained': True, 'previous_session_rejected': True}, indent=2))
    print('Frozen backend authenticated startup, UI/API and owned shutdown passed.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('payload', type=Path)
    parser.add_argument('--data-root', type=Path)
    parser.add_argument('--evidence', type=Path)
    args = parser.parse_args()
    main(args.payload, args.data_root, args.evidence)
