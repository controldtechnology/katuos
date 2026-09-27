#!/usr/bin/env python3
"""
Katu Update — Gerenciador de Atualizações do Katu OS
Mantenha seu sistema atualizado sem usar o terminal.
"""
import sys, os, subprocess
from pathlib import Path

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
    from katu_core.packages import apt_update, apt_upgrade, apt_list_upgradable, flatpak_list_upgradable
    CORE = True
except ImportError:
    CORE = False
    class _FakeUI:
        STYLESHEET = ""; BG = "#0d1117"; SURFACE = "#161b22"; CARD = "#1c2128"
        BORDER = "#30363d"; ACCENT = "#00c853"; TEXT = "#e6edf3"; MUTED = "#8b949e"
        ERROR = "#f85149"; AMBER = "#ffab00"; SUCCESS = "#3fb950"; TEXT_INV = "#0d1117"
    ui = _FakeUI()
    def apt_update(cb=None): return False
    def apt_upgrade(cb=None): return False
    def apt_list_upgradable(): return []
    def flatpak_list_upgradable(): return []
    class notifications:
        @staticmethod
        def notify_success(a, b=""): pass
        @staticmethod
        def notify_error(a, b=""): pass


class CheckThread(QThread):
    progress  = pyqtSignal(str)
    done      = pyqtSignal(list, list)  # apt_updates, flatpak_updates

    def run(self):
        self.progress.emit("Atualizando lista de pacotes...")
        apt_update(lambda l: self.progress.emit(l[:80]))
        self.progress.emit("Verificando atualizações APT...")
        apt_pkgs = apt_list_upgradable()
        self.progress.emit("Verificando atualizações Flatpak...")
        flat_pkgs = flatpak_list_upgradable()
        self.done.emit(apt_pkgs, flat_pkgs)


class UpgradeThread(QThread):
    progress = pyqtSignal(str)
    done     = pyqtSignal(bool)

    def __init__(self, upgrade_flatpak=False):
        super().__init__()
        self._flat = upgrade_flatpak

    def run(self):
        ok = True
        self.progress.emit("Instalando atualizações APT...")
        if not apt_upgrade(lambda l: self.progress.emit(l[:80])):
            ok = False
        if self._flat:
            self.progress.emit("Atualizando Flatpak...")
            try:
                p = subprocess.Popen(
                    ["flatpak", "update", "--noninteractive"],
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
                )
                for line in p.stdout:
                    self.progress.emit(line.rstrip()[:80])
                p.wait()
            except Exception:
                pass
        self.done.emit(ok)


class KatuUpdate(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Katu Update")
        self.setMinimumSize(640, 520)
        self.resize(720, 580)
        self.setWindowIcon(QIcon("/usr/share/icons/hicolor/256x256/apps/katu-logo.png"))
        self._apt_pkgs  = []
        self._flat_pkgs = []
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

        btn_row.addWidget(self._check_btn)
        btn_row.addWidget(self._update_btn)
        lay.addLayout(btn_row)

        # Last check label
        self._last_check = QLabel("")
        self._last_check.setStyleSheet(f"color:{ui.MUTED}; font-size:12px;")
        self._last_check.setAlignment(Qt.AlignCenter)
        lay.addWidget(self._last_check)

    def _check(self):
        self._check_btn.setEnabled(False)
        self._update_btn.setEnabled(False)
        self._list.setVisible(False)
        self._log.setVisible(True)
        self._log.clear()
        self._status_icon.setText("⟳")
        self._status_text.setText("Verificando atualizações...")
        t = CheckThread()
        t.progress.connect(self._log_line)
        t.done.connect(self._on_check_done)
        t.start()
        self._check_thread = t

    def _log_line(self, line):
        self._log.appendPlainText(line)
        self._log.verticalScrollBar().setValue(self._log.verticalScrollBar().maximum())

    def _on_check_done(self, apt_pkgs, flat_pkgs):
        from datetime import datetime
        self._apt_pkgs  = apt_pkgs
        self._flat_pkgs = flat_pkgs
        total = len(apt_pkgs) + len(flat_pkgs)
        self._last_check.setText(f"Última verificação: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
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
            seg_count = sum(1 for p, v, s in apt_pkgs if "security" in s.lower())
            self._status_text.setText(f"{total} atualizações disponíveis")
            self._subtitle.setText(
                f"APT: {len(apt_pkgs)} | Flatpak: {len(flat_pkgs)}"
                + (f" | Segurança: {seg_count}" if seg_count else "")
            )
            self._list.clear()
            self._list.setVisible(True)
            for name, ver, src in apt_pkgs:
                icon = "🔒" if "security" in src.lower() else "📦"
                self._list.addItem(f"{icon} {name}  {ver}  (APT)")
            for name, ver, src in flat_pkgs:
                self._list.addItem(f"🔷 {name}  {ver}  (Flatpak)")
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
        t = UpgradeThread(upgrade_flatpak=bool(self._flat_pkgs))
        t.progress.connect(self._log_line)
        t.done.connect(self._on_upgrade_done)
        t.start()
        self._upgrade_thread = t

    def _on_upgrade_done(self, ok):
        self._check_btn.setEnabled(True)
        if ok:
            self._status_icon.setText("✓")
            self._status_icon.setStyleSheet(f"font-size:24px; color:{ui.SUCCESS};")
            self._status_text.setText("Atualizações instaladas com sucesso!")
            if CORE:
                notifications.notify_success("Katu Update", "Sistema atualizado com sucesso.")
        else:
            self._status_text.setText("Algumas atualizações não puderam ser instaladas.")
            if CORE:
                notifications.notify_error("Katu Update", "Falha em algumas atualizações.")


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
