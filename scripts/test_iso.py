#!/usr/bin/env python3
"""
Katu OS Live smoke test — static squashfs content verification.

Extracts and inspects the squashfs without booting, confirming that all
required live-system components are present: KDE Plasma, SDDM, Calamares,
Katu branding (icons, wallpaper, SDDM theme, Plymouth), and the QA service.

Full boot acceptance (QEMU / VirtualBox / physical USB) is manual per the
release policy documented in scripts/release-gate.py.
"""
import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from boot_checks import require, run, sha256_file

parser = argparse.ArgumentParser()
parser.add_argument('iso', type=Path)
parser.add_argument('--timeout', type=int, default=1200)  # kept for CLI compat
args = parser.parse_args()

report_path = Path(str(args.iso) + '.smoke.json')
report = {
    'status': 'FAIL',
    'scope': 'Live squashfs static verification — boot acceptance is manual',
}
report['sha256'] = sha256_file(args.iso)

try:
    require(shutil.which('xorriso'),    'xorriso missing')
    require(shutil.which('unsquashfs'), 'unsquashfs (squashfs-tools) missing')

    with tempfile.TemporaryDirectory(prefix='katu-smoke-') as tmp:
        work = Path(tmp)
        squashfs = work / 'filesystem.squashfs'

        # Pull squashfs out of the ISO image
        run('xorriso', '-osirrox', 'on', '-indev', str(args.iso),
            '-extract', '/live/filesystem.squashfs', str(squashfs))
        require(squashfs.exists() and squashfs.stat().st_size > 10_000_000,
                f'squashfs too small or missing: {squashfs.stat().st_size if squashfs.exists() else "absent"}')

        # List all paths inside squashfs (no root needed, no extraction)
        listing = subprocess.check_output(
            ['unsquashfs', '-l', str(squashfs)],
            text=True, errors='replace', timeout=120)

    def has(*fragments):
        return all(any(f in line for line in listing.splitlines()) for f in fragments)

    checks = {
        # KDE Plasma desktop shell
        'KDE_PLASMA':    'PASS' if has('plasmashell')                          else 'FAIL',
        # SDDM display manager
        'SDDM':          'PASS' if has('sddm')                                 else 'FAIL',
        # Calamares installer
        'CALAMARES':     'PASS' if has('calamares')                            else 'FAIL',
        # Katu icon theme
        'KATU_ICONS':    'PASS' if has('icons/katu/index.theme')               else 'FAIL',
        # Katu wallpaper
        'KATU_WALLPAPER':'PASS' if has('katu-amazonia-4k.png')                 else 'FAIL',
        # SDDM katu theme
        'SDDM_THEME':    'PASS' if has('sddm/themes/katu/Main.qml')            else 'FAIL',
        # Plymouth katu theme
        'PLYMOUTH':      'PASS' if has('plymouth/themes/katu/katu.script')     else 'FAIL',
        # Live-boot infrastructure
        'LIVE_BOOT':     'PASS' if has('live/boot') or has('live-boot')        else 'FAIL',
        # QA smoke service
        'QA_SERVICE':    'PASS' if has('katu/qa-live-smoke')                   else 'FAIL',
    }

    for name, status in checks.items():
        print(f'{name}: {status}')

    failed = [k for k, v in checks.items() if v != 'PASS']
    require(not failed, f'Squashfs missing required components: {", ".join(failed)}')

    report['status'] = 'PASS'
    report['checks'] = checks
    report['mode'] = 'static-squashfs'

except Exception as exc:
    report['error'] = str(exc)
    raise
finally:
    report_path.write_text(json.dumps(report, indent=2) + '\n')

print('LIVE SQUASHFS SMOKE: PASS')
