#!/usr/bin/env python3
"""
Katu Store — Loja de Aplicativos do Katu OS
Instale software sem precisar de terminal.
"""
import sys, os, subprocess, json
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
    from katu_core import ui
    from katu_core.packages import apt_install, apt_remove, apt_is_installed, flatpak_install, flatpak_remove, flatpak_is_installed, flatpak_ensure_flathub
    CORE = True
except ImportError:
    CORE = False
    class _FakeUI:
        STYLESHEET = ""
        BG = "#0d1117"; SURFACE = "#161b22"; CARD = "#1c2128"; BORDER = "#30363d"
        ACCENT = "#00c853"; ACCENT_H = "#00e676"; TEXT = "#e6edf3"; MUTED = "#8b949e"
        ERROR = "#f85149"; AMBER = "#ffab00"; SUCCESS = "#3fb950"; TEXT_INV = "#0d1117"
    ui = _FakeUI()
    def apt_install(p, cb=None): return False
    def apt_remove(p, cb=None): return False
    def apt_is_installed(p): return False
    def flatpak_install(p, cb=None): return False
    def flatpak_remove(p, cb=None): return False
    def flatpak_is_installed(p): return False
    def flatpak_ensure_flathub(): return False

# ── Catálogo ──────────────────────────────────────────────────────────────────
CATALOG = {
    "Destaques": [
        {"id": "vlc",       "name": "VLC",           "desc": "Reprodutor multimídia completo",      "icon": "🎬", "source": "apt",     "pkg": "vlc"},
        {"id": "firefox",   "name": "Firefox",       "desc": "Navegador de internet",               "icon": "🦊", "source": "apt",     "pkg": "firefox-esr"},
        {"id": "libreoffice","name":"LibreOffice",    "desc": "Suite completa de escritório",        "icon": "📝", "source": "apt",     "pkg": "libreoffice"},
        {"id": "gimp",      "name": "GIMP",          "desc": "Editor de imagens profissional",      "icon": "🎨", "source": "apt",     "pkg": "gimp"},
        {"id": "vscode",    "name": "VS Code",       "desc": "Editor de código da Microsoft",       "icon": "💻", "source": "flatpak", "pkg": "com.visualstudio.code"},
    ],
    "Brasil": [
        {"id": "receitanet","name": "Programa IRPF","desc": "Declaração Imposto de Renda (Receita Federal)","icon":"🇧🇷","source":"webapp","url":"https://www.gov.br/receitafederal/pt-br"},
        {"id": "govbr",     "name": "GOV.BR",       "desc": "Portal do Governo Federal do Brasil",  "icon": "🏛️", "source": "webapp",  "url": "https://www.gov.br"},
        {"id": "caixa",     "name": "CAIXA",        "desc": "Site oficial da Caixa Econômica Federal","icon":"🏦","source":"webapp","url":"https://www.caixa.gov.br"},
        {"id": "bb",        "name": "Banco do Brasil","desc":"Site oficial do Banco do Brasil",      "icon": "💳", "source": "webapp",  "url": "https://www.bb.com.br"},
        {"id": "broffice",  "name": "LibreOffice BR","desc":"LibreOffice em português do Brasil",    "icon": "📝", "source": "apt",     "pkg": "libreoffice-l10n-pt-br"},
        {"id": "nubank",    "name": "Nubank",       "desc": "Site do Nubank",                       "icon": "💜", "source": "webapp",  "url": "https://nubank.com.br"},
        {"id": "meuinss",   "name": "Meu INSS",     "desc": "Serviços do INSS online",              "icon": "🏥", "source": "webapp",  "url": "https://meu.inss.gov.br"},
    ],
    "Comunicação": [
        {"id": "telegram",  "name": "Telegram",     "desc": "Mensagens instantâneas",               "icon": "✈️", "source": "flatpak", "pkg": "org.telegram.desktop"},
        {"id": "whatsapp",  "name": "WhatsApp",     "desc": "WhatsApp Web",                         "icon": "💬", "source": "webapp",  "url": "https://web.whatsapp.com"},
        {"id": "discord",   "name": "Discord",      "desc": "Comunicação para comunidades",         "icon": "🎮", "source": "flatpak", "pkg": "com.discordapp.Discord"},
        {"id": "zoom",      "name": "Zoom",         "desc": "Videoconferências",                    "icon": "📹", "source": "flatpak", "pkg": "us.zoom.Zoom"},
        {"id": "signal",    "name": "Signal",       "desc": "Mensagens criptografadas",             "icon": "🔐", "source": "flatpak", "pkg": "org.signal.Signal"},
    ],
    "Internet": [
        {"id": "chrome",    "name": "Google Chrome","desc": "Navegador Google Chrome",              "icon": "🌐", "source": "apt",     "pkg": "google-chrome-stable"},
        {"id": "chromium",  "name": "Chromium",     "desc": "Navegador de código aberto",           "icon": "🌐", "source": "apt",     "pkg": "chromium"},
        {"id": "thunderbird","name":"Thunderbird",   "desc": "Cliente de e-mail",                   "icon": "📧", "source": "apt",     "pkg": "thunderbird"},
        {"id": "qbittorrent","name":"qBittorrent",   "desc": "Cliente BitTorrent",                  "icon": "⬇️", "source": "apt",     "pkg": "qbittorrent"},
    ],
    "Multimídia": [
        {"id": "audacity",  "name": "Audacity",     "desc": "Editor de áudio",                     "icon": "🎵", "source": "flatpak", "pkg": "org.audacityteam.Audacity"},
        {"id": "handbrake", "name": "HandBrake",    "desc": "Conversor de vídeo",                  "icon": "🎬", "source": "flatpak", "pkg": "fr.handbrake.ghb"},
        {"id": "kdenlive",  "name": "Kdenlive",     "desc": "Editor de vídeo profissional",        "icon": "🎞️", "source": "flatpak", "pkg": "org.kde.kdenlive"},
        {"id": "obs",       "name": "OBS Studio",   "desc": "Gravação e streaming",                "icon": "📡", "source": "flatpak", "pkg": "com.obsproject.Studio"},
        {"id": "spotify",   "name": "Spotify",      "desc": "Streaming de música",                 "icon": "🎧", "source": "flatpak", "pkg": "com.spotify.Client"},
    ],
    "Produtividade": [
        {"id": "libreoffice-full","name":"LibreOffice","desc":"Suite completa de escritório",       "icon": "📝", "source": "apt",     "pkg": "libreoffice"},
        {"id": "obsidian",  "name": "Obsidian",     "desc": "Notas em Markdown",                   "icon": "🔮", "source": "flatpak", "pkg": "md.obsidian.Obsidian"},
        {"id": "onlyoffice","name": "OnlyOffice",   "desc": "Suite Office compatível com Word",    "icon": "📊", "source": "flatpak", "pkg": "org.onlyoffice.desktopeditors"},
        {"id": "joplin",    "name": "Joplin",       "desc": "Notas e lista de tarefas",            "icon": "📓", "source": "flatpak", "pkg": "net.cozic.joplin_desktop"},
    ],
    "Desenvolvimento": [
        {"id": "vscode",    "name": "VS Code",      "desc": "Editor de código",                    "icon": "💻", "source": "flatpak", "pkg": "com.visualstudio.code"},
        {"id": "sublime",   "name": "Sublime Text", "desc": "Editor de texto para código",         "icon": "✏️", "source": "apt",     "pkg": "sublime-text"},
        {"id": "android-studio","name":"Android Studio","desc":"IDE para apps Android",            "icon": "📱", "source": "flatpak", "pkg": "com.google.AndroidStudio"},
        {"id": "postman",   "name": "Postman",      "desc": "Testes de API REST",                  "icon": "📮", "source": "flatpak", "pkg": "com.getpostman.Postman"},
        {"id": "dbeaver",   "name": "DBeaver",      "desc": "Gerenciador de banco de dados",       "icon": "🗄️", "source": "flatpak", "pkg": "io.dbeaver.DBeaverCommunity"},
    ],
    "Gráficos": [
        {"id": "inkscape",  "name": "Inkscape",     "desc": "Editor de imagens vetoriais",         "icon": "✏️", "source": "apt",     "pkg": "inkscape"},
        {"id": "krita",     "name": "Krita",        "desc": "Pintura digital profissional",        "icon": "🖌️", "source": "flatpak", "pkg": "org.kde.krita"},
        {"id": "blender",   "name": "Blender",      "desc": "Modelagem e animação 3D",             "icon": "🧊", "source": "flatpak", "pkg": "org.blender.Blender"},
        {"id": "darktable", "name": "Darktable",    "desc": "Edição de fotos RAW",                 "icon": "📷", "source": "flatpak", "pkg": "org.darktable.Darktable"},
    ],
    "Jogos": [
        {"id": "steam",     "name": "Steam",        "desc": "Plataforma de jogos Valve",           "icon": "🎮", "source": "apt",     "pkg": "steam"},
        {"id": "lutris",    "name": "Lutris",       "desc": "Gerenciador de jogos Linux",          "icon": "🕹️", "source": "flatpak", "pkg": "net.lutris.Lutris"},
        {"id": "heroic",    "name": "Heroic Games", "desc": "Epic Games / GOG no Linux",           "icon": "🦸", "source": "flatpak", "pkg": "com.heroicgameslauncher.hgl"},
        {"id": "0ad",       "name": "0 A.D.",       "desc": "Estratégia histórica em tempo real",  "icon": "⚔️", "source": "apt",     "pkg": "0ad"},
    ],
    "IA": [
        {"id": "katu-ai",   "name": "Katu AI",      "desc": "Assistente IA do Katu OS",            "icon": "🤖", "source": "apt",     "pkg": "katu-ai"},
        {"id": "katu-ia",   "name": "Katu IA Dev",  "desc": "Hub IA para desenvolvedores",         "icon": "💻", "source": "apt",     "pkg": "katu-ia"},
    ],
    "Utilitários": [
        {"id": "vlc",       "name": "VLC",          "desc": "Reprodutor multimídia",               "icon": "🎬", "source": "apt",     "pkg": "vlc"},
        {"id": "ark",       "name": "Ark",          "desc": "Compactador e descompactador",        "icon": "📦", "source": "apt",     "pkg": "ark"},
        {"id": "kcalc",     "name": "KCalc",        "desc": "Calculadora científica",              "icon": "🧮", "source": "apt",     "pkg": "kcalc"},
        {"id": "kate",      "name": "Kate",         "desc": "Editor de texto avançado",            "icon": "✏️", "source": "apt",     "pkg": "kate"},
        {"id": "filelight", "name": "Filelight",    "desc": "Uso de disco visual",                 "icon": "💿", "source": "apt",     "pkg": "filelight"},
    ],
}

