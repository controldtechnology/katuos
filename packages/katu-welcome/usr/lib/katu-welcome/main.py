#!/usr/bin/env python3
"""
Katu OS Welcome — Onboarding para novos usuários
Executado automaticamente no primeiro login.
"""
import sys, os, subprocess
from pathlib import Path

try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
    from PyQt5.QtGui import *
    QT = 'PyQt5'
except ImportError:
    from PySide6.QtWidgets import *
    from PySide6.QtCore import Qt, QThread, Signal as pyqtSignal, QTimer, QSize
    from PySide6.QtGui import *
    QT = 'PySide6'

sys.path.insert(0, '/usr/lib/python3/dist-packages')
try:
    from katu_core import ui, system
    from katu_core.config import KatuConfig, is_first_boot, mark_first_boot_done, is_live_session
    CORE = True
except ImportError:
    CORE = False
    class _FakeUI:
        STYLESHEET = ""; BG = "#0d1117"; SURFACE = "#161b22"; CARD = "#1c2128"
        BORDER = "#30363d"; ACCENT = "#00c853"; ACCENT_H = "#00e676"; TEXT = "#e6edf3"
        MUTED = "#8b949e"; ERROR = "#f85149"; AMBER = "#ffab00"; SUCCESS = "#3fb950"
        TEXT_INV = "#0d1117"
    ui = _FakeUI()
    def is_first_boot(a): return True
    def mark_first_boot_done(a): pass
    def is_live_session(): return False
    class system:
        @staticmethod
        def get_katu_version(): return "1.0"
        @staticmethod
        def get_network_status(): return {"connected": False}
        @staticmethod
        def get_pending_updates(): return -1

FLAG_FILE = Path.home() / ".config" / "katu" / "welcome" / ".first-boot-done"
LIVE_FLAG = Path("/run/live/active")


def is_live():
    return LIVE_FLAG.exists() or (CORE and is_live_session())


def check_first_boot():
    return not FLAG_FILE.exists()


def mark_done():
    FLAG_FILE.parent.mkdir(parents=True, exist_ok=True)
    FLAG_FILE.touch()


# ── Passo base ────────────────────────────────────────────────────────────────
class Step(QWidget):
    next_requested = pyqtSignal()
    back_requested = pyqtSignal()

    def __init__(self, title, icon, parent=None):
        super().__init__(parent)
        self._title = title
        self._icon  = icon

    def build(self, content_widget):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(40, 20, 40, 20)
        lay.setSpacing(16)
        h = QHBoxLayout()
        ico = QLabel(self._icon)
        ico.setStyleSheet("font-size:40px;")
        h.addWidget(ico)
        lbl = QLabel(self._title)
        lbl.setStyleSheet(f"font-size:22px; font-weight:bold; color:{ui.TEXT};")
        h.addWidget(lbl, 1)
        lay.addLayout(h)
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"color:{ui.BORDER};")
        lay.addWidget(sep)
        lay.addWidget(content_widget, 1)
        return lay


# ── Passo 1: Boas-vindas ──────────────────────────────────────────────────────
class WelcomeStep(Step):
    def __init__(self, parent=None):
        super().__init__("Bem-vindo ao Katu OS!", "🐆", parent)
        content = QWidget()
        lay = QVBoxLayout(content)
        lay.setAlignment(Qt.AlignCenter)
        lay.setSpacing(12)
        ver = system.get_katu_version() if CORE else "1.0"
        t = QLabel(f"Katu OS {ver}")
        t.setAlignment(Qt.AlignCenter)
        t.setStyleSheet(f"font-size:28px; font-weight:bold; color:{ui.ACCENT};")
        sub = QLabel("Livre. Brasileiro. Para todos.")
        sub.setAlignment(Qt.AlignCenter)
        sub.setStyleSheet(f"font-size:16px; color:{ui.TEXT};")
        desc = QLabel(
            "Este assistente vai guiar você pelas configurações iniciais.\n"
            "Você pode pular qualquer etapa e configurar depois."
        )
        desc.setAlignment(Qt.AlignCenter)
        desc.setWordWrap(True)
        desc.setStyleSheet(f"color:{ui.MUTED}; font-size:13px;")
        lay.addWidget(t)
        lay.addWidget(sub)
        lay.addSpacing(8)
        lay.addWidget(desc)
        self.build(content)


