"""Outer ASGI boundary for the private desktop loopback server.

The session protects against other browser origins, not malware running as the
same OS user. Keep this wrapper outside static, media, SSE and API routing.
"""
from __future__ import annotations

import secrets
from http.cookies import SimpleCookie, CookieError
from urllib.parse import parse_qs

from starlette.responses import JSONResponse, RedirectResponse, Response

_COOKIE = 'autotransai_desktop'
_CALLBACKS = frozenset(('/api/youtube/oauth-callback', '/api/tiktok/oauth-callback'))
_HEADERS = {'Cache-Control': 'no-store', 'Referrer-Policy': 'no-referrer',
            'X-Content-Type-Options': 'nosniff'}


class DesktopSecurity:
    def __init__(self, app, session_token: str, bootstrap_token: str,
                 instance_id: str, port: int = 8000):
        if not session_token or not bootstrap_token or not instance_id:
            raise ValueError('Desktop authentication values must not be empty')
        self.app = app
        self.session_token = session_token
        self.bootstrap_token = bootstrap_token
        self.instance_id = instance_id
        self.host = f'127.0.0.1:{port}'
        self.origin = f'http://{self.host}'
        self.ready = False

    async def __call__(self, scope, receive, send):
        if scope['type'] == 'lifespan':
            self.ready = False

            async def lifespan_send(message):
                if message['type'] == 'lifespan.startup.complete':
                    self.ready = True
                elif message['type'] in ('lifespan.startup.failed', 'lifespan.shutdown.complete', 'lifespan.shutdown.failed'):
                    self.ready = False
                await send(message)

            async def lifespan_receive():
                message = await receive()
                if message['type'] == 'lifespan.shutdown':
                    self.ready = False
                return message

            try:
                await self.app(scope, lifespan_receive, lifespan_send)
            finally:
                self.ready = False
            return
        if scope['type'] != 'http':
            if scope['type'] == 'websocket':
                await send({'type': 'websocket.close', 'code': 1008})
            return

        headers = {}
        for key, value in scope['headers']:
            headers.setdefault(key.lower(), []).append(value.decode('latin-1'))

        async def reject(status):
            await Response(status_code=status, headers=_HEADERS)(scope, receive, send)

        if headers.get(b'host') != [self.host]:
            return await reject(403)
        # Duplicate security headers are ambiguous: reject rather than selecting one.
        if any(len(headers.get(key, [])) > 1 for key in (b'authorization', b'origin', b'cookie', b'sec-fetch-site')):
            return await reject(403)
        authorization = headers.get(b'authorization', [''])[0]
        bearer = secrets.compare_digest(authorization.encode(), f'Bearer {self.session_token}'.encode())
        path, method = scope['path'], scope['method']
        if path == '/_desktop/health':
            if method != 'GET' or not bearer:
                return await reject(401)
            return await JSONResponse({'protocol': 1, 'instance_id': self.instance_id, 'ready': self.ready}, headers=_HEADERS)(scope, receive, send)
        if path == '/_desktop/bootstrap':
            query = parse_qs(scope.get('query_string', b'').decode('ascii', errors='replace'))
            tokens = query.get('token', [])
            if method != 'GET' or not self.bootstrap_token or len(tokens) != 1 or not secrets.compare_digest(tokens[0].encode(), self.bootstrap_token.encode()):
                return await reject(401)
            # No await before consumption: simultaneous requests cannot reuse it.
            self.bootstrap_token = ''
            response = RedirectResponse('/', status_code=303, headers=_HEADERS)
            response.set_cookie(_COOKIE, self.session_token, httponly=True, samesite='strict', path='/')
            return await response(scope, receive, send)

        callback = method == 'GET' and path in _CALLBACKS
        cookie = SimpleCookie()
        try:
            cookie.load(headers.get(b'cookie', [''])[0])
        except CookieError:
            return await reject(401)
        session = cookie.get(_COOKIE)
        authenticated = bearer or (session is not None and secrets.compare_digest(session.value.encode(), self.session_token.encode()))
        if not callback and not authenticated:
            return await reject(401)
        if method not in ('GET', 'HEAD', 'OPTIONS'):
            origin = headers.get(b'origin', [None])[0]
            if origin is not None and origin != self.origin:
                return await reject(403)
            if origin is None and not bearer and headers.get(b'sec-fetch-site') != ['same-origin']:
                return await reject(403)

        async def secure_send(message):
            if message['type'] == 'http.response.start':
                message = dict(message)
                message['headers'] = [(k, v) for k, v in message.get('headers', [])
                                      if k.lower() not in (b'cache-control', b'referrer-policy', b'x-content-type-options')]
                message['headers'] += [(k.lower().encode(), v.encode()) for k, v in _HEADERS.items()]
            await send(message)

        await self.app(scope, receive, secure_send)
