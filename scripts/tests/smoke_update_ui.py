#!/usr/bin/env python3
"""Exercise existing GUI with a reviewed plan; no package operations."""
import importlib.util
from pathlib import Path
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
directory = ROOT / 'packages/katu-update/usr/lib/katu-update'
sys.path.insert(0, str(directory))
spec = importlib.util.spec_from_file_location('katu_update_ui', directory / 'main.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
app = module.QApplication([])
with patch.object(module.QTimer, 'singleShot'):
    window = module.KatuUpdate()
window._on_check_done(dict(packages=[dict(name='katu-ai', installed='1.0.0', version='1.1.0', origin='Katu', category='Nova funcionalidade', notes='Exemplo de atualização de um componente.')], download=1024*1024, optional=[]), [])
assert window._update_btn.isEnabled()
assert window._list.count() == 1
window.show()
app.processEvents()
assert window.grab().save(str(ROOT / 'output/update-ui.png'))
window._on_check_failed('Servidor indisponível')
assert not window._update_btn.isEnabled()
assert 'Não foi possível' in window._status_text.text()
window._on_check_done(dict(packages=[], download=0, optional=[]), [])
assert not window._update_btn.isEnabled()
print('Qt: one update, failure, and no updates verified')
