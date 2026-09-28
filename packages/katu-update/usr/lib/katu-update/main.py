#!/usr/bin/env python3
"""
Katu Update — Gerenciador de Atualizações do Katu OS
Mantenha seu sistema atualizado sem usar o terminal.
"""
import sys, os, subprocess
from pathlib import Path
import json, time
sys.path.insert(0, '/usr/lib/katu-update')
import backend

try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
    from PyQt5.QtGui import *
    QT = 'PyQt5'
except ImportError:
    from PySide6.QtWidgets import *
    from PySide6.QtCore import Qt, QThread, Signal as pyqtSignal, QTimer
    from PySide6.QtGui import *
    QT = 'PySide6'

sys.path.insert(0, '/usr/lib/python3/dist-packages')
try:
    from katu_core import ui, notifications
    CORE = True
except ImportError:
    CORE = False
    class _FakeUI:
        STYLESHEET = ""; BG = "#0d1117"; SURFACE = "#161b22"; CARD = "#1c2128"
        BORDER = "#30363d"; ACCENT = "#00c853"; TEXT = "#e6edf3"; MUTED = "#8b949e"
        ERROR = "#f85149"; AMBER = "#ffab00"; SUCCESS = "#3fb950"; TEXT_INV = "#0d1117"
    ui = _FakeUI()
    class notifications:
        @staticmethod
        def notify_success(a, b=""): pass
        @staticmethod
        def notify_error(a, b=""): pass


class CheckThread(QThread):
    progress = pyqtSignal(str)
    done = pyqtSignal(dict, list)
    failed = pyqtSignal(str)

    def __init__(self, selected=None):
        super().__init__()
        self.selected = selected

    def run(self):
        try:
            self.progress.emit("Atualizando índices autenticados...")
            backend.run(['pkexec', backend.HELPER, 'refresh'], timeout=900)
            plan = backend.make_plan(self.selected)
            plan['optional'] = backend.optional_apps()
            flat = backend.flatpak_plan()
            self.done.emit(plan, flat)
        except Exception as exc:
            self.failed.emit(str(exc))


class UpgradeThread(QThread):
    progress = pyqtSignal(str)
    done = pyqtSignal(bool)

    def __init__(self, plan, flat):
        super().__init__()
        self.plan, self.flat = plan, flat

    def run(self):
        try:
            if self.plan['packages']:
                backend.preflight(self.plan)
                backend.run(['pkexec', backend.HELPER, 'start', self.plan['digest']] + self.plan['selected'])
                started = time.time()
                while True:
                    state = backend.read_state()
                    if state.get('id') == self.plan['digest'] and state.get('started', 0) >= started - 10:
                        phase = state.get('phase', '')
                        self.progress.emit({'validating': 'Validando...', 'downloading': 'Baixando pacotes autenticados...',
                                            'installing': 'Instalando; não desligue o computador.',
                                            'verifying': 'Validando versões instaladas...'}.get(phase, phase))
                        if phase in ('complete', 'failed'):
                            if not state.get('ok'):
                                raise backend.UpdateError(state.get('error', 'Falha na atualização.'))
                            break
                    active = subprocess.run(['systemctl', 'is-active', '--quiet', backend.UNIT]).returncode == 0
                    if not active and time.time() - started > 10:
                        raise backend.UpdateError('Transação interrompida. Consulte o histórico e verifique o dpkg.')
                    time.sleep(1)
            for scope in ('user', 'system'):
                refs = [item['ref'] for item in self.flat if item['scope'] == scope]
                if refs:
                    self.progress.emit('Atualizando Flatpak (' + scope + ')...')
                    backend.run(['flatpak', 'update', '--' + scope, '--noninteractive'] + refs, timeout=None)
            if self.flat:
                remaining = {(p['scope'], p['ref']) for p in backend.flatpak_plan()}
                if any((p['scope'], p['ref']) in remaining for p in self.flat):
                    raise backend.UpdateError('Flatpak ainda possui atualizações pendentes; verifique novamente.')
            self.done.emit(True)
        except Exception as exc:
            self.progress.emit(str(exc))
            self.done.emit(False)


