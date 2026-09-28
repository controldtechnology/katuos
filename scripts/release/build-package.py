#!/usr/bin/env python3
"""Stage one existing Debian package; version always comes from its control file."""
import argparse
import gzip
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]


def build(name, output):
    if not re.fullmatch(r'katu-[a-z0-9][a-z0-9+-]*', name):
        raise ValueError('Invalid package name')
    source = ROOT / 'packages' / name
    control = (source / 'DEBIAN/control').read_text(encoding='utf-8-sig')
    version = re.search(r'^Version: (.+)$', control, re.M).group(1)
    arch = re.search(r'^Architecture: (.+)$', control, re.M).group(1)
    if not re.fullmatch(r'\d+\.\d+\.\d+(?:-[1-9]\d*)?', version):
        raise ValueError('Use MAJOR.MINOR.PATCH in DEBIAN/control')
    output.mkdir(parents=True, exist_ok=True)
    destination = output / f'{name}_{version}_{arch}.deb'
    if destination.exists():
        raise ValueError('Immutable artifact already exists; increment version or use a clean output directory')
    with tempfile.TemporaryDirectory(prefix='katu-package-') as temp:
        stage = Path(temp) / name
        shutil.copytree(source, stage)
        # All configuration files use dpkg conffile semantics, including existing settings.
        configs = sorted('/' + p.relative_to(stage).as_posix() for p in (stage / 'etc').rglob('*') if p.is_file()) if (stage / 'etc').exists() else []
        if configs:
            (stage / 'DEBIAN/conffiles').write_text('\n'.join(configs) + '\n')
        changelog = stage / 'DEBIAN/changelog'
        if not changelog.exists() or f'({version})' not in changelog.read_text(encoding='utf-8-sig').splitlines()[0]:
            raise ValueError('Changelog does not match package version')
        doc = stage / 'usr/share/doc' / name
        doc.mkdir(parents=True, exist_ok=True)
        with (doc / 'changelog.Debian.gz').open('wb') as stream:
            with gzip.GzipFile(fileobj=stream, mode='wb', mtime=0) as gz:
                gz.write(changelog.read_bytes().replace(b'\r\n', b'\n'))
        for path in stage.rglob('*'):
            if path.is_symlink():
                continue
            if path.is_dir():
                path.chmod(0o755)
                continue
            raw = path.read_bytes()
            executable = raw.startswith(b'#!') or path.parent == stage / 'usr/bin'
            if b'\0' not in raw[:4096]:
                try:
                    normalized = raw.decode('utf-8-sig').replace('\r\n', '\n')
                    path.write_bytes(normalized.encode('utf-8'))
                except UnicodeDecodeError:
                    pass
            path.chmod(0o755 if executable else 0o644)
        subprocess.run(['dpkg-deb', '--build', '--root-owner-group', str(stage), str(destination)], check=True)
    print(destination)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('package')
    parser.add_argument('--output', type=Path, default=ROOT / 'output/packages')
    args = parser.parse_args()
    build(args.package, args.output)
