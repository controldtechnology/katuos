#!/usr/bin/env python3
"""
Katu OS Welcome Application
Bem-vindo ao Katu OS — Livre. Brasileiro. Para todos.
"""

import sys
import os
import subprocess

try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QCheckBox, QScrollArea, QFrame, QGridLayout,
        QSizePolicy
    )
    from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal
    from PyQt5.QtGui import QPixmap, QFont, QColor, QPalette, QIcon
    QT_BACKEND = 'PyQt5'
except ImportError:
    try:
        from PySide6.QtWidgets import (
            QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
            QLabel, QPushButton, QCheckBox, QScrollArea, QFrame, QGridLayout,
            QSizePolicy
        )
        from PySide6.QtCore import Qt, QSize, QThread, Signal as pyqtSignal
        from PySide6.QtGui import QPixmap, QFont, QColor, QPalette, QIcon
        QT_BACKEND = 'PySide6'
    except ImportError:
        print("Erro: PyQt5 ou PySide6 não encontrado.")
        sys.exit(1)

# === Katu Design System 2.0: floresta, rio e luz âmbar ===
KATU_VERSION       = "1.0"
KATU_BG            = "#001111"
KATU_BG_ALT        = "#002211"
KATU_BG_CARD       = "#003322"
KATU_BORDER        = "#335544"
KATU_BORDER_HOVER  = "#557766"
KATU_ACCENT        = "#DDAA44"
KATU_ACCENT_HOVER  = "#FFCC55"
KATU_ACCENT_PRESSED= "#AA7733"
KATU_AMBER         = "#FFCC55"
KATU_TEXT          = "#EEEEDD"
KATU_TEXT_MUTED    = "#C8D3C9"
KATU_NEGATIVE      = "#C85C55"
KATU_LINK           = "#75B9C6"

STYLESHEET = f"""
QMainWindow {{
    background-color: {KATU_BG};
    border: 1px solid {KATU_BORDER};
}}
QWidget {{
    background-color: {KATU_BG};
    color: {KATU_TEXT};
    font-family: 'Noto Sans', 'Liberation Sans', sans-serif;
}}
QScrollArea, QScrollArea > QWidget > QWidget {{
    background-color: transparent;
    border: none;
}}
QLabel#titulo {{
    font-size: 32px;
    font-weight: 600;
    color: {KATU_TEXT};
    letter-spacing: -0.5px;
}}
QLabel#subtitulo {{
    font-size: 13px;
    color: {KATU_ACCENT};
    letter-spacing: 0.3px;
}}
QLabel#versao {{
    font-size: 11px;
    color: {KATU_TEXT_MUTED};
}}
QFrame#separator {{
    background-color: {KATU_BORDER};
    max-height: 1px;
}}
QFrame#hero {{
    background-color: {KATU_BG_ALT};
    border: 1px solid {KATU_BORDER};
    border-radius: 14px;
}}
QLabel#hero-art {{
    background-color: {KATU_BG_CARD};
    border-top-left-radius: 14px;
    border-bottom-left-radius: 14px;
}}
QLabel#hero-copy {{
    background: transparent;
    color: {KATU_TEXT_MUTED};
    font-size: 14px;
}}
QPushButton#btn-fechar {{
    background-color: transparent;
    border: 1px solid {KATU_BORDER};
    border-radius: 6px;
    padding: 8px 20px;
    color: {KATU_TEXT_MUTED};
    font-size: 12px;
}}
QPushButton#btn-fechar:hover {{
    border-color: {KATU_ACCENT};
    color: {KATU_TEXT};
    background-color: {KATU_BG_ALT};
}}
QPushButton#btn-live-primary {{
    background-color: {KATU_ACCENT};
    border: 1px solid {KATU_ACCENT};
    border-radius: 8px;
    padding: 12px 20px;
    color: {KATU_BG};
    font-size: 14px;
    font-weight: 600;
}}
QPushButton#btn-live-primary:hover {{
    background-color: {KATU_ACCENT_HOVER};
    border-color: {KATU_ACCENT_HOVER};
}}
QPushButton#btn-live-secondary {{
    background-color: {KATU_BG_CARD};
    border: 1px solid {KATU_BORDER_HOVER};
    border-radius: 8px;
    padding: 12px 20px;
    color: {KATU_TEXT};
    font-size: 14px;
    font-weight: 600;
}}
QPushButton#btn-live-secondary:hover {{
    background-color: {KATU_BG_ALT};
    border-color: {KATU_ACCENT};
}}
QCheckBox {{
    font-size: 12px;
    color: {KATU_TEXT_MUTED};
    spacing: 8px;
}}
QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1px solid {KATU_BORDER};
    background: {KATU_BG_ALT};
}}
QCheckBox::indicator:checked {{
    background-color: {KATU_ACCENT};
    border-color: {KATU_ACCENT};
}}
QCheckBox::indicator:hover {{
    border-color: {KATU_ACCENT};
}}
"""

