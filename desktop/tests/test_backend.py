"""Desktop adapter tests use disposable files and fresh config subprocesses."""
import io
import json
import os
from pathlib import Path
import socket
import subprocess
import sys

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

REPO = Path(__file__).resolve().parents[2]


def test_paths_separate_resources_from_user_data(monkeypatch, tmp_path):
    from desktop import paths
    monkeypatch.setenv('LOCALAPPDATA', str(tmp_path / 'profile'))
    assert paths.data_root() == tmp_path / 'profile' / 'AutoTransAI'
    assert paths.resource_root() == REPO
    monkeypatch.setattr(sys, 'frozen', True, raising=False)
    monkeypatch.setattr(sys, '_MEIPASS', str(tmp_path / 'payload'), raising=False)
    assert paths.resource_root() == tmp_path / 'payload'


def test_desktop_config_ignores_dotenv_and_inherited_secrets(tmp_path):
    resource = tmp_path / 'resources'
    resource.mkdir()
    (resource / '.env').write_text('GEMINI_API_KEY=dotenv-secret\nDATABASE_URL=mysql://bad\n')
    root = tmp_path / 'private'
    code = '''
import json, sys, os
from desktop.paths import configure_environment
configure_environment(*map(__import__('pathlib').Path, sys.argv[1:]))
from shared.config import load_root_env
from app.config import get_settings
s=get_settings()
print(json.dumps([str(s.ROOT_DIR),str(s.DATA_DIR),str(s.STORAGE_ROOT),s.DB_URL,s.GEMINI_API_KEY,load_root_env(),os.getenv('OPENAI_API_KEY_1')]))
'''
    env = dict(PATH=os.environ.get("PATH", ""), PYTHONPATH=str(REPO) + os.pathsep + str(REPO / 'backend'), DATABASE_URL='mysql://inherited', GEMINI_API_KEY='inherited-secret', DATA_DIR='/wrong', OPENAI_API_KEY_1='numbered-secret')
    out = subprocess.run([sys.executable, '-c', code, str(resource), str(root)], env=env, capture_output=True, text=True, check=True)
    values = json.loads(out.stdout)
    assert values == [str(resource), str(root / 'data'), str(root / 'storage'), f'sqlite+aiosqlite:///{root / "data/workflow.db"}', '', {}, None]


def test_missing_frontend_and_tools_fail_before_import(tmp_path):
    from desktop.backend import validate_resources
    with pytest.raises(RuntimeError, match='frontend'):
        validate_resources(tmp_path)
    (tmp_path / 'frontend/dist').mkdir(parents=True)
    (tmp_path / 'frontend/dist/index.html').write_text('hello')
    with pytest.raises(RuntimeError, match='ffmpeg'):
        validate_resources(tmp_path)


def test_frontend_preserves_api_media_and_unknown_api(tmp_path):
    from desktop.backend import FrontendHost
    (tmp_path / 'index.html').write_text('FRONTEND')
    (tmp_path / 'app.js').write_text('script')
    app = FastAPI()
    @app.get('/api/check')
    def check():
        return {'ok': True}
    @app.get('/media/check')
    def media():
        return {'media': True}
    with TestClient(FrontendHost(app, tmp_path)) as client:
        assert client.get('/').text == 'FRONTEND'
        assert client.get('/studio').text == 'FRONTEND'
        assert client.get('/app.js').text == 'script'
        assert client.get('/api/check').json() == {'ok': True}
        assert client.get('/media/check').json() == {'media': True}
        assert client.get('/api/unknown').status_code == 404
        assert client.get('/media/unknown').status_code == 404
        assert client.get('/missing.js').status_code == 404
        assert client.post('/studio').status_code == 405


def test_exclusive_socket_never_replaces_foreign_listener():
    from desktop.backend import bind_socket
    with socket.socket() as owner:
        owner.bind(('127.0.0.1', 0))
        owner.listen()
        with pytest.raises(RuntimeError, match='already in use'):
            bind_socket(owner.getsockname()[1])
        assert owner.fileno() >= 0


def test_handshake_validates_without_echoing_secret():
    from desktop.backend import read_handshake
    with pytest.raises(ValueError, match='Invalid desktop handshake'):
        read_handshake(io.StringIO('{"session_token":"secret"}\n'))


def test_shutdown_pipe_and_eof():
    from desktop.backend import watch_control
    class Server:
        should_exit = False
    for value in ('', '{"command":"shutdown"}\n'):
        server = Server()
        watch_control(io.StringIO(value), server)
        assert server.should_exit


