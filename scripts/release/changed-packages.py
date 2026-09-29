#!/usr/bin/env python3
"""Map source changes to the smallest reviewable set of Debian artifacts."""
import argparse
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('--base', required=True)
args = parser.parse_args()
paths = subprocess.check_output(['git', 'diff', '--name-only', args.base, 'HEAD'], text=True).splitlines()
packages = set()
all_packages = False
assets = {
    'katu-icons': ('/usr/share/icons/', '/usr/share/icons/katu/'),
    'katu-theme': ('/usr/share/color-schemes/', '/usr/share/plasma/look-and-feel/'),
    'katu-wallpapers': ('/usr/share/wallpapers/',),
    'katu-branding': ('/usr/share/katu/branding/', '/usr/share/pixmaps/'),
}
for path in paths:
    parts = path.split('/')
    if parts[0] == 'packages' and len(parts) > 1:
        packages.add(parts[1])
    elif path.startswith(('scripts/release/', 'scripts/tests/', '.github/workflows/')):
        all_packages = True
    elif path.startswith('config/includes.chroot/usr/share/'):
        relative = path.split('config/includes.chroot', 1)[1]
        owners = [name for name, prefixes in assets.items() if any(relative.startswith(prefix) for prefix in prefixes)]
        packages.update(owners or ['katu-branding'])
    elif path.startswith(('packages/katu-update/usr/lib/katu-update/', 'packages/katu-update/usr/lib/systemd/',
                          'packages/katu-update/usr/share/polkit-1/')):
        packages.add('katu-update')
    elif path.startswith('config/hooks/') or path.startswith('installer/'):
        packages.update(['katu-installer', 'katu-desktop'])
if all_packages:
    import pathlib
    packages = {p.name for p in pathlib.Path('packages').iterdir() if p.is_dir()}
for name in sorted(packages):
    print(name)