# ── Passo 2: Internet ─────────────────────────────────────────────────────────
class InternetStep(Step):
    def __init__(self, parent=None):
        super().__init__("Conectar à Internet", "🌐", parent)
        content = QWidget()
        lay = QVBoxLayout(content)
        lay.setSpacing(12)
        self._status_lbl = QLabel("Verificando conexão...")
        self._status_lbl.setStyleSheet(f"font-size:14px; color:{ui.MUTED};")
        lay.addWidget(self._status_lbl)
        btn = QPushButton("Abrir configurações de rede")
        btn.setObjectName("primary")
        btn.setFixedHeight(40)
        btn.clicked.connect(lambda: subprocess.Popen(["plasma-nm"]))
        lay.addWidget(btn)
        lay.addStretch()
        self.build(content)
        QTimer.singleShot(500, self._check_net)

    def _check_net(self):
        if CORE:
            try:
                net = system.get_network_status()
                if net.get("connected"):
                    kind = "Wi-Fi" if net.get("wifi") else "Ethernet"
                    self._status_lbl.setText(f"✓ Conectado via {kind}")
                    self._status_lbl.setStyleSheet(f"font-size:14px; color:{ui.SUCCESS};")
                else:
                    self._status_lbl.setText("✗ Sem conexão com a internet")
                    self._status_lbl.setStyleSheet(f"font-size:14px; color:{ui.MUTED};")
            except Exception:
                pass


# ── Passo 3: Atualizações ─────────────────────────────────────────────────────
class UpdatesStep(Step):
    def __init__(self, parent=None):
        super().__init__("Atualizações do Sistema", "🔄", parent)
        content = QWidget()
        lay = QVBoxLayout(content)
        lay.setSpacing(12)
        desc = QLabel("Mantenha o Katu OS atualizado para ter as últimas correções de segurança.")
        desc.setWordWrap(True)
        desc.setStyleSheet(f"color:{ui.TEXT};")
        lay.addWidget(desc)
        btn = QPushButton("Abrir Katu Update")
        btn.setObjectName("primary")
        btn.setFixedHeight(40)
        btn.clicked.connect(lambda: subprocess.Popen(["katu-update"]))
        skip = QPushButton("Atualizar depois")
        skip.setFixedHeight(36)
        skip.clicked.connect(self.next_requested.emit)
        lay.addWidget(btn)
        lay.addWidget(skip)
        lay.addStretch()
        self.build(content)


# ── Passo 4: Drivers ──────────────────────────────────────────────────────────
class DriversStep(Step):
    def __init__(self, parent=None):
        super().__init__("Drivers de Hardware", "🖥️", parent)
        content = QWidget()
        lay = QVBoxLayout(content)
        lay.setSpacing(12)
        desc = QLabel("O Katu Drivers verifica se seu hardware está corretamente configurado.")
        desc.setWordWrap(True)
        desc.setStyleSheet(f"color:{ui.TEXT};")
        lay.addWidget(desc)
        btn = QPushButton("Verificar drivers")
        btn.setObjectName("primary")
        btn.setFixedHeight(40)
        btn.clicked.connect(lambda: subprocess.Popen(["katu-drivers"]))
        skip = QPushButton("Verificar depois")
        skip.setFixedHeight(36)
        skip.clicked.connect(self.next_requested.emit)
        lay.addWidget(btn)
        lay.addWidget(skip)
        lay.addStretch()
        self.build(content)


# ── Passo 5: Aparência ────────────────────────────────────────────────────────
class AppearanceStep(Step):
    def __init__(self, parent=None):
        super().__init__("Personalizar Aparência", "🎨", parent)
        content = QWidget()
        lay = QVBoxLayout(content)
        lay.setSpacing(12)
        desc = QLabel("Personalize o Katu OS do jeito que você gosta.")
        desc.setStyleSheet(f"color:{ui.TEXT};")
        lay.addWidget(desc)
        items = [
            ("Configurações de aparência", "systemsettings5 --args kcm_lookandfeel"),
            ("Papel de parede",            "systemsettings5 --args kcm_desktoptheme"),
        ]
        for label, cmd in items:
            btn = QPushButton(label)
            btn.setFixedHeight(38)
            btn.clicked.connect(lambda _, c=cmd: subprocess.Popen(c.split()))
            lay.addWidget(btn)
        lay.addStretch()
        self.build(content)


