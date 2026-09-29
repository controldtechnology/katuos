#!/usr/bin/env python3
"""Map source changes to the smallest reviewable set of Debian artifacts."""
import argparse
import json
from pathlib import Path
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('--event')
parser.add_argument('--base')
args = parser.parse_args()
paths = []
all_packages = False
if args.event:
    event = json.loads(Path(args.event).read_text())
    if 'commits' in event:
        for commit in event['commits']:
            for kind in ('added', 'modified', 'removed'):
                paths.extend(commit.get(kind, []))
    else:
        all_packages = True
else:
    base = args.base or 'HEAD^'
    if subprocess.run(['git', 'cat-file', '-e', base + '^{commit}'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode:
        base = 'HEAD^'
    if subprocess.run(['git', 'cat-file', '-e', base + '^{commit}'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode:
        all_packages = True
    else:
        paths = subprocess.check_output(['git', 'diff', '--name-only', base, 'HEAD'], text=True).splitlines()
packages = set()
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
    elif path == 'scripts/release/build-package.py':
        all_packages = True
    elif path.startswith('config/includes.chroot/usr/share/'):
        relative = path.split('config/includes.chroot', 1)[1]
        owners = [name for name, prefixes in assets.items() if any(relative.startswith(prefix) for prefix in prefixes)]
        packages.update(owners or ['katu-branding'])
    elif path.startswith('config/hooks/') or path.startswith('installer/'):
        packages.update(['katu-installer', 'katu-desktop'])
if all_packages:
    import pathlib
    packages = {p.name for p in pathlib.Path('packages').iterdir() if p.is_dir()}
for name in sorted(packages):
    print(name)
