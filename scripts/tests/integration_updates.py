#!/usr/bin/env python3
"""Real APT/GPG/dpkg acceptance in a DISPOSABLE Debian container only."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts/release'))
sys.path.insert(0, str(ROOT / 'packages/katu-update/usr/lib/katu-update'))
import repository
import backend


def command(*args, ok=True):
    result = subprocess.run(args, text=True, capture_output=True)
    if ok and result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    return result


class AptIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if os.environ.get('KATU_DISPOSABLE_TEST') != '1' or not Path('/.dockerenv').exists():
            raise unittest.SkipTest('Requires explicitly marked disposable Docker container')
        cls.temp = tempfile.TemporaryDirectory(prefix='katu-apt-')
        cls.work = Path(cls.temp.name)
        cls.work.chmod(0o755)
        updater_deb = ROOT / 'output/packages/katu-update_1.1.0_all.deb'
        if not updater_deb.exists():
            command(sys.executable, str(ROOT / 'scripts/release/build-package.py'),
                    'katu-update', '--output', str(updater_deb.parent))
        cls.gpg = cls.work / 'signing'
        cls.gpg.mkdir(mode=0o700)
        os.environ['GNUPGHOME'] = str(cls.gpg)
        command('gpg', '--batch', '--passphrase', '', '--quick-generate-key', 'Katu disposable test', 'rsa2048', 'sign', '1d')
        listing = command('gpg', '--with-colons', '--list-keys').stdout
        cls.key = next(line.split(':')[9] for line in listing.splitlines() if line.startswith('fpr:'))
        os.environ['KATU_SIGNING_KEY'] = cls.key
        cls.repo = cls.work / 'repo'
        # Container dependencies were installed before isolating the sources.
        for file in Path('/etc/apt/sources.list.d').glob('*'):
            if file.is_file():
                file.rename(cls.work / file.name)
        Path('/etc/apt/sources.list').write_text('')
        cls.source = Path('/etc/apt/sources.list.d/katu-test.list')
        cls.publickey = cls.work / 'public.asc'
        cls.publickey.write_text(command('gpg', '--armor', '--export', cls.key).stdout)
        cls.source.write_text(f'deb [signed-by={cls.publickey}] file:{cls.repo}/public beta main\n')
        # Root-only generation directories must still permit APT's _apt user to read.
        cls.counter = 0

    @classmethod
    def package(cls, name, version, depends=''):
        cls.counter += 1
        directory = cls.work / f'pkg-{cls.counter}'
        (directory / 'DEBIAN').mkdir(parents=True)
        (directory / 'DEBIAN/control').write_text(f'Package: {name}\nVersion: {version}\nArchitecture: all\nMaintainer: Test <test@example.invalid>\nDescription: Integration fixture\n' + (f'Depends: {depends}\n' if depends else ''))
        payload = directory / 'usr/share/katu-test' / name
        payload.parent.mkdir(parents=True)
        payload.write_text(version)
        deb = cls.work / f'{name}_{version}_all.deb'
        command('dpkg-deb', '--build', '--root-owner-group', str(directory), str(deb))
        return deb

    @classmethod
    def publish(cls, *debs):
        repository.publish('beta', list(debs), cls.repo, None)
        for directory in (cls.repo / 'generations').iterdir():
            directory.chmod(0o755)
        command('apt-get', '-o', 'APT::Update::Error-Mode=any', 'update')

    def install(self, *names):
        command('apt-get', '-y', '--no-install-recommends', 'install', *names)

    def test_01_single_package_and_no_update(self):
        self.publish(self.package('katu-ai', '1.0.0'), self.package('katu-central', '1.0.0'))
        self.install('katu-ai', 'katu-central')
        self.assertEqual(backend.make_plan()['packages'], [])
        self.publish(self.package('katu-ai', '1.1.0'))
        plan = backend.make_plan()
        self.assertEqual([p['name'] for p in plan['packages']], ['katu-ai'])
        self.install('katu-ai=1.1.0')
        backend.verify_versions(plan)
        self.assertEqual(command('dpkg-query', '-W', '-f=${Version}', 'katu-central').stdout, '1.0.0')

    def test_02_real_dependencies(self):
        self.publish(self.package('katu-core', '1.0.0'))
        self.install('katu-core')
        self.publish(self.package('katu-core', '1.1.0'), self.package('katu-ai', '1.2.0', 'katu-core (>= 1.1.0)'))
        plan = backend.make_plan(['katu-ai'])
        self.assertEqual({p['name'] for p in plan['packages']}, {'katu-ai', 'katu-core'})
        self.install('katu-ai=1.2.0')
        backend.verify_versions(plan)

    def test_03_new_app_via_meta(self):
        self.publish(self.package('katu-desktop', '1.0.0'))
        self.install('katu-desktop')
        self.publish(self.package('katu-example', '1.0.0'), self.package('katu-desktop', '1.1.0', 'katu-example'))
        plan = backend.make_plan(['katu-desktop'])
        self.assertEqual({p['name'] for p in plan['packages']}, {'katu-desktop', 'katu-example'})
        self.install('katu-desktop=1.1.0')
        backend.verify_versions(plan)

    def test_04_icons_only(self):
        self.publish(self.package('katu-icons', '1.0.0'))
        self.install('katu-icons')
        self.publish(self.package('katu-icons', '1.1.0'))
        plan = backend.make_plan()
        self.assertEqual([p['name'] for p in plan['packages']], ['katu-icons'])
        self.install('katu-icons=1.1.0')
        backend.verify_versions(plan)

    def test_05_invalid_signature(self):
        release = self.repo / 'public/dists/beta/InRelease'
        original = release.read_bytes()
        release.write_bytes(original.replace(b'Origin: Katu OS', b'Origin: Bad OS!'))
        self.assertNotEqual(command('apt-get', '-o', 'APT::Update::Error-Mode=any', 'update', ok=False).returncode, 0)
        release.write_bytes(original)
        command('apt-get', 'update')

    def test_06_corrupt_package(self):
        deb = self.package('katu-example', '1.1.0')
        self.publish(deb)
        target = self.repo / 'public/pool/main' / deb.name
        original = target.read_bytes()
        target.write_bytes(b'corrupt' + original[7:])
        self.assertNotEqual(command('apt-get', '-y', '--download-only', 'install', 'katu-example=1.1.0', ok=False).returncode, 0)
        self.assertEqual(command('dpkg-query', '-W', '-f=${Version}', 'katu-example').stdout, '1.0.0')
        target.write_bytes(original)

    def test_07_stable_requires_evidence(self):
        deb = self.package('katu-example', '1.2.0')
        with self.assertRaisesRegex(ValueError, 'Missing stable'):
            repository.publish('stable', [deb], self.repo, None)

    def test_08_offline_refresh_fails(self):
        source = self.source.read_text()
        self.source.write_text('deb http://127.0.0.1:9/unavailable stable main\n')
        self.assertNotEqual(command('apt-get', '-o', 'APT::Update::Error-Mode=any', '-o', 'Acquire::Retries=0', 'update', ok=False).returncode, 0)
        self.source.write_text(source)


    def test_09_actual_updater_self_upgrade(self):
        original = ROOT / 'output/packages/katu-update_1.1.0_all.deb'
        self.publish(original)
        self.install('katu-update=1.1.0')
        stage = self.work / 'updater-next'
        command('dpkg-deb', '-R', str(original), str(stage))
        control = stage / 'DEBIAN/control'
        control.write_text(control.read_text().replace('Version: 1.1.0', 'Version: 1.1.1'))
        newer = self.work / 'katu-update_1.1.1_all.deb'
        command('dpkg-deb', '--build', '--root-owner-group', str(stage), str(newer))
        self.publish(newer)
        plan = backend.make_plan(['katu-update'])
        result = command('/usr/lib/katu-update/helper', 'apply', plan['digest'], 'katu-update', ok=False)
        status = json.loads(Path('/var/lib/katu-update/status.json').read_text())
        self.assertEqual(result.returncode, 0, status)
        backend.verify_versions(plan)
        self.assertTrue(status['ok'])
        self.assertEqual(status['phase'], 'complete')
        self.assertTrue(Path('/var/lib/katu-update/history.jsonl').read_text())

    def test_10_build_release_index_fields(self):
        deb = self.package('katu-example', '1.3.0')
        metadata = command('dpkg-deb', '-f', str(deb)).stdout
        fields = dict(line.split(': ', 1) for line in metadata.splitlines() if ': ' in line)
        self.assertEqual(fields['Package'], 'katu-example')
        self.assertEqual(fields['Version'], '1.3.0')

    def test_11_broken_dependency_rejected(self):
        self.publish(self.package('katu-broken', '1.0.0', 'katu-missing (>= 9.0.0)'))
        with self.assertRaises(Exception):
            backend.make_plan(['katu-broken'])

    def test_12_plan_change_rejected(self):
        plan = backend.make_plan(['katu-example'])
        self.publish(self.package('katu-example', '1.2.0'))
        result = command('/usr/lib/katu-update/helper', 'apply', plan['digest'], 'katu-example', ok=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(command('dpkg-query', '-W', '-f=${Version}', 'katu-example').stdout, '1.0.0')

    def test_13_theme_and_hold(self):
        self.publish(self.package('katu-theme', '1.0.0'))
        self.install('katu-theme')
        self.publish(self.package('katu-theme', '1.1.0'))
        command('apt-mark', 'hold', 'katu-theme')
        with self.assertRaisesRegex(backend.UpdateError, 'retido'):
            backend.make_plan(['katu-theme'])
        self.assertNotIn('katu-theme', [p['name'] for p in backend.make_plan()['packages']])
        command('apt-mark', 'unhold', 'katu-theme')
        plan = backend.make_plan(['katu-theme'])
        self.assertEqual([p['name'] for p in plan['packages']], ['katu-theme'])

    def test_14_unreviewed_beta_cannot_promote(self):
        deb = self.package('katu-unreviewed', '1.0.0')
        evidence = self.work / 'approval.json'
        evidence.write_text(json.dumps({repository.sha(deb): dict.fromkeys(repository.GATES, True)}))
        with self.assertRaisesRegex(ValueError, 'exact beta'):
            repository.publish('stable', [deb], self.repo, evidence)


if __name__ == '__main__':
    unittest.main(verbosity=2)
