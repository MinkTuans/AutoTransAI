"""OAuth callback state is mandatory even when the provider reports an error."""
import time
from unittest.mock import patch

import pytest
from starlette.requests import Request
from app.api.routers import youtube, tiktok
from app.core.open_browser import oauth_done_html, open_oauth_in_chrome


def request():
    return Request({'type': 'http', 'scheme': 'http', 'server': ('127.0.0.1', 8000),
                    'path': '/', 'query_string': b'', 'headers': []})


@pytest.mark.asyncio
@pytest.mark.parametrize('state', [None, 'unknown'])
async def test_youtube_requires_known_state_before_exchange(state):
    response = await youtube.oauth_callback(request(), state=state, code='code', db=None)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_youtube_error_consumes_state_and_expired_state_rejected():
    youtube._oauth_verifiers['error-state'] = {'expires_at': time.monotonic() + 60, 'code_verifier': None}
    response = await youtube.oauth_callback(request(), state='error-state', code=None, db=None)
    assert response.status_code == 400
    assert 'error-state' not in youtube._oauth_verifiers
    youtube._oauth_verifiers['expired'] = {'expires_at': time.monotonic() - 1, 'code_verifier': None}
    response = await youtube.oauth_callback(request(), state='expired', code='code', db=None)
    assert response.status_code == 400
    assert 'expired' not in youtube._oauth_verifiers


@pytest.mark.asyncio
async def test_tiktok_error_consumes_state_and_escapes_provider_text():
    tiktok._oauth_sessions['error-state'] = {'expires_at': time.monotonic() + 60}
    response = await tiktok.oauth_callback(request(), state='error-state', error='denied', error_description='<script>alert(1)</script>', db=None)
    assert response.status_code == 400
    assert 'error-state' not in tiktok._oauth_sessions
    assert b'<script>' not in response.body
    assert b'&lt;script&gt;' in response.body
    replay = await tiktok.oauth_callback(request(), state='error-state', error='denied', error_description='untrusted-provider-text', db=None)
    assert b'untrusted-provider-text' not in replay.body


@pytest.mark.asyncio
async def test_tiktok_expired_state_rejected_before_exchange():
    tiktok._oauth_sessions['expired'] = {'expires_at': time.monotonic() - 1}
    response = await tiktok.oauth_callback(request(), state='expired', code='code', db=None)
    assert response.status_code == 400


def test_oauth_html_is_inert_and_escapes_all_dynamic_text():
    html = oauth_done_html('<img src=x onerror=alert(1)>', False, '<script>alert(1)</script>')
    assert '<script>' not in html and '<img' not in html
    assert "default-src 'none'" in html
    assert 'no-referrer' in html


def test_desktop_uses_windows_broker(monkeypatch):
    monkeypatch.setenv('AUTOTRANSAI_DESKTOP', '1')
    url = 'https://accounts.google.com/o/oauth2/auth?state=safe'
    with patch('app.core.open_browser.sys.platform', 'win32'), patch('app.core.open_browser.os.startfile', create=True) as launch:
        result = open_oauth_in_chrome(url)
    launch.assert_called_once_with(url)
    assert result['browser'] == 'default'


@pytest.mark.asyncio
async def test_youtube_registers_state_without_pkce_and_rejects_replay():
    from unittest.mock import MagicMock
    flow = MagicMock()
    flow.code_verifier = None
    flow.authorization_url.return_value = ('https://accounts.google.com/o/oauth2/auth', 'new-state')
    with patch.object(youtube, '_get_client_config', return_value={}), patch.object(youtube.google_auth_oauthlib.flow.Flow, 'from_client_config', return_value=flow):
        result = await youtube.get_auth_url()
    assert result['state'] == 'new-state'
    assert youtube._oauth_verifiers['new-state']['expires_at'] > time.monotonic()
    response = await youtube.oauth_callback(request(), state='new-state', code=None, db=None)
    assert response.status_code == 400
    replay = await youtube.oauth_callback(request(), state='new-state', code='code', db=None)
    assert replay.status_code == 400