@pytest.mark.skipif(os.name == 'nt', reason='portable executable fixture uses a POSIX shell')
def test_tools_are_executed_and_denied_on_failure(tmp_path):
    from desktop.backend import validate_resources
    dist = tmp_path / 'frontend/dist'
    dist.mkdir(parents=True)
    (dist / 'index.html').write_text('frontend')
    bins = tmp_path / 'bin'
    bins.mkdir()
    for name in ('ffmpeg', 'ffprobe', 'yt-dlp', 'deno'):
        binary = bins / name
        binary.write_text('#!/bin/sh\nexit 0\n')
        binary.chmod(0o700)
    assert validate_resources(tmp_path) == dist
    (bins / 'deno').write_text('#!/bin/sh\nexit 3\n')
    with pytest.raises(RuntimeError, match='deno failed'):
        validate_resources(tmp_path)


def test_handshake_accepts_fixed_protocol_and_absolute_roots(tmp_path):
    from desktop.backend import read_handshake
    value = dict(protocol=1, instance_id='id', session_token='session', bootstrap_token='bootstrap',
                 resource_root=str(tmp_path), data_root=str(tmp_path / 'private'), port=8000)
    assert read_handshake(io.StringIO(json.dumps(value) + '\n')) == value
    value['port'] = 8080
    with pytest.raises(ValueError):
        read_handshake(io.StringIO(json.dumps(value) + '\n'))


def test_desktop_oauth_uses_only_explicit_private_config(tmp_path):
    resources = tmp_path / 'resources'
    resources.mkdir()
    root = tmp_path / 'private'
    (root / 'data').mkdir(parents=True)
    (root / 'data/desktop.env').write_text(
        '# Explicit OAuth app credentials\nYOUTUBE_CLIENT_ID=test-client\n'
        'YOUTUBE_CLIENT_SECRET="literal-${NOT_EXPANDED}"\nTIKTOK_CLIENT_KEY=tiktok-client\n'
        'TIKTOK_CLIENT_SECRET=tiktok-secret\nTIKTOK_SCOPES=user.info.basic\n', encoding='utf-8')
    script = '''
import json, sys
from pathlib import Path
from desktop.paths import configure_environment
configure_environment(Path(sys.argv[1]),Path(sys.argv[2]))
from app.config import get_settings
s=get_settings()
print(json.dumps([s.YOUTUBE_CLIENT_ID,s.YOUTUBE_CLIENT_SECRET,s.TIKTOK_CLIENT_KEY,s.TIKTOK_CLIENT_SECRET,s.TIKTOK_SCOPES,s.YOUTUBE_REDIRECT_URI]))
'''
    output = subprocess.run([sys.executable, '-c', script, str(resources), str(root)],
                            env={'PATH': os.environ.get('PATH', ''), 'PYTHONPATH': str(REPO) + os.pathsep + str(REPO / 'backend')},
                            capture_output=True, text=True)
    assert output.returncode == 0, output.stderr
    assert json.loads(output.stdout) == ['test-client', 'literal-${NOT_EXPANDED}', 'tiktok-client', 'tiktok-secret', 'user.info.basic', 'http://127.0.0.1:8000/api/youtube/oauth-callback']


@pytest.mark.parametrize('entry', ['DATABASE_URL=private-secret', 'DATA_DIR=private-secret', 'YOUTUBE_REDIRECT_URI=private-secret', 'invalid private-secret'])
def test_desktop_oauth_config_rejects_non_allowlisted_settings_without_values(tmp_path, entry):
    root = tmp_path / 'private'
    (root / 'data').mkdir(parents=True)
    (root / 'data/desktop.env').write_text(entry, encoding='utf-8')
    script = '''
import sys
from pathlib import Path
from desktop.paths import configure_environment
try:
    configure_environment(Path(sys.argv[1]),Path(sys.argv[2]))
except ValueError as e:
    print(str(e)); sys.exit(2)
'''
    output = subprocess.run([sys.executable, '-c', script, str(tmp_path / 'resources'), str(root)],
                            env={'PATH': os.environ.get('PATH', ''), 'PYTHONPATH': str(REPO)},
                            capture_output=True, text=True)
    assert output.returncode == 2
    assert 'desktop.env' in output.stdout
    assert 'private-secret' not in output.stdout + output.stderr


@pytest.mark.parametrize('module_name', ['missing.dependency', 'private/credential-value'])
def test_startup_diagnostics_identify_import_without_exception_values(monkeypatch, capsys, module_name):
    from desktop import backend
    monkeypatch.setattr(backend, 'restore_standard_streams', lambda: None)

    def failing_import(stream):
        raise ModuleNotFoundError('private-exception-value', name=module_name)

    monkeypatch.setattr(backend, 'read_handshake', failing_import)
    assert backend.run_backend() == 1
    diagnostic = capsys.readouterr().err
    assert 'ModuleNotFoundError' in diagnostic
    assert 'failing_import' in diagnostic
    assert 'test_backend.py:' in diagnostic
    assert 'private-exception-value' not in diagnostic
    assert 'private/credential-value' not in diagnostic
    if module_name == 'missing.dependency':
        assert module_name in diagnostic