# ── Install Thread ────────────────────────────────────────────────────────────
class InstallThread(QThread):
    progress = pyqtSignal(str)
    done     = pyqtSignal(bool)

    def __init__(self, app_info, install=True):
        super().__init__()
        self._app = app_info
        self._install = install

    def run(self):
        app = self._app
        source = app.get("source")
        pkg    = app.get("pkg", "")
        ok = False
        try:
            if self._install:
                if source == "apt":
                    ok = apt_install(pkg, self.progress.emit)
                elif source == "flatpak":
                    flatpak_ensure_flathub()
                    ok = flatpak_install(pkg, self.progress.emit)
            else:
                if source == "apt":
                    ok = apt_remove(pkg, self.progress.emit)
                elif source == "flatpak":
                    ok = flatpak_remove(pkg, self.progress.emit)
        except Exception as e:
            self.progress.emit(f"Erro: {e}")
        self.done.emit(ok)


# ── App Card ──────────────────────────────────────────────────────────────────
class AppCard(QFrame):
    install_requested = pyqtSignal(dict)
    remove_requested  = pyqtSignal(dict)
    open_webapp       = pyqtSignal(dict)

    def __init__(self, app_info, parent=None):
        super().__init__(parent)
        self._app = app_info
        self.setObjectName("appCard")
        self.setFixedHeight(96)
        self.setStyleSheet(f"""
            QFrame#appCard {{
                background:{ui.CARD}; border:1px solid {ui.BORDER};
                border-radius:10px;
            }}
        """)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 10, 14, 10)
        lay.setSpacing(12)

        ico = QLabel(app_info.get("icon", "📦"))
        ico.setFixedSize(40, 40)
        ico.setAlignment(Qt.AlignCenter)
        ico.setStyleSheet(f"font-size:24px; background:{ui.SURFACE}; border-radius:8px;")

        info = QVBoxLayout()
        info.setSpacing(2)
        name = QLabel(app_info.get("name", ""))
        name.setStyleSheet(f"font-weight:bold; color:{ui.TEXT}; font-size:13px;")
        desc = QLabel(app_info.get("desc", ""))
        desc.setStyleSheet(f"color:{ui.MUTED}; font-size:12px;")
        source = app_info.get("source", "")
        src_colors = {"apt": ui.SUCCESS, "flatpak": ui.INFO, "webapp": ui.AMBER}
        src_label = QLabel(f"Fonte: {source.upper()}")
        src_label.setStyleSheet(f"color:{src_colors.get(source, ui.MUTED)}; font-size:11px;")
        info.addWidget(name)
        info.addWidget(desc)
        info.addWidget(src_label)

        self._btn = QPushButton()
        self._btn.setFixedSize(90, 34)
        self._btn.clicked.connect(self._on_btn)
        self._update_btn()

        lay.addWidget(ico)
        lay.addLayout(info, 1)
        lay.addWidget(self._btn, alignment=Qt.AlignVCenter)

    def _is_installed(self):
        app = self._app
        if app.get("source") == "apt":
            return apt_is_installed(app.get("pkg", ""))
        elif app.get("source") == "flatpak":
            return flatpak_is_installed(app.get("pkg", ""))
        return False

    def _update_btn(self):
        source = self._app.get("source")
        if source == "webapp":
            self._btn.setText("Abrir")
            self._btn.setObjectName("primary")
        elif self._is_installed():
            self._btn.setText("Remover")
            self._btn.setObjectName("")
        else:
            self._btn.setText("Instalar")
            self._btn.setObjectName("primary")
        self._btn.setStyleSheet("")  # force refresh

    def _on_btn(self):
        source = self._app.get("source")
        if source == "webapp":
            self.open_webapp.emit(self._app)
        elif self._is_installed():
            self.remove_requested.emit(self._app)
        else:
            self.install_requested.emit(self._app)

    def mark_installing(self):
        self._btn.setText("...")
        self._btn.setEnabled(False)

    def mark_done(self):
        self._btn.setEnabled(True)
        self._update_btn()


