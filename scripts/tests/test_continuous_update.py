"""Fast failure-path tests; these do not claim installed-system acceptance."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'packages/katu-update/usr/lib/katu-update'))
import backend


class FailureTests(unittest.TestCase):
    def test_no_space(self):
        with patch.object(backend.shutil, 'disk_usage', return_value=types.SimpleNamespace(free=10)):
            with self.assertRaisesRegex(backend.UpdateError, 'Espaço'):
                backend.preflight(dict(download=1024, disk=0, critical=False))

    def test_command_failure_not_empty_success(self):
        with patch.object(backend.subprocess, 'run', return_value=types.SimpleNamespace(returncode=100)):
            with self.assertRaises(backend.UpdateError):
                backend.run(['apt-get', 'update'])

    def test_version_must_be_verified(self):
        with patch.object(backend, 'run', return_value='installed\t1.0.0'):
            with self.assertRaisesRegex(backend.UpdateError, 'Validação'):
                backend.verify_versions({'packages': [{'name': 'katu-ai', 'version': '1.1.0'}]})

    def test_audit_failure(self):
        with patch.object(backend, 'run', side_effect=['installed\t1.1.0', 'unconfigured package']):
            with self.assertRaisesRegex(backend.UpdateError, 'pendentes'):
                backend.verify_versions({'packages': [{'name': 'katu-ai', 'version': '1.1.0'}]})

    def test_success_requires_installed_state(self):
        with patch.object(backend, 'run', return_value='unpacked\t1.1.0'):
            with self.assertRaises(backend.UpdateError):
                backend.verify_versions({'packages': [{'name': 'katu-ai', 'version': '1.1.0'}]})

    def test_no_flatpak_is_supported(self):
        with patch.object(backend.shutil, 'which', return_value=None):
            self.assertEqual(backend.flatpak_plan(), [])

    def test_flatpak_failure_propagates(self):
        with patch.object(backend.shutil, 'which', return_value='/usr/bin/flatpak'), patch.object(backend, 'run', side_effect=backend.UpdateError('offline')):
            with self.assertRaises(backend.UpdateError):
                backend.flatpak_plan()

    def test_migrations_idempotent(self):
        spec = importlib.util.spec_from_file_location('migrate', ROOT / 'packages/katu-update/usr/lib/katu-update/migrate.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as directory:
            module.STATE = Path(directory)
            module.migrate()
            first = (module.STATE / '001-continuous-update.json').read_bytes()
            module.migrate()
            self.assertEqual(first, (module.STATE / '001-continuous-update.json').read_bytes())


if __name__ == '__main__':
    unittest.main()