class KatuUpdate(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Katu Update")
        self.setMinimumSize(640, 520)
        self.resize(720, 580)
        self.setWindowIcon(QIcon("/usr/share/icons/hicolor/256x256/apps/katu-logo.png"))
        self._apt_pkgs  = []
        self._flat_pkgs = []
        self._plan = {}
        self._busy = False
        self._build_ui()
        QTimer.singleShot(500, self._check)

    def _build_ui(self):
        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)
        lay = QVBoxLayout(root)
        lay.setContentsMargins(32, 32, 32, 32)
        lay.setSpacing(16)

        # Header
        h = QHBoxLayout()
        ico = QLabel("🔄")
        ico.setStyleSheet("font-size:32px;")
        info = QVBoxLayout()
        info.setSpacing(2)
        title = QLabel("Katu Update")
        title.setStyleSheet(f"font-size:20px; font-weight:bold; color:{ui.TEXT};")
        self._subtitle = QLabel("Verificando atualizações...")
        self._subtitle.setStyleSheet(f"color:{ui.MUTED};")
        info.addWidget(title)
        info.addWidget(self._subtitle)
        h.addWidget(ico)
        h.addLayout(info, 1)
        lay.addLayout(h)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"color:{ui.BORDER};")
        lay.addWidget(sep)

        # Status card
        self._status_card = QFrame()
        self._status_card.setObjectName("card")
        self._status_card.setStyleSheet(f"QFrame#card{{background:{ui.CARD};border:1px solid {ui.BORDER};border-radius:10px;padding:0 20px;}}")
        self._status_card.setFixedHeight(72)
        sc_lay = QHBoxLayout(self._status_card)
        self._status_icon = QLabel("⟳")
        self._status_icon.setStyleSheet(f"font-size:24px; color:{ui.MUTED};")
        self._status_text = QLabel("Verificando...")
        self._status_text.setStyleSheet(f"font-size:14px; color:{ui.TEXT};")
        sc_lay.addWidget(self._status_icon)
        sc_lay.addWidget(self._status_text, 1)
        lay.addWidget(self._status_card)

        # Update list
        self._list = QListWidget()
        self._list.setVisible(False)
        lay.addWidget(self._list, 1)

        # Log
        self._log = QPlainTextEdit()
        self._log.setReadOnly(True)
        self._log.setFixedHeight(120)
        self._log.setPlaceholderText("Log de operações...")
        self._log.setVisible(False)
        lay.addWidget(self._log)

        # Buttons
        btn_row = QHBoxLayout()
        self._check_btn = QPushButton("VERIFICAR")
        self._check_btn.setObjectName("primary")
        self._check_btn.setFixedHeight(44)
        self._check_btn.clicked.connect(self._check)

        self._update_btn = QPushButton("ATUALIZAR TUDO")
        self._update_btn.setObjectName("primary")
        self._update_btn.setFixedHeight(44)
        self._update_btn.setEnabled(False)
        self._update_btn.clicked.connect(self._update_all)

        self._history_btn = QPushButton("HISTÓRICO")
        self._history_btn.clicked.connect(self._show_history)
        self._apps_btn = QPushButton("APPS OFICIAIS")
        self._apps_btn.clicked.connect(self._offer_app)
        self._cancel_btn = QPushButton("CANCELAR DOWNLOAD")
        self._cancel_btn.setEnabled(False)
        self._cancel_btn.clicked.connect(self._cancel_download)
        btn_row.addWidget(self._history_btn)
        btn_row.addWidget(self._apps_btn)
        btn_row.addWidget(self._cancel_btn)
        btn_row.addWidget(self._check_btn)
        btn_row.addWidget(self._update_btn)
        lay.addLayout(btn_row)

        # Last check label
        self._last_check = QLabel("")
        self._last_check.setStyleSheet(f"color:{ui.MUTED}; font-size:12px;")
        self._last_check.setAlignment(Qt.AlignCenter)
        lay.addWidget(self._last_check)

    def _check(self, selected=None):
        if isinstance(selected, bool):
            selected = None
        self._busy = True
        self._check_btn.setEnabled(False)
        self._update_btn.setEnabled(False)
        self._list.setVisible(False)
        self._log.setVisible(True)
        self._log.clear()
        self._status_icon.setText("⟳")
        self._status_text.setText("Verificando atualizações...")
        t = CheckThread(selected)
        t.progress.connect(self._log_line)
        t.done.connect(self._on_check_done)
        t.failed.connect(self._on_check_failed)
        t.start()
        self._check_thread = t

    def _log_line(self, line):
        self._log.appendPlainText(line)
        self._log.verticalScrollBar().setValue(self._log.verticalScrollBar().maximum())

    def _on_check_done(self, plan, flat_pkgs):
        self._busy = False
        self._plan = plan
        apt_pkgs = plan["packages"]
        from datetime import datetime
        self._apt_pkgs  = apt_pkgs
        self._flat_pkgs = flat_pkgs
        total = len(apt_pkgs) + len(flat_pkgs)
        self._last_check.setText(f"Última verificação: {datetime.now().strftime('%d/%m/%Y %H:%M')} | Canal: {backend.channel()}")
        self._check_btn.setEnabled(True)
        self._log.setVisible(False)

        if total == 0:
            self._status_icon.setText("✓")
            self._status_icon.setStyleSheet(f"font-size:24px; color:{ui.SUCCESS};")
            self._status_text.setText("Seu sistema está atualizado.")
            self._subtitle.setText("Nenhuma atualização disponível")
            self._list.setVisible(False)
            self._update_btn.setEnabled(False)
        else:
            self._status_icon.setText("⚠")
            self._status_icon.setStyleSheet(f"font-size:24px; color:{ui.AMBER};")
            seg_count = sum(1 for p in apt_pkgs if p["category"] == "Segurança")
            self._status_text.setText(f"{total} atualizações disponíveis")
            self._subtitle.setText(
                f"APT: {len(apt_pkgs)} | Flatpak: {len(flat_pkgs)}"
                + (f" | Segurança: {seg_count}" if seg_count else "")
            )
            self._list.clear()
            self._list.setVisible(True)
            for package in apt_pkgs:
                self._list.addItem(f"{package['name']}  {package['installed'] or 'Novo'} → {package['version']}  ({package['origin']})\n{package['category']}: {package['notes']}")
            for package in flat_pkgs:
                self._list.addItem(f"{package['ref']}  {package['version']}  (Flatpak / {package['scope']})")
            self._subtitle.setText(self._subtitle.text() + f" | Download APT: {plan['download'] / 1048576:.1f} MB")
            self._update_btn.setEnabled(True)

    def _update_all(self):
        reply = QMessageBox.question(
            self, "Atualizar sistema",
            f"Instalar {len(self._apt_pkgs) + len(self._flat_pkgs)} atualizações?\n\nO sistema não será reiniciado automaticamente.",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        self._update_btn.setEnabled(False)
        self._check_btn.setEnabled(False)
        self._list.setVisible(False)
        self._log.setVisible(True)
        self._log.clear()
        self._status_text.setText("Instalando atualizações...")
        self._busy = True
        self._cancel_btn.setEnabled(bool(self._apt_pkgs))
        t = UpgradeThread(self._plan, self._flat_pkgs)
        t.progress.connect(self._log_line)
        t.done.connect(self._on_upgrade_done)
        t.start()
        self._upgrade_thread = t

    def _on_upgrade_done(self, ok):
        self._busy = False
        self._cancel_btn.setEnabled(False)
        self._check_btn.setEnabled(True)
        if ok:
            self._status_icon.setText("✓")
            self._status_icon.setStyleSheet(f"font-size:24px; color:{ui.SUCCESS};")
            self._status_text.setText("Atualizações instaladas e validadas.")
            if backend.read_state().get('reboot') or Path('/run/reboot-required').exists():
                reply = QMessageBox.question(self, 'Reinicialização necessária',
                    'É necessário reiniciar para concluir. Reiniciar agora?', QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.Yes:
                    subprocess.Popen(['systemctl', 'reboot'])
            if CORE:
                notifications.notify_success("Katu Update", "Sistema atualizado com sucesso.")
        else:
            self._status_text.setText("Algumas atualizações não puderam ser instaladas.")
            if CORE:
                notifications.notify_error("Katu Update", "Falha em algumas atualizações.")

    def _on_check_failed(self, message):
        self._busy = False
        self._check_btn.setEnabled(True)
        self._update_btn.setEnabled(False)
        self._status_icon.setText("⚠")
        self._status_text.setText("Não foi possível verificar as atualizações.")
        self._subtitle.setText("Verifique a conexão e a configuração do repositório.")
        self._log_line(message)

    def _show_history(self):
        entries = backend.history()
        lines = []
        for entry in reversed(entries):
            stamp = time.strftime('%d/%m/%Y %H:%M', time.localtime(entry.get('started', 0)))
            lines.append(stamp + (' — Concluído' if entry.get('ok') else ' — Falha/interrupção'))
            lines.extend(p['name'] + ' ' + p['version'] for p in entry.get('packages', []))
            if entry.get('error'):
                lines.append(entry['error'])
        current = backend.read_state()
        if current.get('phase') not in (None, 'complete', 'failed'):
            lines.insert(0, 'Última transação: ' + current['phase'] + '. Confira se o serviço está ativo antes de reparar.')
        dialog = QMessageBox(self)
        dialog.setWindowTitle('Histórico do Katu Update')
        dialog.setText('Operações APT registradas pelo sistema')
        dialog.setDetailedText('\n'.join(lines) or 'Nenhuma operação registrada.')
        dialog.exec()

    def _offer_app(self):
        if self._busy:
            return
        apps = self._plan.get('optional', [])
        if not apps:
            QMessageBox.information(self, 'Apps oficiais', 'Nenhum componente opcional novo disponível na última verificação.')
            return
        name, accepted = QInputDialog.getItem(self, 'Apps oficiais', 'Escolha um componente para revisar e instalar:', apps, 0, False)
        if accepted:
            self._check([name])

    def _cancel_download(self):
        if backend.read_state().get('phase') != 'downloading':
            self._log_line('Cancelamento disponível somente durante o download.')
            return
        try:
            backend.run(['pkexec', backend.HELPER, 'cancel'])
        except Exception as exc:
            self._log_line(str(exc))

    def closeEvent(self, event):
        if self._busy:
            QMessageBox.information(self, 'Operação em andamento', 'Aguarde a conclusão da operação.')
            event.ignore()
        else:
            event.accept()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Katu Update")
    if CORE:
        app.setStyleSheet(ui.STYLESHEET)
    win = KatuUpdate()
    win.show()
    sys.exit(app.exec_() if QT == 'PyQt5' else app.exec())


if __name__ == "__main__":
    main()
