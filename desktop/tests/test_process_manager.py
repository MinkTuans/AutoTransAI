"""Portable supervisor contracts exercised against disposable real backends."""
import concurrent.futures
import json
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pytest

from desktop.process_manager import BackendManager, StartupError

FAKE = r'''
import http.server, json, sys, threading, time, subprocess
from pathlib import Path
mode = sys.argv[1]
h = json.loads(sys.stdin.readline())
root = Path(h['data_root'])
root.joinpath('started').write_text(str(__import__('os').getpid()))
if mode == 'exit': sys.exit(17)
if mode == 'hang': time.sleep(60); sys.exit()
if mode == 'tree':
    child = subprocess.Popen([sys.executable, '-c', "import time, pathlib, sys; p=pathlib.Path(sys.argv[1])\nwhile True:\n p.write_text(str(time.monotonic()))\n time.sleep(.02)", str(root / 'heartbeat')])
    root.joinpath('descendant').write_text(str(child.pid))
print(h['session_token'], h['bootstrap_token'], flush=True)
class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.headers.get('Authorization') != 'Bearer ' + h['session_token']:
            self.send_response(403); self.end_headers(); return
        self.send_response(200); self.end_headers()
        self.wfile.write(json.dumps({'protocol': 1, 'instance_id': 'foreign' if mode == 'wrong' else h['instance_id'], 'ready': True}).encode())
    def log_message(self, *args): pass
server = http.server.HTTPServer(('127.0.0.1', h['port']), Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
for line in sys.stdin:
    if json.loads(line).get('command') == 'shutdown': break
server.shutdown()
'''

@pytest.fixture
def factory(tmp_path):
    script = tmp_path / 'fake.py'
    script.write_text(FAKE)
    managers = []
    def make(mode='ok', port=None):
        if port is None:
            with socket.socket() as sock:
                sock.bind(('127.0.0.1', 0)); port = sock.getsockname()[1]
        manager = BackendManager([sys.executable, str(script), mode], tmp_path, tmp_path / 'data', port)
        manager.STARTUP_TIMEOUT = 1.5
        manager.STOP_TIMEOUT = .3
        manager.POLL_INTERVAL = .025
        managers.append(manager)
        return manager
    yield make
    for manager in managers: manager.stop()


def test_authenticated_ready_returns_bootstrap_and_redacts_logs(factory):
    manager = factory()
    url = manager.start()
    assert manager.is_running()
    assert urlparse(url).path == '/_desktop/bootstrap'
    token = parse_qs(urlparse(url).query)['token'][0]
    assert len(token) >= 32
    manager.stop()
    assert not manager.is_running()
    contents = (manager.log_dir / 'backend.log').read_text()
    assert token not in contents
    assert '[REDACTED]' in contents

@pytest.mark.parametrize('mode,match', [('exit', 'exited'), ('wrong', 'identity'), ('hang', 'timed out')])
def test_start_failure_is_bounded_and_cleans_owned_child(factory, mode, match):
    manager = factory(mode)
    before = time.monotonic()
    with pytest.raises(StartupError, match=match): manager.start()
    assert time.monotonic() - before < 4
    assert not manager.is_running()


def test_stop_cancels_start_without_waiting_for_readiness(factory):
    manager = factory('hang'); manager.STARTUP_TIMEOUT = 30
    with concurrent.futures.ThreadPoolExecutor() as pool:
        future = pool.submit(manager.start)
        deadline = time.monotonic() + 2
        while not (manager.data_root / 'started').exists() and time.monotonic() < deadline: time.sleep(.01)
        before = time.monotonic(); manager.stop()
        with pytest.raises(StartupError, match='cancel'): future.result(timeout=2)
        assert time.monotonic() - before < 2
    assert not manager.is_running()


def test_restart_after_failed_start(factory):
    manager = factory('exit')
    with pytest.raises(StartupError): manager.start()
    manager.command[-1] = 'ok'
    assert manager.start().startswith('http://127.0.0.1:')


def test_log_setup_failure_is_helpful_and_does_not_spawn(factory):
    manager = factory(); manager.data_root.mkdir()
    manager.log_dir.write_text('blocked')
    with pytest.raises(StartupError, match='log'): manager.start()
    assert not (manager.data_root / 'started').exists()


def test_foreign_port_is_never_attached_or_killed(factory):
    import http.server, threading
    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200); self.end_headers(); self.wfile.write(b'{"ready":true,"instance_id":"foreign"}')
        def log_message(self, *args): pass
    with http.server.HTTPServer(('127.0.0.1', 0), Handler) as server:
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        try:
            manager = factory('hang', server.server_port)
            with pytest.raises(StartupError): manager.start()
            assert thread.is_alive()
        finally: server.shutdown()


def test_owned_descendant_stops_unrelated_process_survives(factory):
    unrelated = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'])
    try:
        manager = factory('tree'); manager.start()
        heartbeat = manager.data_root / 'heartbeat'
        deadline = time.monotonic() + 2
        while not heartbeat.exists() and time.monotonic() < deadline: time.sleep(.02)
        assert heartbeat.exists()
        manager.stop()
        time.sleep(.1)
        previous = heartbeat.read_text()
        time.sleep(.15)
        assert heartbeat.read_text() == previous
        assert unrelated.poll() is None
    finally:
        unrelated.terminate(); unrelated.wait(timeout=3)


def test_dribbling_foreign_health_response_cannot_extend_startup_deadline(factory):
    import http.server
    import threading

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-Length', '120')
            self.end_headers()
            try:
                for _ in range(120):
                    self.wfile.write(b' ')
                    self.wfile.flush()
                    time.sleep(.01)
            except (BrokenPipeError, ConnectionResetError):
                pass

        def log_message(self, *args):
            pass

    with http.server.ThreadingHTTPServer(('127.0.0.1', 0), Handler) as server:
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            manager = factory('hang', server.server_port)
            manager.STARTUP_TIMEOUT = .15
            before = time.monotonic()
            with pytest.raises(StartupError, match='timed out'):
                manager.start()
            assert time.monotonic() - before < .9
        finally:
            server.shutdown()
