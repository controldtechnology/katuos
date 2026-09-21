#!/usr/bin/env python3
"""
Katu XAMPP — Painel de Controle LAMP
Apache2 + PHP + MariaDB + phpMyAdmin
Interface visual estilo XAMPP para o público brasileiro
"""

import sys, os, subprocess, shutil, webbrowser, time
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

BG = "#0d1117"; BG_ALT = "#161b22"; BG_CARD = "#1c2128"
BORDER = "#30363d"; GREEN = "#00c853"; GREEN_H = "#00e676"
AMBER = "#ffab00"; TEXT = "#e6edf3"; MUTED = "#8b949e"
NEG = "#f85149"; LINK = "#58a6ff"

WWWROOT = Path("/var/www/html")
LOG_APACHE = Path("/var/log/apache2/error.log")
LOG_MYSQL  = Path("/var/log/mysql/error.log")

STYLE = f"""
* {{ font-family: 'Noto Sans','Liberation Sans',sans-serif; font-size:13px; color:{TEXT}; }}
QMainWindow,QWidget#root {{ background:{BG}; }}
QWidget {{ background:transparent; }}
QFrame#header {{ background:{BG_ALT}; border-bottom:1px solid {BORDER}; }}
QFrame#card {{
    background:{BG_CARD}; border:1px solid {BORDER};
    border-radius:10px;
}}
QPushButton#verde {{
    background:{GREEN}; color:{BG}; border:none; border-radius:6px;
    padding:8px 20px; font-weight:bold;
}}
QPushButton#verde:hover {{ background:{GREEN_H}; }}
QPushButton#verde:disabled {{ background:{BORDER}; color:{MUTED}; }}
QPushButton#vermelho {{
    background:{NEG}; color:white; border:none; border-radius:6px;
    padding:8px 20px; font-weight:bold;
}}
QPushButton#vermelho:hover {{ background:#ff6b6b; }}
QPushButton#outline {{
    background:transparent; color:{MUTED}; border:1px solid {BORDER};
    border-radius:6px; padding:8px 18px;
}}
QPushButton#outline:hover {{ border-color:{TEXT}; color:{TEXT}; }}
QTextEdit {{
    background:{BG_CARD}; border:1px solid {BORDER}; border-radius:8px;
    padding:10px; color:{TEXT}; font-family:'Noto Mono','Monospace'; font-size:12px;
}}
QScrollBar:vertical {{ background:{BG}; width:5px; border-radius:3px; }}
QScrollBar::handle:vertical {{ background:{BORDER}; border-radius:3px; }}
QTabWidget::pane {{ border:1px solid {BORDER}; border-radius:8px; background:{BG_ALT}; }}
QTabBar::tab {{ background:{BG}; color:{MUTED}; padding:10px 20px; border-bottom:2px solid transparent; }}
QTabBar::tab:selected {{ color:{GREEN}; border-bottom:2px solid {GREEN}; }}
"""

def _lbl(t, size=13, bold=False, cor=TEXT):
    l = QLabel(t); f = QFont()
    f.setPointSize(size)
    if bold: f.setWeight(QFont.Bold)
    l.setFont(f); l.setStyleSheet(f"color:{cor};background:transparent;")
    l.setWordWrap(True); return l

def _btn(t, obj="verde"):
    b = QPushButton(t); b.setObjectName(obj)
    b.setCursor(Qt.PointingHandCursor); return b

def _sep():
    f = QFrame(); f.setFrameShape(QFrame.HLine)
    f.setStyleSheet(f"background:{BORDER};max-height:1px;border:none;"); return f

def checar_servico(nome):
    try:
        r = subprocess.run(['systemctl', 'is-active', nome],
                           capture_output=True, text=True, timeout=3)
        return r.stdout.strip() == 'active'
    except Exception:
        return False

def controlar_servico(acao, nome):
    try:
        subprocess.run(['pkexec', 'systemctl', acao, nome],
                       timeout=10, check=True)
        return True
    except Exception:
        return False


