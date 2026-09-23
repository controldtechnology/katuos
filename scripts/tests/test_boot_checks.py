import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from boot_checks import grub_entries


class BootRegressionTests(unittest.TestCase):
    def check(self, kernel='/live/vmlinuz', params='${LIVE}', initrd='/live/initrd.img'):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'live').mkdir()
            (root / 'live/vmlinuz').touch()
            (root / 'live/initrd.img').touch()
            config = root / 'grub.cfg'
            config.write_text('set LIVE="boot=live components"\nmenuentry "Katu" {\n'
                              f'linux {kernel} {params}\ninitrd {initrd}\n}}\n')
            return grub_entries(config, root)

    def test_expands_live_parameters(self):
        self.assertEqual(self.check()[0]['params'], ['boot=live', 'components'])

    def test_rejects_virtualbox_unattended_rewrite(self):
        with self.assertRaisesRegex(RuntimeError, 'missing boot=live'):
            self.check(params='auto=true preseed/file=/cdrom/preseed.cfg quiet splash automatic-ubiquity')

    def test_rejects_literal_wildcard(self):
        with self.assertRaisesRegex(RuntimeError, 'unresolved boot path'):
            self.check(kernel='/live/vmlinuz-*')

    def test_rejects_missing_initrd(self):
        with self.assertRaisesRegex(RuntimeError, 'missing /live/initrd-wrong'):
            self.check(initrd='/live/initrd-wrong')

    def test_rejects_mixed_live_model(self):
        with self.assertRaisesRegex(RuntimeError, 'mixed Live'):
            self.check(params='boot=live boot=casper')

if __name__ == '__main__':
    unittest.main()
