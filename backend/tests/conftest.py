"""Keep the backend test process away from configured app data and credentials."""

import os
import re
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


_PROJECT = Path(__file__).resolve().parents[2]
if str(_PROJECT) not in sys.path:
    sys.path.insert(0, str(_PROJECT))

from shared import config as shared_config  # noqa: E402


_ISOLATED = TemporaryDirectory(prefix='autotransai-pytest-')
_ROOT = Path(_ISOLATED.name)
for _key in shared_config.parse_env_file(shared_config.ROOT_ENV_PATH):
    os.environ.pop(_key, None)
for _key in tuple(os.environ):
    if (_key.endswith(('_KEY', 'SECRET', 'TOKEN', 'PASSWORD', 'ACCESS_KEY_ID'))
            or re.search(r'_API_KEY_[1-9]$', _key)):
        os.environ.pop(_key, None)
shared_config.ROOT_ENV_PATH = _ROOT / '.env'
shared_config.ROOT_ENV_PATH.write_text('', encoding='utf-8')
os.environ.update({
    'DATABASE_URL': f'sqlite+aiosqlite:///{_ROOT / "workflow.sqlite"}',
    'DATA_DIR': str(_ROOT / 'data'),
    'STORAGE_ROOT': str(_ROOT / 'storage'),
})
