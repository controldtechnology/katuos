#!/usr/bin/python3
"""Versioned, idempotent system migrations. Never traverse /home."""
import json
import os
from pathlib import Path
import time

STATE = Path('/var/lib/katu-update/migrations')


def migrate():
    STATE.mkdir(parents=True, exist_ok=True)
    marker = STATE / '001-continuous-update.json'
    if marker.exists():
        return
    # Old checker path is now owned by katu-update and starts its native timer.
    # Dpkg owns file replacement and conffiles; no user profile rewriting.
    temp = marker.with_suffix('.tmp')
    with temp.open('w') as stream:
        json.dump({'version': 1, 'completed': time.time()}, stream)
        stream.flush()
        os.fsync(stream.fileno())
    temp.replace(marker)


if __name__ == '__main__':
    migrate()
