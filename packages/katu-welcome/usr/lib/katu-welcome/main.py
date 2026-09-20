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

KATU_VERSION = "1.0"
KATU_GREEN = "#1a5c2a"
KATU_EMERALD = "#2ecc71"
KATU_GOLD = "#f39c12"
KATU_DARK = "#1a1a1a"
KATU_WHITE = "#f8f9fa"

STYLESHEET = f"""
QMainWindow {{
    background-color: {KATU_DARK};
}}
QWidget {{
    background-color: {KATU_DARK};
    color: {KATU_WHITE};
    font-family: 'Noto Sans', 'Liberation Sans', sans-serif;
}}
QLabel#titulo {{
    font-size: 28px;
    font-weight: bold;
    color: {KATU_WHITE};
}}
QLabel#subtitulo {{
    font-size: 14px;
    color: {KATU_EMERALD};
    font-style: italic;
}}
QLabel#versao {{
    font-size: 11px;
    color: #888888;
}}
QPushButton.card {{
    background-color: #2a2a2a;
    border: 1px solid #3a3a3a;
    border-radius: 8px;
    padding: 16px;
    text-align: left;
    color: {KATU_WHITE};
    font-size: 13px;
    min-height: 70px;
    min-width: 200px;
}}
QPushButton.card:hover {{
    background-color: #333333;
    border: 1px solid {KATU_EMERALD};
}}
QPushButton.card:pressed {{
    background-color: {KATU_GREEN};
}}
QPushButton#btn-fechar {{
    background-color: transparent;
    border: 1px solid #555555;
    border-radius: 6px;
    padding: 8px 20px;
    color: #aaaaaa;
    font-size: 12px;
}}
QPushButton#btn-fechar:hover {{
    border-color: {KATU_EMERALD};
    color: {KATU_WHITE};
}}
QCheckBox {{
    font-size: 12px;
    color: #aaaaaa;
    spacing: 8px;
}}
QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border-radius: 3px;
    border: 1px solid #555555;
    background: #2a2a2a;
}}
QCheckBox::indicator:checked {{
    background-color: {KATU_EMERALD};
    border-color: {KATU_EMERALD};
}}
"""

