#!/usr/bin/env python3
"""Signed APT repository, immutable pool, beta-to-stable artifact promotion.

Uses apt-ftparchive/GnuPG; signing home must be outside the served root.
Public root is switched atomically through a symlink on the same filesystem.
"""
import argparse
import datetime
import fcntl
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

GATES = ('build', 'clean_install', 'upgrade', 'functional', 'dependencies', 'removal',
         'no_critical_regression', 'signature', 'installed_katu')


def run(args, **kwargs):
    return subprocess.check_output(args, **kwargs)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def publish(channel, debs, root, evidence):
    key = os.environ['KATU_SIGNING_KEY']
    if not re.fullmatch(r'[A-Fa-f0-9]{40,64}', key):
        raise ValueError('Use the full signing fingerprint')
    gnupg = Path(os.environ['GNUPGHOME']).resolve()
    root = root.resolve()
    if gnupg == root or root in gnupg.parents:
        raise ValueError('Signing key must not be inside repository storage')
    root.mkdir(parents=True, exist_ok=True)
    with (root / '.publish.lock').open('w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        current = root / 'public'
        records = {}
        if (current / 'ledger.json').exists():
            records = json.loads((current / 'ledger.json').read_text())
        gate = json.loads(evidence.read_text()) if evidence else {}
        for deb in debs:
            digest = sha(deb)
            if channel == 'stable':
                if not all(gate.get(digest, {}).get(g) is True for g in GATES):
                    raise ValueError('Missing stable validation evidence for ' + deb.name)
                if digest not in records.get('beta', {}):
                    raise ValueError('Stable must promote the exact beta SHA-256')
        generations = root / 'generations'
        generations.mkdir(exist_ok=True)
        stage = Path(tempfile.mkdtemp(prefix='release-', dir=generations))
        if current.exists():
            shutil.copytree(current, stage, dirs_exist_ok=True)
        pool = stage / 'pool/main'
        pool.mkdir(parents=True, exist_ok=True)
        selected = records.setdefault(channel, {})
        for deb in debs:
            metadata = run(['dpkg-deb', '-f', str(deb), 'Package', 'Version', 'Architecture'], text=True)
            values = dict(line.split(': ', 1) for line in metadata.strip().splitlines())
            name, version, arch = (values[k] for k in ('Package', 'Version', 'Architecture'))
            if not re.fullmatch(r'katu-[a-z0-9+.-]+', name) or not re.fullmatch(r'\d+\.\d+\.\d+(?:-[1-9]\d*)?', version) or arch not in ('all', 'amd64'):
                raise ValueError('Unsupported package metadata')
            target = pool / f'{name}_{version}_{arch}.deb'
            digest = sha(deb)
            if target.exists() and sha(target) != digest:
                raise ValueError('Published version is immutable')
            shutil.copy2(deb, target)
            selected[digest] = dict(path=target.relative_to(stage).as_posix(), name=name, version=version)
        for suite in ('stable', 'beta'):
            binary = stage / 'dists' / suite / 'main/binary-amd64'
            binary.mkdir(parents=True, exist_ok=True)
            paragraphs = []
            for item in records.get(suite, {}).values():
                paragraphs.append(run(['apt-ftparchive', 'packages', item['path']], cwd=stage))
            content = b''.join(paragraphs)
            (binary / 'Packages').write_bytes(content)
            (binary / 'Packages.gz').write_bytes(gzip.compress(content, mtime=0))
            suite_dir = stage / 'dists' / suite
            for old in ('Release', 'InRelease', 'Release.gpg'):
                (suite_dir / old).unlink(missing_ok=True)
            valid = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=14)).strftime('%a, %d %b %Y %H:%M:%S UTC')
            release = run(['apt-ftparchive', '-o', 'APT::FTPArchive::Release::Origin=Katu OS',
                           '-o', 'APT::FTPArchive::Release::Label=Katu OS',
                           '-o', 'APT::FTPArchive::Release::Suite=' + suite,
                           '-o', 'APT::FTPArchive::Release::Codename=' + suite,
                           '-o', 'APT::FTPArchive::Release::Architectures=amd64 all',
                           '-o', 'APT::FTPArchive::Release::Components=main',
                           'release', '.'], cwd=suite_dir)
            (suite_dir / 'Release').write_bytes(b'Valid-Until: ' + valid.encode() + b'\n' + release)
            for flags, filename in ((['--clearsign'], 'InRelease'), (['--armor', '--detach-sign'], 'Release.gpg')):
                subprocess.run(['gpg', '--batch', '--yes', '--local-user', key, '--digest-algo', 'SHA256',
                                '--output', str(suite_dir / filename)] + flags + [str(suite_dir / 'Release')], check=True)
        (stage / 'katu-archive-keyring.asc').write_bytes(run(['gpg', '--armor', '--export', key]))
        (stage / 'ledger.json').write_text(json.dumps(records, indent=2))
        link = root / '.public-next'
        link.unlink(missing_ok=True)
        link.symlink_to(stage.relative_to(root), target_is_directory=True)
        link.replace(current)
        print(current)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['publish'])
    parser.add_argument('channel', choices=['stable', 'beta'])
    parser.add_argument('debs', nargs='+', type=Path)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--evidence', type=Path)
    args = parser.parse_args()
    publish(args.channel, args.debs, args.root, args.evidence)