class ServicoWidget(QFrame):
    """Card de controle de um serviço (Apache/MySQL/PHP)"""

    def __init__(self, nome_display, nome_servico, porta, descricao, cor_icone):
        super().__init__()
        self.setObjectName("card")
        self.nome_servico = nome_servico
        self._ativo = False

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(16)

        # Indicador de status
        self.indicador = QLabel("●")
        self.indicador.setFixedWidth(20)
        self.indicador.setStyleSheet(f"color:{BORDER}; font-size:20px;")

        # Info
        info = QVBoxLayout(); info.setSpacing(3)
        lbl_nome = _lbl(nome_display, 14, bold=True)
        self.lbl_status = _lbl("Verificando…", 12, cor=MUTED)
        lbl_desc = _lbl(descricao, 11, cor=BORDER)
        info.addWidget(lbl_nome)
        info.addWidget(self.lbl_status)
        info.addWidget(lbl_desc)

        # Porta
        lbl_porta = _lbl(f"Porta {porta}", 12, cor=MUTED)
        lbl_porta.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        lbl_porta.setFixedWidth(80)

        # Botões
        btns = QHBoxLayout(); btns.setSpacing(8)
        self.btn_iniciar = _btn("Iniciar", "verde")
        self.btn_parar   = _btn("Parar",   "vermelho")
        self.btn_iniciar.setFixedWidth(90)
        self.btn_parar.setFixedWidth(90)
        self.btn_iniciar.clicked.connect(lambda: self._controlar("start"))
        self.btn_parar.clicked.connect(  lambda: self._controlar("stop"))
        btns.addWidget(self.btn_iniciar)
        btns.addWidget(self.btn_parar)

        layout.addWidget(self.indicador)
        layout.addLayout(info)
        layout.addStretch()
        layout.addWidget(lbl_porta)
        layout.addLayout(btns)

        self.atualizar()

    def atualizar(self):
        self._ativo = checar_servico(self.nome_servico)
        if self._ativo:
            self.indicador.setStyleSheet(f"color:{GREEN}; font-size:20px;")
            self.lbl_status.setText("● Ativo")
            self.lbl_status.setStyleSheet(f"color:{GREEN}; font-size:12px;")
            self.btn_iniciar.setEnabled(False)
            self.btn_parar.setEnabled(True)
        else:
            self.indicador.setStyleSheet(f"color:{NEG}; font-size:20px;")
            self.lbl_status.setText("○ Parado")
            self.lbl_status.setStyleSheet(f"color:{MUTED}; font-size:12px;")
            self.btn_iniciar.setEnabled(True)
            self.btn_parar.setEnabled(False)

    def _controlar(self, acao):
        self.btn_iniciar.setEnabled(False)
        self.btn_parar.setEnabled(False)
        self.lbl_status.setText("⟳  Aguardando…")
        self.lbl_status.setStyleSheet(f"color:{AMBER};")
        ok = controlar_servico(acao, self.nome_servico)
        QTimer.singleShot(1200, self.atualizar)