CARDS = [
    {
        "titulo": "Atualizar sistema",
        "descricao": "Instalar atualizações disponíveis",
        "icone": "system-software-update",
        "acao": "update",
    },
    {
        "titulo": "Instalar aplicativos",
        "descricao": "Abrir a loja de aplicativos",
        "icone": "plasmadiscover",
        "acao": "discover",
    },
    {
        "titulo": "Habilitar Flathub",
        "descricao": "Mais aplicativos via Flatpak",
        "icone": "flatpak",
        "acao": "flathub",
    },
    {
        "titulo": "Drivers de hardware",
        "descricao": "Verificar drivers necessários",
        "icone": "preferences-devices",
        "acao": "drivers",
    },
    {
        "titulo": "Configurar aparência",
        "descricao": "Personalizar o visual do sistema",
        "icone": "preferences-desktop-theme",
        "acao": "aparencia",
    },
    {
        "titulo": "Configurações",
        "descricao": "Configurações do sistema",
        "icone": "systemsettings",
        "acao": "configuracoes",
    },
    {
        "titulo": "Documentação",
        "descricao": "Guias e tutoriais Katu OS",
        "icone": "help-contents",
        "acao": "docs",
    },
    {
        "titulo": "Sobre o Katu OS",
        "descricao": "Versão, licença e créditos",
        "icone": "help-about",
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
                subprocess.Popen(['xdg-open', 'https://katuos.org/docs'])
            elif self.acao == "sobre":
                subprocess.Popen(['systemsettings', 'kcm_about-distro'])
            self.concluido.emit(self.acao, True)
        except Exception as e:
            print(f"Erro ao executar ação '{self.acao}': {e}")
            self.concluido.emit(self.acao, False)


class KatuWelcomeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bem-vindo ao Katu OS")
        self.setMinimumSize(700, 560)
        self.resize(800, 600)
        self.setStyleSheet(STYLESHEET)

        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        layout_principal = QVBoxLayout(widget_central)
        layout_principal.setContentsMargins(40, 32, 40, 24)
        layout_principal.setSpacing(24)

        # Cabeçalho
        cabecalho = QWidget()
        layout_cabecalho = QVBoxLayout(cabecalho)
        layout_cabecalho.setSpacing(4)
        layout_cabecalho.setContentsMargins(0, 0, 0, 0)

        titulo = QLabel("Bem-vindo ao Katu OS")
        titulo.setObjectName("titulo")
        titulo.setAlignment(Qt.AlignLeft)

        subtitulo = QLabel("Livre. Brasileiro. Para todos.")
        subtitulo.setObjectName("subtitulo")

        versao = QLabel(f"Versão {KATU_VERSION} · Baseado em Debian")
        versao.setObjectName("versao")

        layout_cabecalho.addWidget(titulo)
        layout_cabecalho.addWidget(subtitulo)
        layout_cabecalho.addWidget(versao)

        # Grade de cards
        area_scroll = QScrollArea()
        area_scroll.setWidgetResizable(True)
        area_scroll.setFrameShape(QFrame.NoFrame)
        area_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        widget_grade = QWidget()
        grade = QGridLayout(widget_grade)
        grade.setSpacing(12)
        grade.setContentsMargins(0, 0, 0, 0)

        for i, card in enumerate(CARDS):
            btn = QPushButton()
            btn.setProperty("class", "card")
            btn.setStyleSheet(
                f"QPushButton {{ background-color: #2a2a2a; border: 1px solid #3a3a3a; "
                f"border-radius: 8px; padding: 16px; text-align: left; "
                f"color: {KATU_WHITE}; font-size: 13px; min-height: 70px; }} "
                f"QPushButton:hover {{ background-color: #333333; border-color: {KATU_EMERALD}; }} "
                f"QPushButton:pressed {{ background-color: {KATU_GREEN}; }}"
            )

            layout_card = QVBoxLayout(btn)
            layout_card.setContentsMargins(8, 8, 8, 8)

            lbl_titulo = QLabel(f"<b>{card['titulo']}</b>")
            lbl_titulo.setStyleSheet(f"color: {KATU_WHITE}; font-size: 13px;")
            lbl_desc = QLabel(card['descricao'])
            lbl_desc.setStyleSheet("color: #aaaaaa; font-size: 11px;")

            layout_card.addWidget(lbl_titulo)
            layout_card.addWidget(lbl_desc)

            acao = card['acao']
            btn.clicked.connect(lambda checked, a=acao: self._executar_acao(a))

            linha = i // 2
            coluna = i % 2
            grade.addWidget(btn, linha, coluna)

        area_scroll.setWidget(widget_grade)

        # Rodapé
        rodape = QWidget()
        layout_rodape = QHBoxLayout(rodape)
        layout_rodape.setContentsMargins(0, 0, 0, 0)

        self.chk_abrir = QCheckBox("Abrir automaticamente ao iniciar sessão")
        self.chk_abrir.setChecked(self._obter_autostart())
        self.chk_abrir.stateChanged.connect(self._toggle_autostart)

        btn_fechar = QPushButton("Fechar")
        btn_fechar.setObjectName("btn-fechar")
        btn_fechar.clicked.connect(self.close)

        layout_rodape.addWidget(self.chk_abrir)
        layout_rodape.addStretch()
        layout_rodape.addWidget(btn_fechar)

        layout_principal.addWidget(cabecalho)
        layout_principal.addWidget(area_scroll, 1)
        layout_principal.addWidget(rodape)

    def _executar_acao(self, acao):
        self.thread = AcaoThread(acao)
        self.thread.start()

    def _obter_autostart(self):
        autostart = os.path.expanduser(
            '~/.config/autostart/katu-welcome.desktop'
        )
        return os.path.exists(autostart)

    def _toggle_autostart(self, estado):
        autostart_dir = os.path.expanduser('~/.config/autostart')
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

    window = KatuWelcomeWindow()
    window.show()

    sys.exit(app.exec_() if QT_BACKEND == 'PyQt5' else app.exec())


if __name__ == '__main__':
    main()
