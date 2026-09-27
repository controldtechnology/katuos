#!/usr/bin/env python3
"""
Katu Central — Painel de Controle do Katu OS
Ponto central de gerenciamento para usuários.
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
    from katu_core import system, ui, notifications
    from katu_core.config import KatuConfig
    CORE = True
except ImportError:
    CORE = False
    class _FakeUI:
        STYLESHEET = ""
        BG = "#0d1117"; SURFACE = "#161b22"; CARD = "#1c2128"
        BORDER = "#30363d"; ACCENT = "#00c853"; ACCENT_H = "#00e676"
        TEXT = "#e6edf3"; MUTED = "#8b949e"; ERROR = "#f85149"
        AMBER = "#ffab00"; SUCCESS = "#3fb950"
    ui = _FakeUI()

# ── Dados do Sistema em Background ───────────────────────────────────────────
class SystemDataThread(QThread):
    done = pyqtSignal(dict)
    def run(self):
        data = {}
        if CORE:
            try:
                data['os']  = system.get_os_info()
                data['cpu'] = system.get_cpu_info()
                data['mem'] = system.get_memory_info()
                data['disk'] = system.get_disk_info()
                data['net'] = system.get_network_status()
                data['bt']  = system.get_bluetooth_status()
                data['upd'] = system.get_pending_updates()
                data['uptime'] = system.get_uptime()
            except Exception:
                pass
        self.done.emit(data)


# ── Card de Status ────────────────────────────────────────────────────────────
class StatusCard(QFrame):
    clicked = pyqtSignal(str)

    def __init__(self, icon, title, subtitle, status, action_id="", parent=None):
        super().__init__(parent)
        self.action_id = action_id
        self.setObjectName("statusCard")
        self.setCursor(Qt.PointingHandCursor if action_id else Qt.ArrowCursor)
        self.setFixedHeight(90)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(12)

        ico = QLabel(icon)
        ico.setFixedSize(36, 36)
        ico.setAlignment(Qt.AlignCenter)
        ico.setStyleSheet(f"font-size:22px; background:{ui.CARD}; border-radius:8px;")

        info = QVBoxLayout()
        info.setSpacing(2)
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet(f"font-weight:bold; color:{ui.TEXT}; font-size:13px;")
        lbl_sub = QLabel(subtitle)
        lbl_sub.setStyleSheet(f"color:{ui.MUTED}; font-size:12px;")
        info.addWidget(lbl_title)
        info.addWidget(lbl_sub)

        self._status_lbl = QLabel(status)
        self._status_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self._status_lbl.setStyleSheet(f"font-size:12px; color:{ui.MUTED};")

        lay.addWidget(ico)
        lay.addLayout(info, 1)
        lay.addWidget(self._status_lbl)
        self._apply_style()

    def _apply_style(self):
        self.setStyleSheet(f"""
            QFrame#statusCard {{
                background:{ui.CARD}; border:1px solid {ui.BORDER};
                border-radius:10px;
            }}
            QFrame#statusCard:hover {{
                border-color:{ui.BORDER_H if hasattr(ui,'BORDER_H') else '#484f58'};
            }}
        """)

    def update_subtitle(self, text):
        for child in self.findChildren(QLabel):
            if child.styleSheet() and "MUTED" not in child.styleSheet() and "12px" in child.styleSheet():
                child.setText(text)
                return

    def update_status(self, text, color=None):
        self._status_lbl.setText(text)
        if color:
            self._status_lbl.setStyleSheet(f"font-size:12px; color:{color};")

    def mousePressEvent(self, e):
        if self.action_id:
            self.clicked.emit(self.action_id)
        super().mousePressEvent(e)


# ── Sidebar Item ──────────────────────────────────────────────────────────────
class SidebarItem(QFrame):
    clicked = pyqtSignal(str)
    def __init__(self, icon, label, page_id, parent=None):
        super().__init__(parent)
        self.page_id = page_id
        self.setObjectName("sidebarItem")
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(44)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 0, 16, 0)
        lay.setSpacing(10)
        self.ico_lbl = QLabel(icon)
        self.ico_lbl.setFixedWidth(20)
        self.ico_lbl.setAlignment(Qt.AlignCenter)
        self.ico_lbl.setStyleSheet("font-size:16px;")
        self.txt_lbl = QLabel(label)
        self.txt_lbl.setStyleSheet(f"font-size:13px; color:{ui.MUTED};")
        lay.addWidget(self.ico_lbl)
        lay.addWidget(self.txt_lbl, 1)
        self.setSelected(False)

    def setSelected(self, sel):
        self._sel = sel
        if sel:
            self.setStyleSheet(f"""
                QFrame#sidebarItem {{
                    background:{ui.SURFACE}; border-radius:8px;
                    border-left:3px solid {ui.ACCENT};
                }}
            """)
            self.txt_lbl.setStyleSheet(f"font-size:13px; color:{ui.TEXT}; font-weight:bold;")
        else:
            self.setStyleSheet("QFrame#sidebarItem { border-radius:8px; }")
            self.txt_lbl.setStyleSheet(f"font-size:13px; color:{ui.MUTED};")

    def mousePressEvent(self, e):
        self.clicked.emit(self.page_id)
        super().mousePressEvent(e)


# ── Página Home ───────────────────────────────────────────────────────────────
class HomePage(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.NoFrame)
        root = QWidget()
        self.setWidget(root)
        self._lay = QVBoxLayout(root)
        self._lay.setContentsMargins(32, 32, 32, 32)
        self._lay.setSpacing(20)
        self._build_static()
        self._cards = {}
        self._build_cards()
        self._lay.addStretch()

    def _build_static(self):
        h = QHBoxLayout()
        logo = QLabel("🐆")
        logo.setStyleSheet("font-size:36px;")
        info = QVBoxLayout()
        info.setSpacing(2)
        v_lbl = QLabel("Katu OS")
        v_lbl.setStyleSheet(f"font-size:22px; font-weight:bold; color:{ui.TEXT};")
        sub = QLabel("Carregando informações do sistema...")
        sub.setObjectName("ver_sub")
        sub.setStyleSheet(f"font-size:13px; color:{ui.MUTED};")
        info.addWidget(v_lbl)
        info.addWidget(sub)
        h.addWidget(logo)
        h.addLayout(info, 1)
        self._lay.addLayout(h)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"color:{ui.BORDER};")
        self._lay.addWidget(sep)

    def _build_cards(self):
        grid = QGridLayout()
        grid.setSpacing(12)
        items = [
            ("upd",  "🔄", "Atualizações",    "Verificando...", "check_updates"),
            ("drv",  "🖥️",  "Drivers",         "Verificando...", "katu-drivers"),
            ("sec",  "🔒", "Segurança",        "Verificando...", "katu-central"),
            ("stor", "💾", "Armazenamento",    "Verificando...", "run_diagnostic"),
            ("bkp",  "☁️",  "Backup",           "Verificando...", "open_backup"),
            ("ai",   "🤖", "Inteligência Artificial", "Pronto", "katu-ai"),
            ("hw",   "⚙️",  "Hardware",         "Verificando...", "run_diagnostic"),
            ("net",  "🌐", "Rede",             "Verificando...", "open_wifi"),
        ]
        for i, (key, icon, title, sub, action) in enumerate(items):
            card = StatusCard(icon, title, sub, "—", action)
            card.clicked.connect(self._on_card_click)
            self._cards[key] = card
            grid.addWidget(card, i // 2, i % 2)
        self._lay.addLayout(grid)

        btn = QPushButton("VERIFICAR SISTEMA")
        btn.setObjectName("primary")
        btn.setFixedHeight(44)
        btn.clicked.connect(self._verify)
        self._lay.addWidget(btn)

    def _on_card_click(self, action_id):
        if action_id.startswith("katu-"):
            try:
                subprocess.Popen([action_id])
            except Exception:
                pass
        elif CORE:
            from katu_core.actions import execute_action
            execute_action(action_id)

    def _verify(self):
        self._update_data({})
        t = SystemDataThread()
        t.done.connect(self._update_data)
        t.start()
        self._thread = t

    def update_system_data(self, data):
        self._update_data(data)
        sub = self.findChild(QLabel, "ver_sub")
        if sub and data.get("os"):
            os_info = data["os"]
            uptime = data.get("uptime", "")
            sub.setText(f"Versão {os_info.get('version','?')} · Kernel {os_info.get('kernel','?')} · Ativo há {uptime}")

    def _update_data(self, data):
        # Atualizações
        upd = data.get("upd", -1)
        c = self._cards.get("upd")
        if c:
            if upd == 0:
                c.update_status("✓ Atualizado", ui.SUCCESS)
                c._status_lbl.setText("✓ Atualizado")
            elif upd > 0:
                c.update_status(f"⚠ {upd} disponíveis", ui.AMBER)
                c._status_lbl.setText(f"⚠ {upd} disponíveis")
            else:
                c._status_lbl.setText("—")

        # Rede
        net = data.get("net", {})
        c = self._cards.get("net")
        if c and net:
            if net.get("connected"):
                kind = "Wi-Fi" if net.get("wifi") else "Ethernet"
                c._status_lbl.setText(f"✓ {kind}")
                c._status_lbl.setStyleSheet(f"font-size:12px; color:{ui.SUCCESS};")
            else:
                c._status_lbl.setText("✗ Desconectado")
                c._status_lbl.setStyleSheet(f"font-size:12px; color:{ui.ERROR};")

        # Armazenamento
        disks = data.get("disk", [])
        c = self._cards.get("stor")
        if c and disks:
            root_disk = next((d for d in disks if d["mount"] == "/"), None)
            if root_disk:
                c._status_lbl.setText(f"{root_disk['avail']} livres")

        # Hardware
        mem = data.get("mem", {})
        c = self._cards.get("hw")
        if c and mem:
            c._status_lbl.setText(f"RAM {mem.get('percent',0)}%")


# ── Placeholder Pages ─────────────────────────────────────────────────────────
class AppLaunchPage(QWidget):
    def __init__(self, icon, title, desc, cmd, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignCenter)
        lay.setSpacing(16)
        ico = QLabel(icon)
        ico.setAlignment(Qt.AlignCenter)
        ico.setStyleSheet("font-size:56px;")
        lbl = QLabel(title)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet(f"font-size:20px; font-weight:bold; color:{ui.TEXT};")
        sub = QLabel(desc)
        sub.setAlignment(Qt.AlignCenter)
        sub.setWordWrap(True)
        sub.setStyleSheet(f"color:{ui.MUTED}; font-size:13px; max-width:400px;")
        btn = QPushButton(f"Abrir {title}")
        btn.setObjectName("primary")
        btn.setFixedSize(220, 44)
        btn.clicked.connect(lambda: subprocess.Popen([cmd]) if cmd else None)
        lay.addWidget(ico)
        lay.addWidget(lbl)
        lay.addWidget(sub)
        lay.addWidget(btn, alignment=Qt.AlignCenter)


# ── Main Window ───────────────────────────────────────────────────────────────
class KatuCentral(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Katu Central")
        self.setMinimumSize(900, 620)
        self.resize(1100, 700)
        self.setWindowIcon(self._make_icon())

        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)
        hlay = QHBoxLayout(root)
        hlay.setContentsMargins(0, 0, 0, 0)
        hlay.setSpacing(0)

        # Sidebar
        self._sidebar = self._build_sidebar()
        hlay.addWidget(self._sidebar)

        # Content stack
        self._stack = QStackedWidget()
        self._stack.setObjectName("content")
        hlay.addWidget(self._stack, 1)

        self._pages = {}
        self._items = {}
        self._build_pages()
        self._select_page("home")

        # Load data
        t = SystemDataThread()
        t.done.connect(self._on_data)
        t.start()
        self._thread = t

    def _make_icon(self):
        icon_path = "/usr/share/icons/hicolor/256x256/apps/katu-logo.png"
        if os.path.exists(icon_path):
            return QIcon(icon_path)
        return QIcon()

    def _build_sidebar(self):
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet(f"QWidget#sidebar {{ background:{ui.SURFACE}; border-right:1px solid {ui.BORDER}; }}")
        lay = QVBoxLayout(sidebar)
        lay.setContentsMargins(12, 20, 12, 20)
        lay.setSpacing(4)

        logo_row = QHBoxLayout()
        logo_lbl = QLabel("🐆")
        logo_lbl.setStyleSheet("font-size:24px;")
        logo_text = QLabel("Katu Central")
        logo_text.setStyleSheet(f"font-size:15px; font-weight:bold; color:{ui.TEXT};")
        logo_row.addWidget(logo_lbl)
        logo_row.addWidget(logo_text, 1)
        lay.addLayout(logo_row)
        lay.addSpacing(12)

        nav_items = [
            ("🏠", "Início",               "home"),
            ("🔄", "Atualizações",          "updates"),
            ("🖥️",  "Drivers",              "drivers"),
            ("📦", "Aplicativos",           "store"),
            ("🤖", "Inteligência Artificial","ai"),
            ("🔒", "Segurança",             "security"),
            ("☁️",  "Backup",               "backup"),
            ("📱", "Dispositivos",          "connect"),
            ("⚙️",  "Sistema",              "system"),
            ("🔍", "Diagnóstico",           "diagnostic"),
            ("❓", "Ajuda",                "help"),
        ]
        for icon, label, page_id in nav_items:
            item = SidebarItem(icon, label, page_id)
            item.clicked.connect(self._select_page)
            lay.addWidget(item)
            self._items[page_id] = item

        lay.addStretch()
        ver_lbl = QLabel("Katu OS 1.0")
        ver_lbl.setStyleSheet(f"font-size:11px; color:{ui.MUTED}; padding-left:8px;")
        lay.addWidget(ver_lbl)
        return sidebar

    def _build_pages(self):
        # Home
        home = HomePage()
        self._pages["home"] = home
        self._stack.addWidget(home)

        # Launch pages for other sections
        external = {
            "updates":    ("🔄", "Katu Update",      "Gerencie atualizações do sistema",                   "katu-update"),
            "drivers":    ("🖥️",  "Katu Drivers",     "Detecte e instale drivers de hardware",               "katu-drivers"),
            "store":      ("📦", "Katu Store",        "Encontre e instale aplicativos",                      "katu-store"),
            "ai":         ("🤖", "Katu AI",           "Assistente de inteligência artificial",               "katu-ai"),
            "backup":     ("☁️",  "Katu Backup",       "Crie e restaure backups dos seus arquivos",           "katu-backup"),
            "connect":    ("📱", "Katu Connect",      "Conecte e gerencie seu smartphone",                  "katu-connect"),
            "diagnostic": ("🔍", "Katu Diagnostic",   "Verifique a saúde do seu computador",                 "katu-diagnostic"),
            "help":       ("❓", "Katu Help",         "Central de ajuda e documentação offline",             "katu-help"),
        }
        for page_id, (icon, title, desc, cmd) in external.items():
            page = AppLaunchPage(icon, title, desc, cmd)
            self._pages[page_id] = page
            self._stack.addWidget(page)

        # Security (inline)
        self._pages["security"] = self._build_security_page()
        self._stack.addWidget(self._pages["security"])

        # System info (inline)
        self._pages["system"] = self._build_system_page()
        self._stack.addWidget(self._pages["system"])

    def _build_security_page(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(32, 32, 32, 32)
        lay.setSpacing(16)
        t = QLabel("🔒 Segurança")
        t.setStyleSheet(f"font-size:20px; font-weight:bold; color:{ui.TEXT};")
        lay.addWidget(t)

        items = [
            ("Atualizações de segurança", "Verificando..."),
            ("Firewall (UFW)",            "Verificando..."),
            ("Sessão atual",              "Usuário comum"),
        ]
        for title, val in items:
            row = QHBoxLayout()
            lbl = QLabel(title)
            lbl.setStyleSheet(f"color:{ui.TEXT};")
            val_lbl = QLabel(val)
            val_lbl.setStyleSheet(f"color:{ui.MUTED};")
            row.addWidget(lbl, 1)
            row.addWidget(val_lbl)
            card = QFrame()
            card.setObjectName("card")
            card.setLayout(row)
            card.setFixedHeight(52)
            card.setStyleSheet(f"QFrame#card{{background:{ui.CARD};border:1px solid {ui.BORDER};border-radius:8px;padding:0 16px;}}")
            lay.addWidget(card)
        lay.addStretch()
        return w

    def _build_system_page(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(32, 32, 32, 32)
        lay.setSpacing(16)
        t = QLabel("⚙️ Meu Computador")
        t.setStyleSheet(f"font-size:20px; font-weight:bold; color:{ui.TEXT};")
        lay.addWidget(t)
        self._sys_labels = {}
        fields = [
            ("os_name",   "Sistema",         "Katu OS"),
            ("os_ver",    "Versão",           "Carregando..."),
            ("kernel",    "Kernel Linux",     "Carregando..."),
            ("plasma",    "KDE Plasma",       "Carregando..."),
            ("arch",      "Arquitetura",      "amd64"),
            ("cpu",       "Processador",      "Carregando..."),
            ("ram",       "Memória RAM",      "Carregando..."),
            ("gpu",       "Placa de vídeo",   "Carregando..."),
            ("disk",      "Armazenamento /",  "Carregando..."),
        ]
        for key, label, default in fields:
            row = QHBoxLayout()
            lbl_k = QLabel(label)
            lbl_k.setFixedWidth(180)
            lbl_k.setStyleSheet(f"color:{ui.MUTED}; font-size:12px;")
            lbl_v = QLabel(default)
            lbl_v.setStyleSheet(f"color:{ui.TEXT}; font-size:13px;")
            row.addWidget(lbl_k)
            row.addWidget(lbl_v, 1)
            self._sys_labels[key] = lbl_v
            card = QFrame()
            card.setFixedHeight(44)
            card.setStyleSheet(f"background:{ui.CARD}; border:1px solid {ui.BORDER}; border-radius:8px; padding:0 16px;")
            card.setLayout(row)
            lay.addWidget(card)
        lay.addStretch()
        return w

    def _select_page(self, page_id):
        for pid, item in self._items.items():
            item.setSelected(pid == page_id)
        if page_id in self._pages:
            self._stack.setCurrentWidget(self._pages[page_id])

    def _on_data(self, data):
        # Update home page
        home = self._pages.get("home")
        if home:
            home.update_system_data(data)
        # Update system page
        if data:
            os_i = data.get("os", {})
            cpu_i = data.get("cpu", {})
            mem_i = data.get("mem", {})
            disks = data.get("disk", [])
            sys_labels = self._sys_labels
            if os_i:
                sys_labels.get("os_ver",  QLabel()).setText(os_i.get("version", "?"))
                sys_labels.get("kernel",  QLabel()).setText(os_i.get("kernel",  "?"))
                sys_labels.get("plasma",  QLabel()).setText(os_i.get("plasma",  "?"))
                sys_labels.get("arch",    QLabel()).setText(os_i.get("arch",    "?"))
            if cpu_i:
                sys_labels.get("cpu", QLabel()).setText(
                    f"{cpu_i.get('model','?')} ({cpu_i.get('cores',0)} núcleos)")
            if mem_i:
                total = mem_i.get("total_mb", 0)
                gb = f"{total/1024:.1f} GB" if total else "?"
                sys_labels.get("ram", QLabel()).setText(
                    f"{gb} total ({mem_i.get('percent',0)}% em uso)")
            if CORE:
                try:
                    gpu = system.get_gpu_info()
                    sys_labels.get("gpu", QLabel()).setText(gpu)
                except Exception:
                    pass
            if disks:
                root = next((d for d in disks if d["mount"] == "/"), None)
                if root:
                    sys_labels.get("disk", QLabel()).setText(
                        f"{root['used']} usados / {root['size']} total ({root['avail']} livres)")


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Katu Central")
    app.setApplicationVersion("1.0.1")
    if CORE:
        app.setStyleSheet(ui.STYLESHEET)
    win = KatuCentral()
    win.show()
    sys.exit(app.exec_() if QT == 'PyQt5' else app.exec())


if __name__ == "__main__":
    main()