class AbaServicos(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        # Botões globais
        barra = QHBoxLayout()
        self.btn_iniciar_tudo = _btn("▶  Iniciar tudo", "verde")
        self.btn_parar_tudo   = _btn("■  Parar tudo",   "vermelho")
        self.btn_atualizar    = _btn("↺  Atualizar",     "outline")
        self.btn_iniciar_tudo.clicked.connect(self._iniciar_tudo)
        self.btn_parar_tudo.clicked.connect(self._parar_tudo)
        self.btn_atualizar.clicked.connect(self._atualizar_todos)
        barra.addWidget(self.btn_iniciar_tudo)
        barra.addWidget(self.btn_parar_tudo)
        barra.addStretch()
        barra.addWidget(self.btn_atualizar)
        layout.addLayout(barra)
        layout.addWidget(_sep())

        # Cards de serviços
        self.apache = ServicoWidget(
            "Apache",       "apache2",       80,
            "Servidor web HTTP — hospeda seus sites em /var/www/html", GREEN)
        self.mysql  = ServicoWidget(
            "MariaDB (MySQL)", "mariadb",    3306,
            "Banco de dados MySQL/MariaDB — compatível com todo o ecossistema", AMBER)
        self.php    = ServicoWidget(
            "PHP",          "php8.2-fpm",   9000,
            "PHP 8.2 FastCGI — processa scripts PHP nos seus projetos", LINK)

        layout.addWidget(self.apache)
        layout.addWidget(self.mysql)
        layout.addWidget(self.php)
        layout.addStretch()

        # Links rápidos
        links = QHBoxLayout(); links.setSpacing(12)
        for texto, url in [
            ("🌐  Abrir localhost",     "http://localhost"),
            ("🗄️   phpMyAdmin",          "http://localhost/phpmyadmin"),
            ("📁  Pasta www",           None),
        ]:
            b = _btn(texto, "outline")
            if url:
                b.clicked.connect(lambda u=url: webbrowser.open(u))
            else:
                b.clicked.connect(lambda: subprocess.Popen(['dolphin', str(WWWROOT)]))
            links.addWidget(b)
        links.addStretch()
        layout.addLayout(links)

        # Timer de atualização automática
        self._timer = QTimer()
        self._timer.timeout.connect(self._atualizar_todos)
        self._timer.start(5000)

    def _atualizar_todos(self):
        for s in [self.apache, self.mysql, self.php]:
            s.atualizar()

    def _iniciar_tudo(self):
        for servico in ["apache2", "mariadb"]:
            controlar_servico("start", servico)
        QTimer.singleShot(1500, self._atualizar_todos)

    def _parar_tudo(self):
        for servico in ["apache2", "mariadb"]:
            controlar_servico("stop", servico)
        QTimer.singleShot(1500, self._atualizar_todos)


class AbaArquivos(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        layout.addWidget(_lbl("Pasta de Projetos Web", 16, bold=True))
        layout.addWidget(_lbl(
            f"Coloque seus projetos em: {WWWROOT}\n"
            "Acesse via: http://localhost/nome-do-projeto",
            13, cor=MUTED))

        # Atalhos
        grid = QGridLayout(); grid.setSpacing(10)
        acoes = [
            ("📁  Abrir no Dolphin",     lambda: subprocess.Popen(['dolphin', str(WWWROOT)])),
            ("💻  Abrir no Terminal",    lambda: subprocess.Popen(['konsole', '--workdir', str(WWWROOT)])),
            ("🌐  Abrir localhost",      lambda: webbrowser.open('http://localhost')),
            ("🗄️   phpMyAdmin",           lambda: webbrowser.open('http://localhost/phpmyadmin')),
            ("📝  php.ini",              lambda: subprocess.Popen(['kate', '/etc/php/8.2/apache2/php.ini'])),
            ("⚙️   httpd.conf",          lambda: subprocess.Popen(['kate', '/etc/apache2/apache2.conf'])),
        ]
        for i, (txt, acao) in enumerate(acoes):
            b = _btn(txt, "outline"); b.clicked.connect(acao)
            b.setFixedHeight(48)
            grid.addWidget(b, i // 2, i % 2)
        layout.addLayout(grid)

        layout.addWidget(_sep())
        layout.addWidget(_lbl("Criar novo projeto", 14, bold=True))

        row = QHBoxLayout()
        self.campo_proj = QLineEdit()
        self.campo_proj.setPlaceholderText("nome-do-projeto")
        self.campo_proj.setFixedHeight(40)
        btn_criar = _btn("Criar projeto", "verde")
        btn_criar.clicked.connect(self._criar_projeto)
        row.addWidget(self.campo_proj)
        row.addWidget(btn_criar)
        layout.addLayout(row)

        self.lbl_resultado = _lbl("", 12, cor=GREEN)
        layout.addWidget(self.lbl_resultado)

        layout.addStretch()

    def _criar_projeto(self):
        nome = self.campo_proj.text().strip().replace(" ", "-")
        if not nome:
            return
        pasta = WWWROOT / nome
        try:
            pasta.mkdir(parents=True, exist_ok=True)
            (pasta / "index.php").write_text(
                f"<?php\n// Projeto: {nome}\necho '<h1>🚀 {nome} — funcionando!</h1>';\necho '<p>Katu OS + LAMP stack</p>';\n")
            self.lbl_resultado.setText(f"✓  Projeto criado! Acesse: http://localhost/{nome}")
            self.lbl_resultado.setStyleSheet(f"color:{GREEN};font-size:12px;")
            self.campo_proj.clear()
        except PermissionError:
            self.lbl_resultado.setText(f"✗  Sem permissão. Tente: sudo chown -R $USER /var/www/html")
            self.lbl_resultado.setStyleSheet(f"color:{NEG};font-size:12px;")


class AbaLog(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        barra = QHBoxLayout()
        self.combo_log = QComboBox()
        self.combo_log.addItems(["Apache — Erros", "MariaDB — Erros"])
        btn_atualizar = _btn("↺  Atualizar", "outline")
        btn_atualizar.clicked.connect(self._carregar)
        barra.addWidget(self.combo_log)
        barra.addStretch()
        barra.addWidget(btn_atualizar)
        layout.addLayout(barra)

        self.txt = QTextEdit(); self.txt.setReadOnly(True)
        layout.addWidget(self.txt, 1)

        self.combo_log.currentIndexChanged.connect(self._carregar)
        self._carregar()

        # Auto-refresh
        t = QTimer(); t.timeout.connect(self._carregar); t.start(3000)

    def _carregar(self):
        idx = self.combo_log.currentIndex()
        path = LOG_APACHE if idx == 0 else LOG_MYSQL
        try:
            if path.exists():
                linhas = path.read_text(errors='replace').splitlines()
                self.txt.setPlainText('\n'.join(linhas[-100:]))
                self.txt.verticalScrollBar().setValue(
                    self.txt.verticalScrollBar().maximum())
            else:
                self.txt.setPlainText(f"Log não encontrado: {path}")
        except Exception as e:
            self.txt.setPlainText(f"Erro ao ler log: {e}")


class KatuXAMPP(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Katu XAMPP — Painel LAMP")
        self.setMinimumSize(860, 620)
        self.resize(920, 660)
        self.setStyleSheet(STYLE)

        central = QWidget(); central.setObjectName("root")
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QFrame(); header.setObjectName("header"); header.setFixedHeight(56)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(24, 0, 24, 0)
        h_layout.addWidget(_lbl("Katu XAMPP", 16, bold=True, cor=AMBER))
        h_layout.addSpacing(12)
        h_layout.addWidget(_lbl("Apache · PHP 8.2 · MariaDB · phpMyAdmin", 12, cor=MUTED))
        h_layout.addStretch()
        # Status geral
        self.lbl_status_geral = _lbl("Verificando…", 12, cor=MUTED)
        h_layout.addWidget(self.lbl_status_geral)
        layout.addWidget(header)

        # Abas
        tabs = QTabWidget(); tabs.setDocumentMode(True)
        tabs.addTab(AbaServicos(),  "⚡  Serviços")
        tabs.addTab(AbaArquivos(), "📁  Projetos")
        tabs.addTab(AbaLog(),      "📋  Logs")
        tabs.addTab(self._aba_info(), "ℹ️   Info")
        layout.addWidget(tabs, 1)

        # Status update timer
        t = QTimer(); t.timeout.connect(self._atualizar_status_geral); t.start(4000)
        self._atualizar_status_geral()

    def _atualizar_status_geral(self):
        ativo_a = checar_servico("apache2")
        ativo_m = checar_servico("mariadb")
        if ativo_a and ativo_m:
            self.lbl_status_geral.setText("● Todos os serviços ativos")
            self.lbl_status_geral.setStyleSheet(f"color:{GREEN};font-size:12px;")
        elif ativo_a or ativo_m:
            self.lbl_status_geral.setText("◐ Serviços parcialmente ativos")
            self.lbl_status_geral.setStyleSheet(f"color:{AMBER};font-size:12px;")
        else:
            self.lbl_status_geral.setText("○ Serviços parados")
            self.lbl_status_geral.setStyleSheet(f"color:{MUTED};font-size:12px;")

    def _aba_info(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)
        layout.addWidget(_lbl("Configuração do servidor LAMP", 16, bold=True))

        def info_row(rotulo, valor):
            r = QHBoxLayout()
            r.addWidget(_lbl(rotulo, 12, cor=MUTED, bold=True))
            r.addWidget(_lbl(valor, 12))
            r.addStretch()
            layout.addLayout(r)

        info_row("Pasta de projetos:",  "/var/www/html/")
        info_row("URL local:",          "http://localhost/")
        info_row("phpMyAdmin:",         "http://localhost/phpmyadmin/")
        info_row("Usuário MySQL root:", "root (sem senha localmente)")
        info_row("Porta Apache:",       "80 (HTTP) / 443 (HTTPS)")
        info_row("Porta MariaDB:",      "3306")
        info_row("Versão PHP:",         "8.2 (FPM + CLI)")
        info_row("Config Apache:",      "/etc/apache2/apache2.conf")
        info_row("Config PHP:",         "/etc/php/8.2/apache2/php.ini")
        info_row("Config MySQL:",       "/etc/mysql/mariadb.conf.d/")

        layout.addWidget(_sep())
        layout.addWidget(_lbl("Comandos úteis no terminal:", 13, bold=True))
        for cmd in [
            "sudo systemctl start apache2 mariadb",
            "sudo systemctl stop apache2 mariadb",
            "sudo mysql -u root              # Entrar no MySQL",
            "sudo a2enmod rewrite            # Habilitar mod_rewrite",
            "php -v                          # Verificar versão PHP",
            "composer install               # Instalar dependências",
        ]:
            lbl = QLabel(f"<code style='color:{GREEN};'>{cmd}</code>")
            lbl.setTextFormat(Qt.RichText)
            lbl.setStyleSheet("background:transparent;")
            layout.addWidget(lbl)

        layout.addStretch()
        return w


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Katu XAMPP")
    w = KatuXAMPP()
    w.show()
    sys.exit(app.exec_() if QT == 'PyQt5' else app.exec())

if __name__ == '__main__':
    main()
