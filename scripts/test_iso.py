#!/usr/bin/env python3
"""Boot the final ISO's kernel/initrd and real Live medium in QEMU.

This tests the Live chain; firmware/GRUB boot is a separate VirtualBox test.
"""
import argparse
import hashlib
import json
import secrets
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from boot_checks import require, run, sha256_file, grub_entries

parser = argparse.ArgumentParser()
parser.add_argument('iso', type=Path)
parser.add_argument('--timeout', type=int, default=600)
args = parser.parse_args()
report_path = Path(str(args.iso) + '.smoke.json')
report = {'status': 'FAIL', 'scope': 'QEMU Live kernel/initrd + ISO, firmware not covered'}
report['sha256'] = sha256_file(args.iso)
process = None
try:
    require(shutil.which('qemu-system-x86_64'), 'QEMU missing: NOT TESTED; gate blocked')
    with tempfile.TemporaryDirectory(prefix='katu-smoke-') as temp:
        work = Path(temp)
        for source, target in [('/live/vmlinuz', 'vmlinuz'), ('/live/initrd.img', 'initrd'),
                               ('/boot/grub/grub.cfg', 'grub.cfg')]:
            run('xorriso', '-osirrox', 'on', '-indev', args.iso, '-extract', source, work / target)
        entry = grub_entries(work / 'grub.cfg')[0]
        require(entry['kernel'] == '/live/vmlinuz' and entry['initrds'] == ['/live/initrd.img'],
                'Smoke runner must be updated for changed default boot paths')
        boot_params = [p for p in entry['params'] if p not in ('quiet', 'splash')]
        report['boot_parameters'] = boot_params
        nonce = secrets.token_hex(16)
        serial = Path(str(args.iso) + '.serial.log')
        stderr = Path(str(args.iso) + '.qemu.log')
        command = ['qemu-system-x86_64', '-machine', 'q35', '-accel', 'tcg', '-m', '4096', '-smp', '2',
                   '-display', 'none', '-vga', 'std', '-no-reboot', '-monitor', 'none',
                   '-serial', 'file:' + str(serial), '-nic', 'user,model=e1000',
                   '-cdrom', str(args.iso.resolve()), '-kernel', str(work / 'vmlinuz'),
                   '-initrd', str(work / 'initrd'), '-append',
                   ' '.join(boot_params + ['console=tty0', 'console=ttyS0,115200', f'katu.qa={nonce}'])]
        with stderr.open('w') as error_log:
            process = subprocess.Popen(command, stdout=error_log, stderr=error_log)
            deadline = time.monotonic() + args.timeout
            while time.monotonic() < deadline:
                log = serial.read_text(errors='replace') if serial.exists() else ''
                require('(initramfs)' not in log and 'Kernel panic' not in log and 'emergency mode' not in log,
                        'Unexpected initramfs/panic/emergency shell: release rejected')
                require(f'KATU_QA_FAIL:{nonce}' not in log,
                        'Live acceptance failed; inspect the serial log diagnostics')
                if f'KATU_QA_PASS:{nonce}:systemd:sddm:plasmashell:overlay' in log:
                    report['status'] = 'PASS'
                    report['evidence'] = str(serial)
                    break
                require(process.poll() is None, 'QEMU exited before Live acceptance marker')
                time.sleep(3)
            require(report['status'] == 'PASS', 'QEMU timed out before Plasma/DBus/overlay verification')
except Exception as exc:
    report['error'] = str(exc)
    raise
finally:
    if process and process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
    report_path.write_text(json.dumps(report, indent=2) + '\n')
print('QEMU LIVE SMOKE: PASS (manual interaction acceptance remains required)')
