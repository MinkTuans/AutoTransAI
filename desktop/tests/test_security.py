import asyncio
import importlib

from starlette.responses import Response
from starlette.testclient import TestClient


async def app(scope, receive, send):
    if scope['type'] == 'lifespan':
        while True:
            message = await receive()
            if message['type'] == 'lifespan.startup':
                await send({'type': 'lifespan.startup.complete'})
            else:
                await send({'type': 'lifespan.shutdown.complete'})
                return
    else:
        await Response('data', status_code=206 if any(k == b'range' for k,v in scope['headers']) else 200)(scope, receive, send)


def guard():
    try:
        module = importlib.import_module('desktop.security')
    except ModuleNotFoundError:
        module = None
    assert module is not None, 'Desktop security boundary must exist'
    return module.DesktopSecurity(app, 'session-secret', 'bootstrap-secret', 'instance')


def test_anonymous_and_exact_callback_exception():
    with TestClient(guard(), base_url='http://127.0.0.1:8000') as client:
        for path in ['/', '/api/settings', '/media/video.mp4', '/assets/app.js', '/api/youtube/oauth-callback/extra']:
            assert client.get(path).status_code == 401
        for provider in ['youtube', 'tiktok']:
            path = f'/api/{provider}/oauth-callback'
            assert client.get(path).status_code == 200
            assert client.post(path).status_code in [401, 403]


def test_bootstrap_cookie_streams_and_csrf():
    with TestClient(guard(), base_url='http://127.0.0.1:8000') as client:
        response = client.get('/_desktop/bootstrap?token=bootstrap-secret', follow_redirects=False)
        assert response.status_code == 303
        assert response.headers['location'] == '/'
        assert 'HttpOnly' in response.headers['set-cookie']
        assert 'SameSite=strict' in response.headers['set-cookie']
        assert response.headers['cache-control'] == 'no-store'
        assert response.headers['referrer-policy'] == 'no-referrer'
        assert client.get('/_desktop/bootstrap?token=bootstrap-secret').status_code == 401
        for path in ['/api/settings', '/media/video.mp4', '/assets/app.js', '/api/events']:
            assert client.get(path).status_code == 200
        assert client.get('/media/video.mp4', headers={'Range':'bytes=0-3'}).status_code == 206
        for origin in ['http://evil.test', 'http://127.0.0.1:9000', 'null']:
            assert client.post('/api/settings', headers={'Origin': origin}).status_code == 403
        assert client.post('/api/settings').status_code == 403
        assert client.post('/api/settings', headers={'Origin': 'http://127.0.0.1:8000'}).status_code == 200
        assert client.get('/', headers={'Host':'localhost:8000'}).status_code == 403


def test_health_requires_bearer_and_successful_lifespan():
    boundary = guard()
    with TestClient(boundary, base_url='http://127.0.0.1:8000') as client:
        assert client.get('/_desktop/health').status_code == 401
        response = client.get('/_desktop/health', headers={'Authorization':'Bearer session-secret'})
        assert response.json() == {'protocol': 1, 'instance_id':'instance', 'ready': True}
        assert response.headers['cache-control'] == 'no-store'
    assert boundary.ready is False
    client = TestClient(boundary, base_url='http://127.0.0.1:8000')
    assert client.get('/_desktop/health', headers={'Authorization':'Bearer session-secret'}).json()['ready'] is False


def test_bearer_and_fetch_metadata_do_not_allow_foreign_origin():
    with TestClient(guard(), base_url='http://127.0.0.1:8000') as client:
        auth = {'Authorization': 'Bearer session-secret'}
        assert client.post('/api/settings', headers=auth).status_code == 200
        assert client.post('/api/settings', headers={**auth, 'Origin': 'null'}).status_code == 403
        client.get('/_desktop/bootstrap?token=bootstrap-secret')
        assert client.post('/api/settings', headers={'Sec-Fetch-Site': 'same-origin'}).status_code == 200
        assert client.post('/api/settings', headers={'Sec-Fetch-Site': 'cross-site'}).status_code == 403
        assert client.get('/_desktop/health').status_code == 401
        assert client.get('/_desktop/bootstrap?token=wrong').status_code == 401


def test_duplicate_hosts_and_websocket_rejected():
    with TestClient(guard(), base_url='http://127.0.0.1:8000') as client:
        response = client.get('/', headers=[('Host', '127.0.0.1:8000'), ('Host', 'evil.test')])
        assert response.status_code == 403
        import pytest
        from starlette.websockets import WebSocketDisconnect
        with pytest.raises(WebSocketDisconnect):
            with client.websocket_connect('/api/socket'):
                pass


def test_failed_lifespan_never_reports_ready():
    boundary = guard()

    async def failing(scope, receive, send):
        await receive()
        await send({'type': 'lifespan.startup.failed', 'message': 'failure'})

    boundary.app = failing
    messages = []

    async def receive():
        return {'type': 'lifespan.startup'}

    async def send(message):
        messages.append(message)

    asyncio.run(boundary({'type': 'lifespan'}, receive, send))
    assert messages[0]['type'] == 'lifespan.startup.failed'
    assert boundary.ready is False