# ── Passo 6: IA ───────────────────────────────────────────────────────────────
class AIStep(Step):
    def __init__(self, parent=None):
        super().__init__("Inteligência Artificial", "🤖", parent)
        content = QWidget()
        lay = QVBoxLayout(content)
        lay.setSpacing(12)
        desc = QLabel(
            "O Katu AI é seu assistente pessoal. Converse, faça perguntas,\n"
            "peça ajuda — tudo em português."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet(f"color:{ui.TEXT};")
        lay.addWidget(desc)
        note = QLabel(
            "Para usar IA em nuvem, você precisará de uma chave de API própria.\n"
            "Também é possível usar IA localmente, sem internet."
        )
        note.setWordWrap(True)
        note.setStyleSheet(f"color:{ui.MUTED}; font-size:12px;")
        lay.addWidget(note)
        btn = QPushButton("Abrir Katu AI")
        btn.setObjectName("primary")
        btn.setFixedHeight(40)
        btn.clicked.connect(lambda: subprocess.Popen(["katu-ai"]))
        skip = QPushButton("Configurar depois")
        skip.setFixedHeight(36)
        skip.clicked.connect(self.next_requested.emit)
        lay.addWidget(btn)
        lay.addWidget(skip)
        lay.addStretch()
        self.build(content)


# ── Passo 7: Aplicativos ──────────────────────────────────────────────────────
class AppsStep(Step):
    def __init__(self, parent=None):
        super().__init__("Instalar Aplicativos", "📦", parent)
        content = QWidget()
        lay = QVBoxLayout(content)
        lay.setSpacing(12)
        desc = QLabel("Encontre e instale aplicativos na Katu Store — sem precisar de terminal.")
        desc.setWordWrap(True)
        desc.setStyleSheet(f"color:{ui.TEXT};")
        lay.addWidget(desc)
        btn = QPushButton("Abrir Katu Store")
        btn.setObjectName("primary")
        btn.setFixedHeight(40)
        btn.clicked.connect(lambda: subprocess.Popen(["katu-store"]))
        skip = QPushButton("Instalar depois")
        skip.setFixedHeight(36)
        skip.clicked.connect(self.next_requested.emit)
        lay.addWidget(btn)
        lay.addWidget(skip)
        lay.addStretch()
        self.build(content)


# ── Passo 8: Backup ───────────────────────────────────────────────────────────
class BackupStep(Step):
    def __init__(self, parent=None):
        super().__init__("Backup dos seus Arquivos", "☁️", parent)
        content = QWidget()
        lay = QVBoxLayout(content)
        lay.setSpacing(12)
        desc = QLabel("Proteja seus arquivos com o Katu Backup.")
        desc.setStyleSheet(f"color:{ui.TEXT};")
        lay.addWidget(desc)
        btn = QPushButton("Configurar Backup")
        btn.setObjectName("primary")
        btn.setFixedHeight(40)
        btn.clicked.connect(lambda: subprocess.Popen(["katu-backup"]))
        skip = QPushButton("Configurar depois")
        skip.setFixedHeight(36)
        skip.clicked.connect(self.next_requested.emit)
        lay.addWidget(btn)
        lay.addWidget(skip)
        lay.addStretch()
        self.build(content)


# ── Passo 9: Pronto ───────────────────────────────────────────────────────────
class ReadyStep(Step):
    def __init__(self, parent=None):
        super().__init__("Tudo pronto!", "✅", parent)
        content = QWidget()
        lay = QVBoxLayout(content)
        lay.setAlignment(Qt.AlignCenter)
        lay.setSpacing(12)
        t = QLabel("O Katu OS está configurado e pronto para usar.")
        t.setAlignment(Qt.AlignCenter)
        t.setWordWrap(True)
        t.setStyleSheet(f"font-size:15px; color:{ui.TEXT};")
        links = [
            ("🐆 Katu Central",    "katu-central"),
            ("🤖 Katu AI",         "katu-ai"),
            ("📦 Katu Store",      "katu-store"),
        ]
        lay.addWidget(t)
        for label, cmd in links:
            btn = QPushButton(label)
            btn.setFixedHeight(38)
            btn.clicked.connect(lambda _, c=cmd: subprocess.Popen([c]))
            lay.addWidget(btn)
        lay.addStretch()
        self.build(content)


# ── Live Mode Page ────────────────────────────────────────────────────────────
class LiveModeWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Katu OS — Modo Live")
        self.setMinimumSize(560, 380)
        self.resize(620, 420)
        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)
        lay = QVBoxLayout(root)
        lay.setContentsMargins(40, 40, 40, 40)
        lay.setAlignment(Qt.AlignCenter)
        lay.setSpacing(16)
        ico = QLabel("🐆")
        ico.setAlignment(Qt.AlignCenter)
        ico.setStyleSheet("font-size:48px;")
        title = QLabel("Você está experimentando o Katu OS")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"font-size:20px; font-weight:bold; color:{ui.TEXT};")
        sub = QLabel(
            "Este é o modo Live. Nada será salvo nesta sessão.\n"
            "Se gostar, instale o Katu OS no seu computador!"
        )
        sub.setAlignment(Qt.AlignCenter)
        sub.setWordWrap(True)
        sub.setStyleSheet(f"color:{ui.MUTED};")
        btn = QPushButton("INSTALAR KATU OS")
        btn.setObjectName("primary")
        btn.setFixedHeight(48)
        btn.setMinimumWidth(200)
        btn.clicked.connect(lambda: subprocess.Popen(["calamares"]))
        close_btn = QPushButton("Continuar experimentando")
        close_btn.setFixedHeight(36)
        close_btn.clicked.connect(self.close)
        lay.addWidget(ico)
        lay.addWidget(title)
        lay.addWidget(sub)
        lay.addSpacing(12)
        lay.addWidget(btn, alignment=Qt.AlignCenter)
        lay.addWidget(close_btn, alignment=Qt.AlignCenter)