@pytest.mark.asyncio
async def test_tiktok_generated_state_success_then_replay():
    from types import SimpleNamespace
    from unittest.mock import AsyncMock
    with patch.object(tiktok, '_require_tiktok_app', return_value=('key', 'secret', 'scope')):
        result = await tiktok.get_auth_url()
        state = result['state']
        assert tiktok._oauth_sessions[state]['expires_at'] > time.monotonic()
        with patch.object(tiktok, '_exchange_code', new=AsyncMock(return_value={'access_token': 'token'})), patch.object(tiktok, '_fetch_user_info', new=AsyncMock(return_value={})), patch.object(tiktok, 'persist_tiktok_account', new=AsyncMock(return_value=SimpleNamespace(display_name='test'))):
            response = await tiktok.oauth_callback(request(), state=state, code='code', db=None)
        assert response.status_code == 200
        assert state not in tiktok._oauth_sessions
        replay = await tiktok.oauth_callback(request(), state=state, code='code', db=None)
        assert replay.status_code == 400


@pytest.mark.asyncio
async def test_youtube_loopback_callback_exchanges_validated_code_over_https_with_pkce(monkeypatch):
    import json
    from unittest.mock import AsyncMock, MagicMock
    import requests
    from requests_oauthlib import OAuth2Session

    monkeypatch.delenv('OAUTHLIB_INSECURE_TRANSPORT', raising=False)
    state = 'validated-oauth-state'
    verifier = 'v' * 43
    youtube._oauth_verifiers[state] = {
        'expires_at': time.monotonic() + 60,
        'code_verifier': verifier,
        'redirect_uri': 'http://127.0.0.1:8000/api/youtube/oauth-callback',
    }
    config = {'web': {
        'client_id': 'test-client', 'client_secret': 'test-secret',
        'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
        'token_uri': 'https://oauth2.googleapis.com/token',
        'redirect_uris': ['http://127.0.0.1:8000/api/youtube/oauth-callback'],
    }}
    outbound = []

    def token_request(self, method, url, **kwargs):
        outbound.append((method, url, kwargs))
        response = requests.Response()
        response.status_code = 200
        response._content = json.dumps({
            'access_token': 'access-token', 'refresh_token': 'refresh-token',
            'token_type': 'Bearer', 'expires_in': 3600,
        }).encode()
        response.headers = {'content-type': 'application/json'}
        response.request = requests.Request(method, url, data=kwargs.get('data')).prepare()
        return response

    result = MagicMock()
    result.scalars.return_value.first.return_value = None
    db = MagicMock()
    db.execute = AsyncMock(return_value=result)
    db.commit = AsyncMock()
    channel_api = MagicMock()
    channel_api.channels.return_value.list.return_value.execute.return_value = {
        'items': [{'id': 'channel-id', 'snippet': {'title': 'Studio'}}]
    }
    callback_request = Request({
        'type': 'http', 'scheme': 'http', 'server': ('127.0.0.1', 8000),
        'path': '/api/youtube/oauth-callback',
        'query_string': f'state={state}&code=validated-code'.encode(), 'headers': [],
    })
    with patch.object(youtube, '_get_client_config', return_value=config), \
         patch.object(OAuth2Session, 'request', token_request), \
         patch('googleapiclient.discovery.build', return_value=channel_api), \
         patch.object(youtube, 'encrypt_data', return_value='encrypted'):
        response = await youtube.oauth_callback(callback_request, state=state,
                                                 code='validated-code', db=db)
    assert response.status_code == 200
    assert len(outbound) == 1
    method, url, kwargs = outbound[0]
    assert method == 'POST' and url == 'https://oauth2.googleapis.com/token'
    assert kwargs['data']['code'] == 'validated-code'
    assert kwargs['data']['code_verifier'] == verifier
    assert kwargs['data']['redirect_uri'] == 'http://127.0.0.1:8000/api/youtube/oauth-callback'
    assert state not in youtube._oauth_verifiers
