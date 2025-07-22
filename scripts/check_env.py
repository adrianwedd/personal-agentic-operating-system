#!/usr/bin/env python3
"""Warn if any variables from .env.example are missing in .env."""
from __future__ import annotations
import sys
from pathlib import Path
from typing import List


def _parse_env(path: Path) -> dict:
    """Return mapping of key->value for env file."""
    data: dict[str, str] = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '=' not in line:
            continue
        key, val = line.split('=', 1)
        data[key.strip()] = val.strip()
    return data


def missing_vars(example: Path, env: Path) -> List[str]:
    req = _parse_env(example)
    actual = _parse_env(env) if env.exists() else {}
    return [k for k in req if not actual.get(k)]


def main(example: str = '.env.example', env_file: str = '.env') -> int:
    ex = Path(example)
    env = Path(env_file)
    miss = missing_vars(ex, env)
    if miss:
        print('⚠ Missing env vars: ' + ', '.join(sorted(miss)))
    else:
        print('All required env vars set.')
    return 0


if __name__ == '__main__':
    sys.exit(main(*sys.argv[1:]))