# ── Main Welcome Window ───────────────────────────────────────────────────────
class KatuWelcome(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bem-vindo ao Katu OS")
        self.setMinimumSize(640, 520)
        self.resize(720, 580)
        self.setWindowIcon(QIcon("/usr/share/icons/hicolor/256x256/apps/katu-welcome.png"))
        self._step = 0
        self._steps = [
            WelcomeStep,
            InternetStep,
            UpdatesStep,
            DriversStep,
            AppearanceStep,
            AIStep,
            AppsStep,
            BackupStep,
            ReadyStep,
        ]
        self._build_ui()
        self._show_step(0)

    def _build_ui(self):
        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)
        lay = QVBoxLayout(root)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # Progress dots
        prog = QWidget()
        prog.setFixedHeight(48)
        prog.setStyleSheet(f"background:{ui.SURFACE}; border-bottom:1px solid {ui.BORDER};")
        prog_lay = QHBoxLayout(prog)
        prog_lay.setAlignment(Qt.AlignCenter)
        prog_lay.setSpacing(8)
        self._dots = []
        for i in range(len(self._steps)):
            dot = QLabel("●")
            dot.setFixedSize(16, 16)
            dot.setAlignment(Qt.AlignCenter)
            dot.setStyleSheet(f"color:{ui.BORDER};")
            self._dots.append(dot)
            prog_lay.addWidget(dot)
        lay.addWidget(prog)

        # Step stack
        self._stack = QStackedWidget()
        lay.addWidget(self._stack, 1)

        # Build all steps
        for StepClass in self._steps:
            step = StepClass()
            step.next_requested.connect(self._next)
            step.back_requested.connect(self._back)
            self._stack.addWidget(step)

        # Navigation bar
        nav = QWidget()
        nav.setFixedHeight(60)
        nav.setStyleSheet(f"background:{ui.SURFACE}; border-top:1px solid {ui.BORDER};")
        nav_lay = QHBoxLayout(nav)
        nav_lay.setContentsMargins(24, 8, 24, 8)
        nav_lay.setSpacing(12)

        self._back_btn = QPushButton("← Anterior")
        self._back_btn.setFixedHeight(40)
        self._back_btn.setEnabled(False)
        self._back_btn.clicked.connect(self._back)

        self._no_show = QCheckBox("Não mostrar novamente")
        self._no_show.setStyleSheet(f"color:{ui.MUTED}; font-size:12px;")

        self._next_btn = QPushButton("Próximo →")
        self._next_btn.setObjectName("primary")
        self._next_btn.setFixedHeight(40)
        self._next_btn.clicked.connect(self._next)

        nav_lay.addWidget(self._back_btn)
        nav_lay.addWidget(self._no_show, 1)
        nav_lay.addWidget(self._next_btn)
        lay.addWidget(nav)

    def _show_step(self, idx):
        self._step = idx
        self._stack.setCurrentIndex(idx)
        self._back_btn.setEnabled(idx > 0)
        is_last = idx == len(self._steps) - 1
        self._next_btn.setText("Concluir" if is_last else "Próximo →")
        for i, dot in enumerate(self._dots):
            if i < idx:
                dot.setStyleSheet(f"color:{ui.SUCCESS};")
            elif i == idx:
                dot.setStyleSheet(f"color:{ui.ACCENT}; font-size:14px;")
            else:
                dot.setStyleSheet(f"color:{ui.BORDER};")

    def _next(self):
        if self._step < len(self._steps) - 1:
            self._show_step(self._step + 1)
        else:
            self._finish()

    def _back(self):
        if self._step > 0:
            self._show_step(self._step - 1)

    def _finish(self):
        if self._no_show.isChecked():
            mark_done()
        self.close()


def main():
    # Check if running in Live mode
    if is_live():
        app = QApplication(sys.argv)
        app.setApplicationName("Katu OS Live")
        if CORE:
            app.setStyleSheet(ui.STYLESHEET)
        win = LiveModeWidget()
        win.show()
        sys.exit(app.exec_() if QT == 'PyQt5' else app.exec())
        return

    # Normal first-boot
    app = QApplication(sys.argv)
    app.setApplicationName("Katu Welcome")
    if CORE:
        app.setStyleSheet(ui.STYLESHEET)
    win = KatuWelcome()
    win.show()
    sys.exit(app.exec_() if QT == 'PyQt5' else app.exec())


if __name__ == "__main__":
    main()
