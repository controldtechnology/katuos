#!/usr/bin/python3
"""Notify through KDE only after a successful authenticated refresh."""
import json
from pathlib import Path
import subprocess
import sys
import time
sys.path.insert(0, '/usr/lib/katu-update')
from backend import STATE, make_plan


def main():
    try:
        checked = json.loads((STATE / 'check.json').read_text())
        if not checked['ok'] or time.time() - checked['time'] > 172800:
            return
        plan = make_plan()
        if not plan['packages']:
            return
        marker = Path.home() / '.local/state/katu-update/notified'
        if marker.exists() and marker.read_text() == plan['digest']:
            return
        marker.parent.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(['notify-send', '--app-name=Katu Update', '--icon=system-software-update',
                                 '--action=view=VER', '--wait', '--expire-time=15000',
                                 'Katu Update', 'Novas atualizações estão disponíveis.'],
                                capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            marker.write_text(plan['digest'])
        if result.stdout.strip() == 'view':
            subprocess.Popen(['/usr/bin/katu-update'])
    except Exception:
        return


if __name__ == '__main__':
    main()
