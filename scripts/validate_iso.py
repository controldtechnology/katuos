#!/usr/bin/env python3
"""Validate the final ISO; structural success is never a release approval."""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from boot_checks import require, run, rooted, kernel_version, grub_entries, initrd_check, rootfs_check, sha256_file

parser = argparse.ArgumentParser()
parser.add_argument('iso', type=Path)
parser.add_argument('--report', type=Path, required=True)
args = parser.parse_args()
report = {'status': 'FAIL', 'checks': {}, 'iso': str(args.iso.resolve())}
args.report.parent.mkdir(parents=True, exist_ok=True)

def passed(name):
    report['checks'][name] = 'PASS'
    print(name + ': PASS', flush=True)

try:
    __import__('yaml')  # Fail before the expensive extraction if installer validator cannot run.
    for tool in ['xorriso', 'unsquashfs', 'unmkinitramfs', 'grub-script-check', 'mcopy']:
        require(shutil.which(tool), f'Required tool missing: {tool}')
    require(args.iso.is_file(), 'ISO missing')
    report['sha256'] = sha256_file(args.iso)
    report['size'] = args.iso.stat().st_size
    with tempfile.TemporaryDirectory(prefix='katu-validate-') as temporary:
        scratch = Path(temporary)
        iso = scratch / 'iso'
        iso.mkdir()
        result = subprocess.run(['xorriso', '-indev', str(args.iso), '-report_el_torito', 'plain',
                                 '-report_system_area', 'plain', '-pvd_info'],
                                check=True, capture_output=True, text=True)
        metadata = result.stdout + result.stderr
        report['xorriso'] = metadata
        label = re.search(r"Volume [Ii]d\s*:\s*'([^']+)'", metadata)
        require(label, 'Cannot read ISO label')
        report['label'] = label[1]
        require(label[1] == 'KATU_OS_1.0', 'Unexpected ISO label')
        require(re.search(r'El Torito boot img\s*:.*BIOS', metadata), 'No BIOS boot catalog entry')
        require(re.search(r'El Torito boot img\s*:.*UEFI', metadata), 'No UEFI boot catalog entry')
        require('MBR' in metadata and ('GPT' in metadata or 'isohybrid' in metadata.lower()),
                'Hybrid disk layout missing')
        passed('ISO STRUCTURE')
        run('xorriso', '-osirrox', 'on', '-indev', args.iso, '-extract', '/', iso)
        configs = list((iso / 'boot/grub').rglob('*.cfg'))
        require(configs, 'GRUB configs missing')
        entries = []
        for config in configs:
            run('grub-script-check', config)
            if re.search(r'^\s*(linux|linuxefi)\s', config.read_text(), re.M):
                entries.extend(grub_entries(config, iso))
        require(entries, 'No GRUB Live entries')
        passed('GRUB')
        squash = iso / 'live/filesystem.squashfs'
        run('unsquashfs', '-s', squash)
        root = scratch / 'rootfs'
        run('unsquashfs', '-no-progress', '-processors', '2', '-d', root, squash)
        passed('SQUASHFS')
        versions = {kernel_version(rooted(iso, e['kernel'])) for e in entries}
        require(len(versions) == 1, 'Multiple kernels unsupported by this build')
        version = versions.pop()
        report['kernel'] = version
        config = rootfs_check(root, version)
        passed('KERNEL')
        for index, initrd in enumerate(sorted({i for e in entries for i in e['initrds']})):
            work = scratch / ('ramfs-' + str(index))
            work.mkdir()
            initrd_check(rooted(iso, initrd), version, work, config)
        for check in ['INITRD', 'LIVE-BOOT', 'KERNEL/MODULES']:
            passed(check)
        run('python3', Path(__file__).with_name('validate-installer.py'), '--root', root)
        passed('INSTALLER STRUCTURE')
        for name in ['boot/grub/themes/katu/theme.txt', 'usr/share/plymouth/themes/katu/katu.plymouth',
                     'usr/share/sddm/themes/katu/Main.qml', 'usr/share/sddm/themes/katu/background.png',
                     'usr/share/sddm/themes/katu/logo.png', 'etc/sddm.conf.d/katu.conf',
                     'etc/calamares/branding/katu/branding.desc',
                     'etc/calamares/branding/katu/stylesheet.qss',
                     'usr/share/applications/katu-install.desktop',
                     'usr/lib/systemd/system/katu-live-autologin.service',
                     'usr/lib/katu/live-autologin']:
            require(rooted(root, name).is_file(), f'Missing branding/installer asset: {name}')
        require('Current=katu' in rooted(root, 'etc/sddm.conf.d/katu.conf').read_text(),
                'Installed greeter must select the Katu SDDM theme')
        sddm_qml = rooted(root, 'usr/share/sddm/themes/katu/Main.qml').read_text()
        require('import QtQuick.Controls' not in sddm_qml and 'import QtQuick.Layouts' not in sddm_qml,
                'Katu SDDM theme must use the QtQuick/SddmComponents baseline for Qt 6 compatibility')
        live_login = rooted(root, 'usr/lib/systemd/system/katu-live-autologin.service').read_text()
        require('ConditionKernelCommandLine=boot=live' in live_login,
                'Live auto-login must not apply to the installed system')
        require('Katu' in rooted(root, 'etc/os-release').read_text(), 'OS branding missing')
        require(any(rooted(root, 'usr/share/wallpapers/katu').rglob('*.png')), 'Wallpaper missing')
        passed('BRANDING STRUCTURE')
        efi = iso / 'efi.img'
        require(efi.is_file(), 'EFI system partition image missing')
        run('mcopy', '-i', efi, '::/EFI/BOOT/BOOTX64.EFI', scratch / 'BOOTX64.EFI')
        require((scratch / 'BOOTX64.EFI').read_bytes()[:2] == b'MZ', 'Invalid EFI executable')
        passed('UEFI STRUCTURE')
        passed('BIOS STRUCTURE')
        packages = {}
        for line in (iso / 'live/filesystem.packages').read_text().splitlines():
            fields = line.split()
            if len(fields) == 2:
                packages[fields[0]] = fields[1]
        report['packages'] = {k: packages.get(k) for k in ['plasma-workspace', 'calamares', 'live-boot',
                              'live-config', 'initramfs-tools', 'grub-common', 'sddm', 'systemd']}
        require(not packages.get('casper'), 'Casper mixed with Debian Live')
        report['status'] = 'PASS'
except Exception as exc:
    report['error'] = str(exc)
    if isinstance(exc, subprocess.CalledProcessError):
        report['output'], report['stderr'] = exc.stdout, exc.stderr
    raise
finally:
    args.report.write_text(json.dumps(report, indent=2) + '\n')
