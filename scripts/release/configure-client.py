#!/usr/bin/env python3
"""One-time trust bootstrap from an independently verified public key."""
import argparse
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from urllib.parse import urlsplit


def configure(url, channel, key, fingerprint, root):
    parsed = urlsplit(url)
    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment or any(c.isspace() for c in url):
        raise ValueError('Repository URL must be credential-free HTTPS')
    if channel not in ('stable', 'beta'):
        raise ValueError('Unsupported channel')
    if not re.fullmatch(r'[A-Fa-f0-9]{40,64}', fingerprint):
        raise ValueError('Full public fingerprint required')
    raw = key.read_bytes()
    if b'PRIVATE KEY' in raw or b'-----BEGIN PGP PUBLIC KEY BLOCK-----' not in raw:
        raise ValueError('Only an armored public key is accepted')
    with tempfile.TemporaryDirectory() as tmp:
        output = subprocess.check_output(['gpg', '--homedir', tmp, '--batch', '--with-colons', '--show-keys', str(key)], text=True)
    primary = []
    want = False
    for line in output.splitlines():
        fields = line.split(':')
        if fields[0] == 'pub':
            want = True
        elif fields[0] == 'fpr' and want:
            primary.append(fields[9])
            want = False
    if primary != [fingerprint.upper()]:
        raise ValueError('Public key fingerprint mismatch')
    keydir = root / 'etc/apt/keyrings'
    sources = root / 'etc/apt/sources.list.d'
    preferences = root / 'etc/apt/preferences.d'
    for directory in (keydir, sources, preferences):
        directory.mkdir(parents=True, exist_ok=True)
    def put(path, data):
        if path.exists() and path.read_bytes() != data and not path.with_suffix(path.suffix + '.pre-katu').exists():
            shutil.copy2(path, path.with_suffix(path.suffix + '.pre-katu'))
        temp = path.with_suffix(path.suffix + '.tmp')
        temp.write_bytes(data)
        temp.chmod(0o644)
        temp.replace(path)
    put(keydir / 'katu-archive-keyring.asc', raw)
    put(sources / 'katu.sources', f'Types: deb\nURIs: {url.rstrip("/")}\nSuites: {channel}\nComponents: main\nArchitectures: amd64\nSigned-By: /etc/apt/keyrings/katu-archive-keyring.asc\nCheck-Valid-Until: yes\n'.encode())
    blocked = 'beta' if channel == 'stable' else 'stable'
    put(preferences / 'katu-channels', f'Package: *\nPin: release o=Katu OS,n={blocked}\nPin-Priority: -1\n'.encode())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', default='https://repo.katuos.com.br')
    parser.add_argument('--channel', choices=['stable', 'beta'], default='stable')
    parser.add_argument('--key', type=Path, required=True)
    parser.add_argument('--fingerprint', required=True)
    parser.add_argument('--root', type=Path, default=Path('/'))
    args = parser.parse_args()
    if args.root == Path('/') and os.geteuid() != 0:
        parser.error('Run as administrator')
    configure(args.url, args.channel, args.key, args.fingerprint, args.root)