# ── Main Window ───────────────────────────────────────────────────────────────
class KatuStore(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Katu Store")
        self.setMinimumSize(900, 600)
        self.resize(1100, 700)
        self.setWindowIcon(QIcon("/usr/share/icons/hicolor/256x256/apps/katu-logo.png"))
        self._active_cards = {}
        self._threads = {}
        self._build_ui()

    def _build_ui(self):
        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)
        lay = QVBoxLayout(root)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # Top bar
        topbar = self._build_topbar()
        lay.addWidget(topbar)

        # Body
        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        # Category list
        self._cat_list = self._build_cat_list()
        body.addWidget(self._cat_list)

        # App grid scroll
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.NoFrame)
        self._grid_widget = QWidget()
        self._grid_layout = QVBoxLayout(self._grid_widget)
        self._grid_layout.setContentsMargins(24, 20, 24, 24)
        self._grid_layout.setSpacing(10)
        self._scroll.setWidget(self._grid_widget)
        body.addWidget(self._scroll, 1)

        body_w = QWidget()
        body_w.setLayout(body)
        lay.addWidget(body_w, 1)

        # Status bar
        self._status = QLabel("Pronto")
        self._status.setStyleSheet(f"color:{ui.MUTED}; font-size:12px; padding:4px 16px;")
        self._status.setFixedHeight(28)
        self._status.setStyleSheet(f"background:{ui.SURFACE}; border-top:1px solid {ui.BORDER}; color:{ui.MUTED}; padding:4px 16px; font-size:12px;")
        lay.addWidget(self._status)

        self._load_category("Destaques")

    def _build_topbar(self):
        bar = QWidget()
        bar.setFixedHeight(60)
        bar.setStyleSheet(f"background:{ui.SURFACE}; border-bottom:1px solid {ui.BORDER};")
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(20, 8, 20, 8)
        lay.setSpacing(12)
        logo = QLabel("📦 Katu Store")
        logo.setStyleSheet(f"font-size:16px; font-weight:bold; color:{ui.TEXT};")
        self._search = QLineEdit()
        self._search.setPlaceholderText("Pesquisar aplicativos...")
        self._search.setFixedHeight(36)
        self._search.setMaximumWidth(320)
        self._search.textChanged.connect(self._on_search)
        lay.addWidget(logo)
        lay.addWidget(self._search, 1)
        return bar

    def _build_cat_list(self):
        lst = QListWidget()
        lst.setFixedWidth(180)
        lst.setStyleSheet(f"""
            QListWidget {{ background:{ui.SURFACE}; border:none; border-right:1px solid {ui.BORDER}; }}
            QListWidget::item {{ padding:10px 16px; color:{ui.MUTED}; font-size:13px; }}
            QListWidget::item:selected {{ background:{ui.CARD}; color:{ui.TEXT}; border-left:3px solid {ui.ACCENT}; }}
        """)
        for cat in CATALOG.keys():
            lst.addItem(cat)
        lst.setCurrentRow(0)
        lst.currentTextChanged.connect(self._load_category)
        return lst

    def _load_category(self, cat):
        for i in reversed(range(self._grid_layout.count())):
            w = self._grid_layout.itemAt(i).widget()
            if w:
                w.deleteLater()

        apps = CATALOG.get(cat, [])
        title = QLabel(cat)
        title.setStyleSheet(f"font-size:18px; font-weight:bold; color:{ui.TEXT}; padding-bottom:4px;")
        self._grid_layout.addWidget(title)

        grid = QGridLayout()
        grid.setSpacing(10)
        for i, app in enumerate(apps):
            card = AppCard(app)
            card.install_requested.connect(self._on_install)
            card.remove_requested.connect(self._on_remove)
            card.open_webapp.connect(self._on_webapp)
            self._active_cards[app["id"]] = card
            grid.addWidget(card, i // 2, i % 2)
        w = QWidget()
        w.setLayout(grid)
        self._grid_layout.addWidget(w)
        self._grid_layout.addStretch()

    def _on_search(self, text):
        text = text.lower().strip()
        if not text:
            return
        for i in reversed(range(self._grid_layout.count())):
            w = self._grid_layout.itemAt(i).widget()
            if w:
                w.deleteLater()
        title = QLabel(f'Resultados para "{text}"')
        title.setStyleSheet(f"font-size:18px; font-weight:bold; color:{ui.TEXT}; padding-bottom:4px;")
        self._grid_layout.addWidget(title)
        grid = QGridLayout()
        grid.setSpacing(10)
        idx = 0
        for cat_apps in CATALOG.values():
            for app in cat_apps:
                if text in app.get("name","").lower() or text in app.get("desc","").lower():
                    card = AppCard(app)
                    card.install_requested.connect(self._on_install)
                    card.remove_requested.connect(self._on_remove)
                    card.open_webapp.connect(self._on_webapp)
                    self._active_cards[app["id"]] = card
                    grid.addWidget(card, idx // 2, idx % 2)
                    idx += 1
        if idx == 0:
            self._grid_layout.addWidget(QLabel("Nenhum resultado encontrado."))
        else:
            w = QWidget()
            w.setLayout(grid)
            self._grid_layout.addWidget(w)
        self._grid_layout.addStretch()

    def _on_install(self, app_info):
        reply = QMessageBox.question(
            self, "Instalar aplicativo",
            f"Instalar {app_info['name']}?\nFonte: {app_info['source'].upper()}",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        card = self._active_cards.get(app_info["id"])
        if card:
            card.mark_installing()
        self._status.setText(f"Instalando {app_info['name']}...")
        t = InstallThread(app_info, install=True)
        t.progress.connect(lambda msg: self._status.setText(msg[-80:]))
        t.done.connect(lambda ok: self._on_install_done(app_info, ok, card))
        t.start()
        self._threads[app_info["id"]] = t

    def _on_remove(self, app_info):
        reply = QMessageBox.question(
            self, "Remover aplicativo",
            f"Remover {app_info['name']}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        card = self._active_cards.get(app_info["id"])
        if card:
            card.mark_installing()
        t = InstallThread(app_info, install=False)
        t.done.connect(lambda ok: self._on_install_done(app_info, ok, card))
        t.start()
        self._threads[app_info["id"]] = t

    def _on_install_done(self, app_info, ok, card):
        if ok:
            self._status.setText(f"✓ {app_info['name']} — concluído")
        else:
            self._status.setText(f"✗ Falha ao processar {app_info['name']}")
        if card:
            card.mark_done()

    def _on_webapp(self, app_info):
        url = app_info.get("url", "")
        if url:
            subprocess.Popen(["xdg-open", url])


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Katu Store")
    if CORE:
        app.setStyleSheet(ui.STYLESHEET)
    win = KatuStore()
    win.show()
    sys.exit(app.exec_() if QT == 'PyQt5' else app.exec())


if __name__ == "__main__":
    main()
