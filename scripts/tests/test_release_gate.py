import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class ReleaseGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / 'scripts').mkdir()
        for name in ['release-gate.py', 'boot_checks.py']:
            shutil.copyfile(Path(__file__).resolve().parents[1] / name, self.root / 'scripts' / name)
        self.iso = self.root / 'test.iso'
        self.iso.write_bytes(b'not a real iso: gate fixture')
        self.digest = hashlib.sha256(self.iso.read_bytes()).hexdigest()
        checks = {name: 'PASS' for name in ['ISO STRUCTURE', 'GRUB', 'SQUASHFS', 'KERNEL',
                  'INITRD', 'LIVE-BOOT', 'KERNEL/MODULES', 'INSTALLER STRUCTURE',
                  'BRANDING STRUCTURE', 'UEFI STRUCTURE', 'BIOS STRUCTURE']}
        self.validation = {'status': 'PASS', 'sha256': self.digest, 'checks': checks}
        self.smoke = {'status': 'PASS', 'sha256': self.digest}

    def tearDown(self):
        self.temp.cleanup()

    def run_gate(self):
        for name, report in [('validation', self.validation), ('smoke', self.smoke)]:
            Path(str(self.iso) + '.' + name + '.json').write_text(json.dumps(report))
        result = subprocess.run([sys.executable, str(self.root / 'scripts/release-gate.py'),
                                 str(self.iso), '--commit', 'fixture', '--build-date', 'fixture'],
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.root / 'release').exists())
        return result.stderr

    def test_not_tested_manual_cannot_publish(self):
        self.assertIn('Release requires manual evidence', self.run_gate())

    def test_smoke_from_other_iso_cannot_publish(self):
        self.smoke['sha256'] = 'different'
        self.assertIn('smoke: not PASS for this exact ISO', self.run_gate())

    def test_incomplete_structure_report_cannot_publish(self):
        self.validation['checks'].pop('INITRD')
        self.assertIn('Missing check: INITRD', self.run_gate())

if __name__ == '__main__':
    unittest.main()
