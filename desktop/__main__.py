"""Shared source/frozen entrypoint; child mode must avoid importing GUI code."""
from __future__ import annotations

import sys


def main(argv=None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if args == ['--desktop-backend']:
        from desktop.backend import run_backend
        return run_backend()
    if args:
        raise SystemExit(f'Unknown desktop argument: {args[0]}')
    from desktop.shell import run_shell
    return run_shell()


if __name__ == '__main__':
    raise SystemExit(main())
