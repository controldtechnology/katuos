#!/usr/bin/env python3
"""Validate the Calamares deployment in the source tree or built rootfs."""
import argparse
from pathlib import Path
import yaml
from boot_checks import png_check

parser = argparse.ArgumentParser()
parser.add_argument('--root', type=Path)
args = parser.parse_args()
base = args.root / 'etc/calamares' if args.root else Path(__file__).resolve().parents[1] / 'installer/calamares'

for name in ['logo.png', 'icon.png', 'welcome.png'] + [f'slide-{i:02d}.png' for i in range(1, 7)]:
    png_check(base / 'branding/katu' / name)

def config(name):
    path = base / name
    data = yaml.safe_load(path.read_text(encoding='utf-8-sig'))
    if not isinstance(data, dict):
        raise ValueError(f'{path}: expected a YAML mapping')
    return data

settings = config('settings.conf')
branding = config('branding/katu/branding.desc')
assert branding.get('componentName') == 'katu'
assert (base / 'branding/katu/stylesheet.qss').is_file(), 'Katu Calamares stylesheet is missing'
configs = {p.stem: config('modules/' + p.name) for p in (base / 'modules').glob('*.conf')}
steps = [m for step in settings['sequence'] for modules in step.values() for m in modules]
requirements = configs['welcome']['requirements']
assert {'storage', 'root'} <= set(requirements['required']) <= set(requirements['check'])
assert requirements['requiredStorage'] >= 20
boot = configs['bootloader']
assert boot['efiBootLoader'] == 'grub'
assert boot['efiBootloaderId'] == 'debian'
assert boot['installEFIFallback'] is True
assert steps.index('grubcfg') < steps.index('bootloader') < steps.index('umount')
assert steps.index('shellprocess') < steps.index('bootloader')
for operation in configs['packages']['operations']:
    if 'install' in operation:
        assert set(operation['install']) == {
            'grub-common', 'grub2-common', 'grub-pc-bin',
            'grub-efi-amd64-bin', 'efibootmgr'
        }
for mapping in configs['unpackfs']['unpack']:
    assert {'source', 'sourcefs', 'destination'} <= mapping.keys()

if args.root:
    deployed_brand = args.root / 'etc/calamares/branding/katu'
    assert (deployed_brand / 'stylesheet.qss').is_file(), 'Calamares Katu stylesheet is not deployed'
    sddm_theme = args.root / 'usr/share/sddm/themes/katu'
    assert (sddm_theme / 'Main.qml').is_file(), 'Katu SDDM theme is not deployed'
    sddm_config = args.root / 'etc/sddm.conf.d/katu.conf'
    assert sddm_config.is_file(), 'Katu SDDM configuration is missing'
    assert 'Current=katu' in sddm_config.read_text(encoding='utf-8'), 'Katu SDDM theme is not selected'
    module_dirs = list((args.root / 'usr/lib').glob('**/calamares/modules'))
    for name in set(steps):
        assert any((d / name).is_dir() for d in module_dirs), f'Module not installed: {name}'
    for path in ['usr/bin/calamares', 'usr/bin/katu-installer', 'usr/bin/pkexec',
                 'usr/bin/kdialog', 'usr/sbin/grub-install', 'usr/sbin/grub-mkconfig',
                 'usr/sbin/update-initramfs', 'usr/lib/grub/x86_64-efi/modinfo.sh',
                 'usr/lib/grub/i386-pc/modinfo.sh']:
        assert (args.root / path).exists(), f'Missing installer dependency: {path}'

print('Installer configuration and dependencies: PASS')