CARDS = [
    {
        "titulo": "Atualizar sistema",
        "descricao": "Instalar todas as atualizações disponíveis",
        "icone": "system-software-update",
        "cor_accent": KATU_ACCENT,
        "acao": "update",
    },
    {
        "titulo": "Instalar aplicativos",
        "descricao": "Abrir a loja de aplicativos Discover",
        "icone": "plasmadiscover",
        "cor_accent": KATU_LINK,
        "acao": "discover",
    },
    {
        "titulo": "Habilitar Flathub",
        "descricao": "Adicionar repositório com mais de 2.000 apps",
        "icone": "flatpak",
        "cor_accent": KATU_AMBER,
        "acao": "flathub",
    },
    {
        "titulo": "Drivers de hardware",
        "descricao": "Verificar e instalar drivers necessários",
        "icone": "preferences-devices",
        "cor_accent": KATU_ACCENT,
        "acao": "drivers",
    },
    {
        "titulo": "Configurar aparência",
        "descricao": "Personalizar cores, tema e wallpaper",
        "icone": "preferences-desktop-theme",
        "cor_accent": KATU_AMBER,
        "acao": "aparencia",
    },
    {
        "titulo": "Configurações do sistema",
        "descricao": "Ajustar som, rede, usuários e mais",
        "icone": "systemsettings",
        "cor_accent": KATU_LINK,
        "acao": "configuracoes",
    },
    {
        "titulo": "Documentação",
        "descricao": "Guias, tutoriais e suporte Katu OS",
        "icone": "help-contents",
        "cor_accent": KATU_TEXT_MUTED,
        "acao": "docs",
    },
    {
        "titulo": "Sobre o Katu OS",
        "descricao": "Versão, licença, créditos e sistema",
        "icone": "help-about",
        "cor_accent": KATU_TEXT_MUTED,
        "acao": "sobre",
    },
]


class AcaoThread(QThread):
    concluido = pyqtSignal(str, bool)

    def __init__(self, acao):
        super().__init__()
        self.acao = acao

    def run(self):
        try:
            if self.acao == "update":
                subprocess.Popen([
                    'pkexec', 'bash', '-c',
                    'apt-get update && apt-get upgrade -y'
                ])
            elif self.acao == "discover":
                subprocess.Popen(['plasma-discover'])
            elif self.acao == "flathub":
                subprocess.Popen([
                    'pkexec', 'flatpak', 'remote-add', '--if-not-exists',
                    'flathub', 'https://dl.flathub.org/repo/flathub.flatpakrepo'
                ])
            elif self.acao == "drivers":
                subprocess.Popen(['systemsettings', 'kcm_device_automounter'])
            elif self.acao == "aparencia":
                subprocess.Popen(['systemsettings', 'kcm_lookandfeel'])
            elif self.acao == "configuracoes":
                subprocess.Popen(['systemsettings'])
            elif self.acao == "docs":
                subprocess.Popen(['xdg-open', 'https://katuos.com.br/docs'])
            elif self.acao == "sobre":
                subprocess.Popen(['systemsettings', 'kcm_about-distro'])
            self.concluido.emit(self.acao, True)
        except Exception as e:
            print(f"Erro ao executar ação '{self.acao}': {e}")
            self.concluido.emit(self.acao, False)


class CardButton(QPushButton):
    def __init__(self, titulo, descricao, icone, cor_accent, parent=None):
        super().__init__(parent)
        self._cor_accent = cor_accent
        self._normal_style = (
            f"QPushButton {{ background-color: {KATU_BG_CARD}; "
            f"border: 1px solid {KATU_BORDER}; border-radius: 10px; "
            f"padding: 12px 14px; text-align: left; color: {KATU_TEXT}; "
            f"min-height: 76px; }}"
            f"QPushButton:hover {{ background-color: {KATU_BG_ALT}; "
            f"border-color: {cor_accent}; }}"
            f"QPushButton:pressed {{ background-color: {KATU_BG}; }}"
        )
        self.setStyleSheet(self._normal_style)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(12)

        icon_label = QLabel()
        icon_label.setFixedSize(32, 32)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("background: transparent;")
        icon_label.setPixmap(QIcon.fromTheme(icone).pixmap(QSize(26, 26)))

        lbl_titulo = QLabel(f"<b>{titulo}</b>")
        lbl_titulo.setStyleSheet(f"color: {KATU_TEXT}; font-size: 13px; background: transparent;")

        lbl_desc = QLabel(descricao)
        lbl_desc.setStyleSheet(f"color: {KATU_TEXT_MUTED}; font-size: 11px; background: transparent;")
        lbl_desc.setWordWrap(True)

        copy = QVBoxLayout()
        copy.setContentsMargins(0, 0, 0, 0)
        copy.setSpacing(5)
        copy.addWidget(lbl_titulo)
        copy.addWidget(lbl_desc)
        layout.addWidget(icon_label)
        layout.addLayout(copy, 1)


