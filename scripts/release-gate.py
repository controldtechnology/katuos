#!/usr/bin/env python3
"""Only copy an ISO to release/ with matching automated AND manual evidence."""
import argparse
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from boot_checks import require, sha256_file

parser = argparse.ArgumentParser()
parser.add_argument('iso', type=Path)
parser.add_argument('--candidate', action='store_true')
parser.add_argument('--manual', type=Path)
parser.add_argument('--commit', required=True)
parser.add_argument('--build-date', required=True)
args = parser.parse_args()
digest = sha256_file(args.iso)
reports = {}
for kind in ['validation', 'smoke']:
    reports[kind] = json.loads(Path(str(args.iso) + '.' + kind + '.json').read_text())
    require(reports[kind]['status'] == 'PASS' and reports[kind]['sha256'] == digest,
            f'{kind}: not PASS for this exact ISO')
manual = {'sha256': digest, 'tests': {name: 'NOT TESTED' for name in
          ['VIRTUALBOX LIVE', 'VIRTUALBOX INSTALLATION', 'BOOT WITHOUT ISO', 'BRANDING', 'PHYSICAL USB']}}
if args.manual:
    manual = json.loads(args.manual.read_text())
    require(manual['sha256'] == digest, 'Manual results are for another ISO')
if not args.candidate:
    require(args.manual, 'Release requires manual evidence for this exact ISO')
    for name in ['VIRTUALBOX LIVE', 'VIRTUALBOX INSTALLATION', 'BOOT WITHOUT ISO', 'BRANDING']:
        result = manual['tests'].get(name, {})
        require(isinstance(result, dict) and result.get('status') == 'PASS' and result.get('evidence'),
                f'{name}: missing PASS with evidence')
    require(manual['tests'].get('PHYSICAL USB') is not None, 'USB status must be explicit')
    destination = Path(__file__).resolve().parents[1] / 'release' / args.iso.stem
    destination.mkdir(parents=True, exist_ok=False)
    shutil.copy2(args.iso, destination / args.iso.name)
else:
    destination = args.iso.parent
manifest = {
    'version': (Path(__file__).resolve().parents[1] / 'VERSION').read_text().strip(),
    'architecture': 'amd64', 'git_commit': args.commit, 'build_date': args.build_date,
    'validated_at': datetime.now(timezone.utc).isoformat(), 'iso': args.iso.name,
    'size': args.iso.stat().st_size, 'sha256': digest, 'label': reports['validation']['label'],
    'kernel': reports['validation']['kernel'], 'packages': reports['validation']['packages'],
    'live_build': subprocess.check_output(['dpkg-query', '-W', '-f=${Version}', 'live-build'], text=True),
    'automated': reports, 'manual': manual, 'release': not args.candidate,
}
(destination / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
(destination / 'SHA256SUMS').write_text(f'{digest}  {args.iso.name}\n')
print('CANDIDATE ONLY' if args.candidate else 'RELEASE GATE: PASS')
