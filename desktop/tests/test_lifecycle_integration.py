"""Real app/process integration; tool fixtures only satisfy version preflight.

These portable checks do not exercise vendor media executables or WebView2.
Windows frozen-process smoke belongs to the Windows build/acceptance pipeline.
"""
import http.client
import os
from pathlib import Path
import socket
import sys
from urllib.parse import urlsplit

import pytest

from desktop.process_manager import BackendManager


@pytest.mark.skipif(os.name == 'nt', reason='POSIX version-tool fixtures; Windows uses frozen payload smoke')
def test_real_backend_cookie_media_restart_and_cleanup(tmp_path):
    # Do not disturb a service the test does not own.
    with socket.socket() as probe:
        try:
            probe.bind(('127.0.0.1', 8000))
        except OSError:
            pytest.skip('Fixed desktop port is occupied by an unrelated service')
    repo = Path(__file__).resolve().parents[2]
    resources = tmp_path / 'payload with spaces'
    resources.mkdir()
    (resources / 'backend').symlink_to(repo / 'backend', target_is_directory=True)
    dist = resources / 'frontend' / 'dist'
    dist.mkdir(parents=True)
    (dist / 'index.html').write_text('INTEGRATION-STUDIO', encoding='utf-8')
    (resources / 'bin').mkdir()
    for name in ('ffmpeg', 'ffprobe', 'yt-dlp', 'deno'):
        binary = resources / 'bin' / name
        binary.write_text('#!/bin/sh\nexit 0\n', encoding='utf-8')
        binary.chmod(0o700)
    writable = tmp_path / 'private user data'
    command = [sys.executable, '-c',
               f'import sys; sys.path.insert(0, {str(repo)!r}); '
               'from desktop.backend import run_backend; raise SystemExit(run_backend())']
    manager = BackendManager(command, resources, writable)

    def request(path, cookie=None, method='GET', headers=None):
        connection = http.client.HTTPConnection('127.0.0.1', 8000, timeout=5)
        try:
            fields = dict(headers or {})
            if cookie:
                fields['Cookie'] = cookie
            connection.request(method, path, headers=fields)
            response = connection.getresponse()
            return response.status, dict(response.getheaders()), response.read()
        finally:
            connection.close()

    try:
        bootstrap = manager.start()
        target = urlsplit(bootstrap)
        path = target.path + '?' + target.query
        assert request('/')[0] == 401
        status, headers, _ = request(path)
        assert status == 303 and headers['location'] == '/'
        cookie = headers['set-cookie'].split(';', 1)[0]
        assert request(path)[0] == 401
        assert request('/', cookie)[2] == b'INTEGRATION-STUDIO'
        assert request('/api/unknown-integration-route', cookie)[0] == 404
        assert request('/api/system/health', cookie)[0] == 200
        assert request('/api/system/health', cookie, 'POST', {'Origin': 'http://evil.invalid'})[0] == 403
        assert (writable / 'data' / 'workflow.db').is_file()
        media = writable / 'storage' / 'projects' / 'integration' / 'sample.mp4'
        media.parent.mkdir(parents=True)
        media.write_bytes(b'0123456789')
        media_url = '/media/projects/integration/sample.mp4'
        assert request(media_url)[0] == 401
        status, headers, body = request(media_url, cookie, headers={'Range': 'bytes=2-5'})
        assert status == 206 and body == b'2345'
        assert headers['content-range'] == 'bytes 2-5/10'
        manager.stop()
        assert not manager.is_running()
        second = manager.start()
        assert second != bootstrap
        assert request('/', cookie)[0] == 401
        assert media.read_bytes() == b'0123456789'
    finally:
        manager.stop()
    assert not manager.is_running()
    log = (manager.log_dir / 'backend.log').read_text(encoding='utf-8')
    assert target.query.split('=', 1)[1] not in log
    assert cookie.split('=', 1)[1] not in log
