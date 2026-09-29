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

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from desktop.process_manager import BackendManager


def main(payload: Path) -> None:
    if sys.platform != 'win32':
        raise SystemExit('Frozen Windows smoke test requires Windows')
    payload = payload.resolve()
    with tempfile.TemporaryDirectory(prefix='AutoTransAI smoke ü ') as temporary:
        manager = BackendManager([str(payload / 'AutoTransAI.exe')],
                                 payload / '_internal', Path(temporary))
        try:
            url = manager.start()
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
        finally:
            manager.stop()
            if manager.is_running():
                raise AssertionError('Owned frozen backend survived shutdown')
    print('Frozen backend authenticated startup, UI/API and owned shutdown passed.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('payload', type=Path)
    main(parser.parse_args().payload)