class KatuWelcomeWindow(QMainWindow):
    def __init__(self, live_mode=False):
        super().__init__()
        self.live_mode = live_mode
        self.setWindowTitle("Bem-vindo ao Katu OS")
        self.setMinimumSize(720, 560)
        self.resize(920, 660)
        self.setStyleSheet(STYLESHEET)

        if self.live_mode:
            self.setMinimumSize(680, 520)
            self.resize(900, 600)
            self._live_art_source = QPixmap()
            self._live_art_label = None
            self._build_live_window()
            return

        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        layout_principal = QVBoxLayout(widget_central)
        layout_principal.setContentsMargins(28, 24, 28, 20)
        layout_principal.setSpacing(14)

        # Hero editorial com arte oficial; as ações nativas permanecem abaixo.
        hero = QFrame()
        hero.setObjectName("hero")
        hero.setMinimumHeight(170)
        layout_hero = QHBoxLayout(hero)
        layout_hero.setContentsMargins(0, 0, 20, 0)
        layout_hero.setSpacing(22)

        hero_art = QLabel()
        hero_art.setObjectName("hero-art")
        hero_art.setMinimumWidth(250)
        hero_art.setMaximumWidth(360)
        hero_art.setMinimumHeight(170)
        hero_art.setAlignment(Qt.AlignCenter)
        hero_art.setPixmap(QPixmap('/usr/share/katu/welcome/hero.png').scaled(
            360, 190, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))

        hero_copy = QWidget()
        hero_copy.setStyleSheet("background: transparent;")
        layout_hero_copy = QVBoxLayout(hero_copy)
        layout_hero_copy.setContentsMargins(0, 18, 0, 18)
        layout_hero_copy.setSpacing(6)

        titulo = QLabel("Bem-vindo ao Katu OS")
        titulo.setObjectName("titulo")

        subtitulo = QLabel("Livre. Brasileiro. Para todos.")
        subtitulo.setObjectName("subtitulo")

        descricao_hero = QLabel("Um espaço livre e acolhedor para trabalhar, estudar e criar.")
        descricao_hero.setObjectName("hero-copy")
        descricao_hero.setWordWrap(True)

        versao = QLabel(f"Versão {KATU_VERSION} · Debian 13 · KDE Plasma")
        versao.setObjectName("versao")

        layout_hero_copy.addWidget(titulo)
        layout_hero_copy.addWidget(subtitulo)
        layout_hero_copy.addWidget(descricao_hero)
        layout_hero_copy.addStretch()
        layout_hero_copy.addWidget(versao)
        layout_hero.addWidget(hero_art, 4)
        layout_hero.addWidget(hero_copy, 5)

        # Separador
        sep = QFrame()
        sep.setObjectName("separator")
        sep.setFrameShape(QFrame.HLine)

        # Grade de cards
        area_scroll = QScrollArea()
        area_scroll.setWidgetResizable(True)
        area_scroll.setFrameShape(QFrame.NoFrame)

        widget_grade = QWidget()
        grade = QGridLayout(widget_grade)
        grade.setSpacing(10)
        grade.setContentsMargins(0, 0, 0, 0)

        for i, card in enumerate(CARDS):
            btn = CardButton(card['titulo'], card['descricao'], card['icone'], card['cor_accent'])
            acao = card['acao']
            btn.clicked.connect(lambda checked, a=acao: self._executar_acao(a))
            grade.addWidget(btn, i // 2, i % 2)

        area_scroll.setWidget(widget_grade)

        # Rodapé
        rodape = QWidget()
        layout_rodape = QHBoxLayout(rodape)
        layout_rodape.setContentsMargins(0, 0, 0, 0)

        self.chk_abrir = QCheckBox("Abrir automaticamente no início da sessão")
        self.chk_abrir.setChecked(self._obter_autostart())
        self.chk_abrir.stateChanged.connect(self._toggle_autostart)

        btn_fechar = QPushButton("Fechar")
        btn_fechar.setObjectName("btn-fechar")
        btn_fechar.clicked.connect(self.close)

        layout_rodape.addWidget(self.chk_abrir)
        layout_rodape.addStretch()
        layout_rodape.addWidget(btn_fechar)

        layout_principal.addWidget(hero)
        layout_principal.addWidget(sep)
        layout_principal.addWidget(area_scroll, 1)
        layout_principal.addWidget(rodape)

    def _build_live_window(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 18, 20, 16)
        layout.setSpacing(12)

        arte = QLabel()
        arte.setAlignment(Qt.AlignCenter)
        arte.setMinimumHeight(380)
        arte.setStyleSheet(
            f"background-color: {KATU_BG_ALT}; border: 1px solid {KATU_BORDER}; "
            "border-radius: 12px;"
        )
        self._live_art_source = QPixmap('/usr/share/katu/welcome/hero.png')
        self._live_art_label = arte
        self._update_live_art()
        arte.setAccessibleName("Boas-vindas ao Katu OS")

        actions = QHBoxLayout()
        actions.setSpacing(12)

        btn_experimentar = QPushButton("Experimentar o Katu OS")
        btn_experimentar.setObjectName("btn-live-secondary")
        btn_experimentar.setMinimumHeight(48)
        btn_experimentar.setAccessibleDescription(
            "Fechar esta tela e continuar usando o sistema Live"
        )
        btn_experimentar.clicked.connect(self.close)

        btn_instalar = QPushButton("Instalar Katu OS")
        btn_instalar.setObjectName("btn-live-primary")
        btn_instalar.setMinimumHeight(48)
        btn_instalar.setAccessibleDescription(
            "Abrir o instalador do sistema no computador"
        )
        btn_instalar.clicked.connect(self._abrir_instalador)

        actions.addWidget(btn_experimentar, 1)
        actions.addWidget(btn_instalar, 1)

        dica = QLabel("Você pode fechar esta janela e continuar usando o modo Live.")
        dica.setAlignment(Qt.AlignCenter)
        dica.setStyleSheet(f"color: {KATU_TEXT_MUTED}; font-size: 12px;")

        layout.addWidget(arte, 1)
        layout.addLayout(actions)
        layout.addWidget(dica)

    def _update_live_art(self):
        if self._live_art_label is None or self._live_art_source.isNull():
            return
        available = self._live_art_label.size() - QSize(16, 16)
        if available.width() <= 0 or available.height() <= 0:
            return
        self._live_art_label.setPixmap(self._live_art_source.scaled(
            available, Qt.KeepAspectRatio, Qt.SmoothTransformation
        ))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.live_mode:
            self._update_live_art()

    def _abrir_instalador(self):
        subprocess.Popen(['katu-installer'])
        self.close()

    def _executar_acao(self, acao):
        self.thread = AcaoThread(acao)
        self.thread.start()

    def _obter_autostart(self):
        autostart = os.path.expanduser('~/.config/autostart/katu-welcome.desktop')
        return os.path.exists(autostart)

    def _remover_flag_firstboot(self):
        try:
            if os.path.exists('/etc/katu-firstboot'):
                os.remove('/etc/katu-firstboot')
        except PermissionError:
            pass  # sem sudo não é possível — não é crítico

    def _toggle_autostart(self, estado):
        autostart_dir  = os.path.expanduser('~/.config/autostart')
        autostart_file = os.path.join(autostart_dir, 'katu-welcome.desktop')

        if estado:
            os.makedirs(autostart_dir, exist_ok=True)
            with open(autostart_file, 'w') as f:
                f.write(
                    "[Desktop Entry]\n"
                    "Type=Application\n"
                    "Name=Katu Welcome\n"
                    "Exec=katu-welcome\n"
                    "Hidden=false\n"
                    "NoDisplay=false\n"
                    "X-GNOME-Autostart-enabled=true\n"
                )
        else:
            if os.path.exists(autostart_file):
                os.remove(autostart_file)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Katu Welcome")
    app.setApplicationVersion(KATU_VERSION)
    app.setOrganizationName("Katu OS")

    live_mode = '--live' in sys.argv[1:]
    window = KatuWelcomeWindow(live_mode=live_mode)
    if not live_mode:
        window._remover_flag_firstboot()
    window.show()

    sys.exit(app.exec_() if QT_BACKEND == 'PyQt5' else app.exec())


if __name__ == '__main__':
    main()
