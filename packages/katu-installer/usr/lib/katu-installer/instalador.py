#!/usr/bin/env python3
"""
Katu Instalador — Assistente de Instalação
Interface amigável estilo Windows 11 para o público brasileiro.
"""

import sys
import os
import subprocess
import shutil
import platform

try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QStackedWidget, QFrame, QRadioButton,
        QButtonGroup, QLineEdit, QCheckBox, QProgressBar, QSizePolicy,
        QSpacerItem, QGraphicsDropShadowEffect
    )
    from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve
    from PyQt5.QtGui import QPixmap, QFont, QColor, QPalette, QIcon, QPainter, QBrush
    QT = 'PyQt5'
except ImportError:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QStackedWidget, QFrame, QRadioButton,
        QButtonGroup, QLineEdit, QCheckBox, QProgressBar, QSizePolicy,
        QSpacerItem, QGraphicsDropShadowEffect
    )
    from PySide6.QtCore import Qt, QThread, Signal as pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve
    from PySide6.QtGui import QPixmap, QFont, QColor, QPalette, QIcon, QPainter, QBrush
    QT = 'PySide6'

# ─── Paleta Amazônia Dark ────────────────────────────────────────────────────
BG       = "#0d1117"
BG_ALT   = "#161b22"
BG_CARD  = "#1c2128"
BORDER   = "#30363d"
GREEN    = "#00c853"
GREEN_HV = "#00e676"
GREEN_PR = "#00a040"
AMBER    = "#ffab00"
TEXT     = "#e6edf3"
MUTED    = "#8b949e"
NEG      = "#f85149"
LINK     = "#58a6ff"

STYLE = f"""
* {{
    font-family: 'Noto Sans', 'Segoe UI', sans-serif;
    font-size: 14px;
    color: {TEXT};
}}
QMainWindow, QWidget#central {{
    background-color: {BG};
}}
QWidget {{
    background-color: transparent;
}}
QLabel {{
    background-color: transparent;
}}
QFrame#sidebar {{
    background-color: {BG_ALT};
    border-right: 1px solid {BORDER};
}}
QFrame#conteudo {{
    background-color: {BG};
}}
QFrame#card {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 12px;
}}
QFrame#card:hover {{
    border-color: {GREEN};
}}
QPushButton#btn_proximo {{
    background-color: {GREEN};
    color: {BG};
    border: none;
    border-radius: 8px;
    padding: 12px 32px;
    font-size: 14px;
    font-weight: bold;
    min-width: 160px;
}}
QPushButton#btn_proximo:hover {{
    background-color: {GREEN_HV};
}}
QPushButton#btn_proximo:pressed {{
    background-color: {GREEN_PR};
}}
QPushButton#btn_proximo:disabled {{
    background-color: {BORDER};
    color: {MUTED};
}}
QPushButton#btn_voltar {{
    background-color: transparent;
    color: {MUTED};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 12px 24px;
    font-size: 14px;
    min-width: 100px;
}}
QPushButton#btn_voltar:hover {{
    border-color: {TEXT};
    color: {TEXT};
}}
QPushButton#btn_cancelar {{
    background-color: transparent;
    color: {MUTED};
    border: none;
    padding: 8px 16px;
    font-size: 12px;
}}
QPushButton#btn_cancelar:hover {{
    color: {NEG};
}}
QRadioButton {{
    spacing: 12px;
    font-size: 14px;
    color: {TEXT};
    padding: 4px;
}}
QRadioButton::indicator {{
    width: 20px;
    height: 20px;
    border-radius: 10px;
    border: 2px solid {BORDER};
    background: {BG_ALT};
}}
QRadioButton::indicator:checked {{
    background: {GREEN};
    border-color: {GREEN};
}}
QLineEdit {{
    background-color: {BG_ALT};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 14px;
    color: {TEXT};
}}
QLineEdit:focus {{
    border-color: {GREEN};
    border-width: 2px;
}}
QLineEdit[erro="true"] {{
    border-color: {NEG};
}}
QCheckBox {{
    spacing: 10px;
    font-size: 13px;
    color: {MUTED};
}}
QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid {BORDER};
    background: {BG_ALT};
}}
QCheckBox::indicator:checked {{
    background: {GREEN};
    border-color: {GREEN};
}}
QProgressBar {{
    background-color: {BG_ALT};
    border: none;
    border-radius: 4px;
    height: 6px;
    text-align: center;
}}
QProgressBar::chunk {{
    background-color: {GREEN};
    border-radius: 4px;
}}
"""


def _lbl(texto, size=14, bold=False, cor=TEXT):
    l = QLabel(texto)
    f = QFont()
    f.setPointSize(size)
    if bold:
        f.setWeight(QFont.Bold)
    l.setFont(f)
    l.setStyleSheet(f"color: {cor}; background: transparent;")
    l.setWordWrap(True)
    return l


def _sep():
    f = QFrame()
    f.setFrameShape(QFrame.HLine)
    f.setStyleSheet(f"background-color: {BORDER}; max-height: 1px; border: none;")
    return f


# ─── Verificação de Requisitos ───────────────────────────────────────────────
def checar_requisitos():
    resultados = {}

    # RAM
    try:
        with open('/proc/meminfo') as f:
            for linha in f:
                if 'MemTotal' in linha:
                    kb = int(linha.split()[1])
                    gb = kb / 1024 / 1024
                    resultados['ram'] = {'valor': round(gb, 1), 'ok': gb >= 2}
                    break
    except Exception:
        resultados['ram'] = {'valor': 0, 'ok': False}

    # Disco
    try:
        stat = os.statvfs('/')
        gb = stat.f_bavail * stat.f_frsize / 1024**3
        resultados['disco'] = {'valor': round(gb, 1), 'ok': gb >= 20}
    except Exception:
        resultados['disco'] = {'valor': 0, 'ok': False}

    # Energia (detectar se é notebook com bateria)
    bat_path = '/sys/class/power_supply/BAT0'
    if os.path.exists(bat_path):
        try:
            status = open(f'{bat_path}/status').read().strip()
            resultados['energia'] = {'valor': status, 'ok': status == 'Charging'}
        except Exception:
            resultados['energia'] = {'valor': 'Desconhecido', 'ok': True}
    else:
        resultados['energia'] = {'valor': 'Fonte', 'ok': True}

    # Internet
    try:
        subprocess.run(['ping', '-c', '1', '-W', '2', '8.8.8.8'],
                       capture_output=True, timeout=3)
        resultados['internet'] = {'ok': True}
    except Exception:
        resultados['internet'] = {'ok': False}

    return resultados


# ─── Telas ───────────────────────────────────────────────────────────────────

class TelaBoasVindas(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 50, 60, 40)
        layout.setSpacing(0)

        # Logo
        logo = QLabel()
        logo.setAlignment(Qt.AlignLeft)
        pix = QPixmap('/usr/share/pixmaps/katu-logo.png')
        if not pix.isNull():
            logo.setPixmap(pix.scaledToWidth(140, Qt.SmoothTransformation))
        else:
            logo.setText("Katu OS")
            logo.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {GREEN};")
        layout.addWidget(logo)

        layout.addSpacing(48)

        titulo = _lbl("Bem-vindo ao\nKatu OS", size=32, bold=True)
        titulo.setStyleSheet(f"color: {TEXT}; font-size: 32px; font-weight: bold; line-height: 1.2;")
        layout.addWidget(titulo)

        layout.addSpacing(16)

        desc = _lbl(
            "Vamos instalar o Katu OS no seu computador.\n"
            "O processo é simples e leva apenas alguns minutos.",
            size=15, cor=MUTED
        )
        layout.addWidget(desc)

        layout.addSpacing(40)

        # Destaques
        for icone, texto in [
            ("✦", "Baseado em Debian 13 — o Linux mais confiável do mundo"),
            ("✦", "Interface KDE Plasma — moderna, rápida e em português"),
            ("✦", "Firefox, Chrome, LibreOffice e VLC já incluídos"),
            ("✦", "100% gratuito e de código aberto"),
        ]:
            row = QHBoxLayout()
            row.setSpacing(14)
            ic = _lbl(icone, size=12, cor=GREEN)
            ic.setFixedWidth(16)
            tx = _lbl(texto, size=13, cor=MUTED)
            row.addWidget(ic)
            row.addWidget(tx)
            row.addStretch()
            layout.addLayout(row)
            layout.addSpacing(8)

        layout.addStretch()

        nota = _lbl("Você precisará de conexão com a internet apenas para atualizações futuras.", size=11, cor=BORDER)
        layout.addWidget(nota)


class TelaRequisitos(QWidget):
    def __init__(self):
        super().__init__()
        self.layout_principal = QVBoxLayout(self)
        self.layout_principal.setContentsMargins(60, 50, 60, 40)
        self.layout_principal.setSpacing(0)

        self.layout_principal.addWidget(_lbl("Verificando seu computador", size=24, bold=True))
        self.layout_principal.addSpacing(8)
        self.layout_principal.addWidget(_lbl("Certifique-se de que tudo está em ordem antes de instalar.", size=14, cor=MUTED))
        self.layout_principal.addSpacing(32)

        self.container_itens = QVBoxLayout()
        self.layout_principal.addLayout(self.container_itens)
        self.layout_principal.addStretch()

        self._itens = {}
        self._adicionar_item('ram',      '💾', 'Memória RAM',       'Mínimo: 2 GB')
        self._adicionar_item('disco',    '💿', 'Espaço em disco',   'Mínimo: 20 GB livres')
        self._adicionar_item('energia',  '🔌', 'Fonte de energia',  'Recomendado: conectado na tomada')
        self._adicionar_item('internet', '🌐', 'Internet',          'Opcional — para atualizações futuras')

        self.atualizar()

    def _adicionar_item(self, chave, icone, titulo, desc):
        card = QFrame()
        card.setObjectName("card")
        card.setFixedHeight(72)
        row = QHBoxLayout(card)
        row.setContentsMargins(20, 0, 20, 0)
        row.setSpacing(16)

        ic_lbl = _lbl(icone, size=22)
        ic_lbl.setFixedWidth(36)

        info = QVBoxLayout()
        info.setSpacing(2)
        lbl_titulo = _lbl(titulo, size=14, bold=True)
        lbl_desc = _lbl(desc, size=12, cor=MUTED)
        info.addWidget(lbl_titulo)
        info.addWidget(lbl_desc)

        self.status_lbl = QLabel("…")
        self.status_lbl.setFixedWidth(100)
        self.status_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.status_lbl.setStyleSheet(f"color: {MUTED}; font-size: 12px;")

        row.addWidget(ic_lbl)
        row.addLayout(info)
        row.addStretch()
        row.addWidget(self.status_lbl)

        self._itens[chave] = {'card': card, 'status': self.status_lbl, 'desc': lbl_desc}
        self.container_itens.addWidget(card)
        self.container_itens.addSpacing(8)

    def atualizar(self):
        reqs = checar_requisitos()

        configs = {
            'ram':     (f"{reqs['ram']['valor']} GB disponíveis",     reqs['ram']['ok'],     "Mínimo: 2 GB — OK" if reqs['ram']['ok'] else f"Apenas {reqs['ram']['valor']} GB — recomendado 4 GB"),
            'disco':   (f"{reqs['disco']['valor']} GB disponíveis",   reqs['disco']['ok'],   "Espaço suficiente" if reqs['disco']['ok'] else f"Apenas {reqs['disco']['valor']} GB — precisa de 20 GB"),
            'energia': (reqs['energia']['valor'],                      reqs['energia']['ok'], "Conectado à tomada" if reqs['energia']['ok'] else "Use a fonte de energia para instalar"),
            'internet':(("Conectado" if reqs['internet']['ok'] else "Sem conexão"), True,    "Recomendado, mas não obrigatório"),
        }

        for chave, (valor, ok, desc_nova) in configs.items():
            item = self._itens[chave]
            cor = GREEN if ok else AMBER
            icone = "✓" if ok else "⚠"
            item['status'].setText(f"{icone} {valor}")
            item['status'].setStyleSheet(f"color: {cor}; font-size: 12px; font-weight: bold;")
            item['desc'].setText(desc_nova)
            item['desc'].setStyleSheet(f"color: {cor if not ok else MUTED}; font-size: 12px;")


class TelaDisco(QWidget):
    opcao_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 50, 60, 40)
        layout.setSpacing(0)

        layout.addWidget(_lbl("Onde instalar o Katu OS?", size=24, bold=True))
        layout.addSpacing(8)
        layout.addWidget(_lbl("Escolha como o Katu OS será instalado no disco.", size=14, cor=MUTED))
        layout.addSpacing(32)

        self.grupo = QButtonGroup(self)
        self.opcao_selecionada = "automatico"

        # Opção 1 — Automático (recomendado)
        self._card_auto = self._criar_opcao(
            "automatico",
            "🗂️  Instalar automaticamente",
            "Recomendado para a maioria das pessoas.\n"
            "O Katu OS ocupará o disco inteiro. Todos os dados serão apagados.",
            recomendado=True
        )

        # Opção 2 — Ao lado do Windows
        self._card_dual = self._criar_opcao(
            "dualsboot",
            "🪟  Instalar ao lado do Windows",
            "Mantém o Windows e instala o Katu OS no espaço livre.\n"
            "Você escolherá qual sistema iniciar toda vez que ligar o computador.",
            recomendado=False
        )

        # Opção 3 — Avançado
        self._card_manual = self._criar_opcao(
            "manual",
            "⚙️  Particionamento personalizado",
            "Para usuários avançados. Você configura as partições manualmente.",
            recomendado=False
        )

        layout.addWidget(self._card_auto)
        layout.addSpacing(10)
        layout.addWidget(self._card_dual)
        layout.addSpacing(10)
        layout.addWidget(self._card_manual)
        layout.addStretch()

        aviso = QFrame()
        aviso.setObjectName("card")
        aviso_layout = QHBoxLayout(aviso)
        aviso_layout.setContentsMargins(16, 12, 16, 12)
        ic = _lbl("⚠", size=16, cor=AMBER)
        ic.setFixedWidth(24)
        tx = _lbl("Na opção automática, TODOS os dados do disco selecionado serão apagados.\nFaça backup dos seus arquivos importantes antes de continuar.", size=12, cor=AMBER)
        aviso_layout.addWidget(ic)
        aviso_layout.addWidget(tx)
        layout.addWidget(aviso)

        # Selecionar automático por padrão
        self.grupo.buttons()[0].setChecked(True)

    def _criar_opcao(self, valor, titulo, descricao, recomendado):
        card = QFrame()
        card.setObjectName("card")
        card.setFixedHeight(100)
        card.setCursor(Qt.PointingHandCursor)

        row = QHBoxLayout(card)
        row.setContentsMargins(20, 0, 20, 0)
        row.setSpacing(16)

        radio = QRadioButton()
        radio.setProperty("valor", valor)
        self.grupo.addButton(radio)
        radio.toggled.connect(lambda checked, v=valor: self._ao_mudar(checked, v))

        info = QVBoxLayout()
        info.setSpacing(4)

        linha_titulo = QHBoxLayout()
        lbl_titulo = _lbl(titulo, size=14, bold=True)
        linha_titulo.addWidget(lbl_titulo)
        if recomendado:
            badge = QLabel(" Recomendado ")
            badge.setStyleSheet(
                f"background-color: {GREEN}; color: {BG}; border-radius: 4px; "
                f"padding: 2px 8px; font-size: 11px; font-weight: bold;"
            )
            linha_titulo.addWidget(badge)
        linha_titulo.addStretch()

        lbl_desc = _lbl(descricao, size=12, cor=MUTED)
        info.addLayout(linha_titulo)
        info.addWidget(lbl_desc)

        row.addWidget(radio)
        row.addLayout(info)

        # Clicar no card inteiro seleciona o radio
        card.mousePressEvent = lambda e, r=radio: r.setChecked(True)

        return card

    def _ao_mudar(self, checked, valor):
        if checked:
            self.opcao_selecionada = valor
            self.opcao_changed.emit(valor)

    def get_opcao(self):
        return self.opcao_selecionada


class TelaUsuario(QWidget):
    valido_changed = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 50, 60, 40)
        layout.setSpacing(0)

        layout.addWidget(_lbl("Quem vai usar este computador?", size=24, bold=True))
        layout.addSpacing(8)
        layout.addWidget(_lbl("Crie sua conta de usuário.", size=14, cor=MUTED))
        layout.addSpacing(36)

        form = QVBoxLayout()
        form.setSpacing(20)

        self.campo_nome = self._campo(form, "Seu nome completo", "Ex: João da Silva", "nome_completo")
        self.campo_nome.textChanged.connect(self._ao_digitar_nome)

        self.campo_usuario = self._campo(form, "Nome de usuário", "Ex: joao (sem espaços, letras minúsculas)", "nome_usuario")
        self.campo_usuario.textChanged.connect(self._validar)

        self.campo_senha = self._campo(form, "Senha", "Escolha uma senha segura", "senha", senha=True)
        self.campo_senha.textChanged.connect(self._validar)

        self.campo_confirmar = self._campo(form, "Confirmar senha", "Digite a senha novamente", "confirmar", senha=True)
        self.campo_confirmar.textChanged.connect(self._validar)

        self.lbl_forca = QLabel("")
        self.lbl_forca.setStyleSheet(f"color: {MUTED}; font-size: 12px;")
        form.addWidget(self.lbl_forca)

        self.lbl_erro = QLabel("")
        self.lbl_erro.setStyleSheet(f"color: {NEG}; font-size: 12px;")
        form.addWidget(self.lbl_erro)

        layout.addLayout(form)
        layout.addStretch()

        self.chk_autologin = QCheckBox("Entrar automaticamente (sem precisar digitar senha)")
        self.chk_autologin.setChecked(True)
        layout.addWidget(self.chk_autologin)

    def _campo(self, layout, rotulo, placeholder, nome, senha=False):
        lbl = _lbl(rotulo, size=13, bold=True)
        campo = QLineEdit()
        campo.setPlaceholderText(placeholder)
        campo.setObjectName(nome)
        if senha:
            campo.setEchoMode(QLineEdit.Password)
        layout.addWidget(lbl)
        layout.addWidget(campo)
        return campo

    def _ao_digitar_nome(self, texto):
        usuario = texto.lower().split()[0] if texto.strip() else ""
        usuario = ''.join(c for c in usuario if c.isalpha() or c.isdigit() or c == '_')
        self.campo_usuario.blockSignals(True)
        self.campo_usuario.setText(usuario)
        self.campo_usuario.blockSignals(False)
        self._validar()

    def _validar(self):
        nome = self.campo_nome.text().strip()
        usuario = self.campo_usuario.text().strip()
        senha = self.campo_senha.text()
        confirmar = self.campo_confirmar.text()

        erro = ""
        ok = True

        if not nome:
            ok = False
        elif not usuario:
            ok = False
        elif not usuario[0].isalpha():
            erro = "O nome de usuário deve começar com uma letra."
            ok = False
        elif len(senha) < 6:
            if senha:
                erro = "A senha deve ter pelo menos 6 caracteres."
            ok = False
        elif senha != confirmar:
            if confirmar:
                erro = "As senhas não coincidem."
            ok = False

        # Força da senha
        forca = ""
        if senha:
            pts = sum([len(senha) >= 8, any(c.isupper() for c in senha),
                       any(c.isdigit() for c in senha),
                       any(c in '!@#$%^&*' for c in senha)])
            cores = [NEG, AMBER, AMBER, GREEN, GREEN]
            nomes = ["", "Fraca", "Razoável", "Boa", "Forte"]
            forca = f"Força da senha: <span style='color:{cores[pts]}'>{nomes[pts]}</span>"

        self.lbl_forca.setText(forca)
        self.lbl_erro.setText(erro)
        self.valido_changed.emit(ok)

    def get_dados(self):
        return {
            'nome':      self.campo_nome.text().strip(),
            'usuario':   self.campo_usuario.text().strip(),
            'senha':     self.campo_senha.text(),
            'autologin': self.chk_autologin.isChecked()
        }

    def is_valido(self):
        dados = self.get_dados()
        return (dados['nome'] and dados['usuario'] and
                len(dados['senha']) >= 6 and
                dados['senha'] == self.campo_confirmar.text())


class TelaResumo(QWidget):
    def __init__(self, tela_disco, tela_usuario):
        super().__init__()
        self.tela_disco = tela_disco
        self.tela_usuario = tela_usuario

        self.layout_principal = QVBoxLayout(self)
        self.layout_principal.setContentsMargins(60, 50, 60, 40)
        self.layout_principal.setSpacing(0)

        self.layout_principal.addWidget(_lbl("Tudo pronto para instalar!", size=24, bold=True))
        self.layout_principal.addSpacing(8)
        self.layout_principal.addWidget(_lbl(
            "Confirme os detalhes abaixo e clique em Instalar.", size=14, cor=MUTED))
        self.layout_principal.addSpacing(32)

        self.container = QVBoxLayout()
        self.layout_principal.addLayout(self.container)
        self.layout_principal.addStretch()

        aviso = QFrame()
        aviso.setObjectName("card")
        aviso_l = QHBoxLayout(aviso)
        aviso_l.setContentsMargins(16, 12, 16, 12)
        ic = _lbl("ℹ", size=16, cor=LINK)
        ic.setFixedWidth(24)
        tx = _lbl(
            "Após clicar em Instalar, o processo começará automaticamente.\n"
            "Não desligue o computador durante a instalação.",
            size=12, cor=LINK)
        aviso_l.addWidget(ic)
        aviso_l.addWidget(tx)
        self.layout_principal.addWidget(aviso)

    def atualizar(self):
        # Limpar
        while self.container.count():
            item = self.container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        opcoes_disco = {
            'automatico': 'Instalar automaticamente (disco inteiro)',
            'dualsboot':  'Instalar ao lado do Windows',
            'manual':     'Particionamento personalizado',
        }
        dados = self.tela_usuario.get_dados()
        disco = self.tela_disco.get_opcao()

        for rotulo, valor in [
            ("Instalação",      opcoes_disco.get(disco, disco)),
            ("Nome",            dados['nome']),
            ("Usuário",         dados['usuario']),
            ("Login automático", "Sim" if dados['autologin'] else "Não"),
        ]:
            row = QHBoxLayout()
            lbl_r = _lbl(rotulo, size=13, cor=MUTED)
            lbl_r.setFixedWidth(140)
            lbl_v = _lbl(valor, size=13, bold=True)
            row.addWidget(lbl_r)
            row.addWidget(lbl_v)
            row.addStretch()
            self.container.addLayout(row)
            self.container.addWidget(_sep())
            self.container.addSpacing(4)


class TelaInstalando(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 0, 60, 40)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(0)

        layout.addStretch()

        self.lbl_icone = _lbl("⟳", size=48, cor=GREEN)
        self.lbl_icone.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_icone)

        layout.addSpacing(24)

        self.lbl_titulo = _lbl("Instalando Katu OS…", size=24, bold=True)
        self.lbl_titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_titulo)

        layout.addSpacing(8)

        self.lbl_etapa = _lbl("Preparando o sistema…", size=14, cor=MUTED)
        self.lbl_etapa.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_etapa)

        layout.addSpacing(32)

        self.barra = QProgressBar()
        self.barra.setRange(0, 100)
        self.barra.setValue(0)
        self.barra.setTextVisible(False)
        self.barra.setFixedHeight(6)
        layout.addWidget(self.barra)

        layout.addSpacing(12)

        self.lbl_pct = _lbl("0%", size=12, cor=MUTED)
        self.lbl_pct.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_pct)

        layout.addStretch()

        nota = _lbl("Isso pode levar entre 10 e 30 minutos.\nNão desligue o computador.", size=12, cor=BORDER)
        nota.setAlignment(Qt.AlignCenter)
        layout.addWidget(nota)

    def set_progresso(self, pct, etapa=""):
        self.barra.setValue(pct)
        self.lbl_pct.setText(f"{pct}%")
        if etapa:
            self.lbl_etapa.setText(etapa)


class TelaConcluido(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 0, 60, 40)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(0)
        layout.addStretch()

        ic = _lbl("✓", size=56, cor=GREEN)
        ic.setAlignment(Qt.AlignCenter)
        layout.addWidget(ic)

        layout.addSpacing(24)

        titulo = _lbl("Instalação concluída!", size=28, bold=True)
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        layout.addSpacing(12)

        desc = _lbl(
            "O Katu OS foi instalado com sucesso no seu computador.\n"
            "Remova o pendrive e reinicie para começar a usar.",
            size=15, cor=MUTED
        )
        desc.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc)

        layout.addStretch()


# ─── Janela Principal ────────────────────────────────────────────────────────

class KatuInstalador(QMainWindow):
    PASSOS = ["Boas-vindas", "Verificação", "Disco", "Usuário", "Resumo", "Instalando", "Pronto"]

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Instalador Katu OS")
        self.setMinimumSize(960, 640)
        self.resize(960, 640)
        self.setStyleSheet(STYLE)
        self._passo_atual = 0
        self._calamares_proc = None

        central = QWidget()
        central.setObjectName("central")
        self.setCentralWidget(central)
        raiz = QHBoxLayout(central)
        raiz.setContentsMargins(0, 0, 0, 0)
        raiz.setSpacing(0)

        # ── Sidebar ──────────────────────────────────────────────────────────
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(24, 32, 24, 32)
        sb_layout.setSpacing(0)

        logo = QLabel()
        pix = QPixmap('/usr/share/pixmaps/katu-logo.png')
        if not pix.isNull():
            logo.setPixmap(pix.scaledToWidth(100, Qt.SmoothTransformation))
        else:
            logo.setText("Katu OS")
            logo.setStyleSheet(f"color: {GREEN}; font-size: 18px; font-weight: bold;")
        logo.setAlignment(Qt.AlignLeft)
        sb_layout.addWidget(logo)
        sb_layout.addSpacing(36)

        self._passo_labels = []
        for i, nome in enumerate(self.PASSOS[:-1]):  # excluir "Pronto" da sidebar
            row = QHBoxLayout()
            row.setSpacing(12)
            num = QLabel(str(i + 1))
            num.setFixedSize(28, 28)
            num.setAlignment(Qt.AlignCenter)
            num.setStyleSheet(
                f"border-radius: 14px; background-color: {BORDER}; "
                f"color: {MUTED}; font-size: 12px; font-weight: bold;"
            )
            lbl = QLabel(nome)
            lbl.setStyleSheet(f"color: {MUTED}; font-size: 13px;")
            row.addWidget(num)
            row.addWidget(lbl)
            row.addStretch()
            sb_layout.addLayout(row)
            sb_layout.addSpacing(12)
            self._passo_labels.append((num, lbl))

        sb_layout.addStretch()

        versao = _lbl("Katu OS 1.0", size=11, cor=BORDER)
        sb_layout.addWidget(versao)

        # ── Conteúdo ─────────────────────────────────────────────────────────
        conteudo_wrapper = QFrame()
        conteudo_wrapper.setObjectName("conteudo")
        conteudo_layout = QVBoxLayout(conteudo_wrapper)
        conteudo_layout.setContentsMargins(0, 0, 0, 0)
        conteudo_layout.setSpacing(0)

        self.stack = QStackedWidget()
        self.tela_boas_vindas = TelaBoasVindas()
        self.tela_requisitos  = TelaRequisitos()
        self.tela_disco       = TelaDisco()
        self.tela_usuario     = TelaUsuario()
        self.tela_resumo      = TelaResumo(self.tela_disco, self.tela_usuario)
        self.tela_instalando  = TelaInstalando()
        self.tela_concluido   = TelaConcluido()

        for tela in [self.tela_boas_vindas, self.tela_requisitos, self.tela_disco,
                     self.tela_usuario, self.tela_resumo, self.tela_instalando, self.tela_concluido]:
            self.stack.addWidget(tela)

        conteudo_layout.addWidget(self.stack, 1)

        # Barra de ações
        barra = QFrame()
        barra.setStyleSheet(f"background-color: {BG_ALT}; border-top: 1px solid {BORDER};")
        barra.setFixedHeight(72)
        barra_layout = QHBoxLayout(barra)
        barra_layout.setContentsMargins(40, 0, 40, 0)

        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setObjectName("btn_cancelar")
        self.btn_cancelar.clicked.connect(self.close)

        self.btn_voltar = QPushButton("← Voltar")
        self.btn_voltar.setObjectName("btn_voltar")
        self.btn_voltar.clicked.connect(self._voltar)
        self.btn_voltar.hide()

        self.btn_proximo = QPushButton("Próximo →")
        self.btn_proximo.setObjectName("btn_proximo")
        self.btn_proximo.clicked.connect(self._proximo)

        barra_layout.addWidget(self.btn_cancelar)
        barra_layout.addStretch()
        barra_layout.addWidget(self.btn_voltar)
        barra_layout.addSpacing(12)
        barra_layout.addWidget(self.btn_proximo)

        conteudo_layout.addWidget(barra)

        raiz.addWidget(sidebar)
        raiz.addWidget(conteudo_wrapper, 1)

        # Conectar validação de usuário
        self.tela_usuario.valido_changed.connect(self._ao_validar_usuario)

        self._atualizar_sidebar()
        self._atualizar_botoes()

    def _atualizar_sidebar(self):
        for i, (num, lbl) in enumerate(self._passo_labels):
            if i < self._passo_atual:
                num.setStyleSheet(
                    f"border-radius: 14px; background-color: {GREEN}; "
                    f"color: {BG}; font-size: 12px; font-weight: bold;")
                num.setText("✓")
                lbl.setStyleSheet(f"color: {MUTED}; font-size: 13px;")
            elif i == self._passo_atual:
                num.setStyleSheet(
                    f"border-radius: 14px; background-color: {GREEN}; "
                    f"color: {BG}; font-size: 14px; font-weight: bold;")
                num.setText(str(i + 1))
                lbl.setStyleSheet(f"color: {TEXT}; font-size: 13px; font-weight: bold;")
            else:
                num.setStyleSheet(
                    f"border-radius: 14px; background-color: {BORDER}; "
                    f"color: {MUTED}; font-size: 12px; font-weight: bold;")
                num.setText(str(i + 1))
                lbl.setStyleSheet(f"color: {MUTED}; font-size: 13px;")

    def _atualizar_botoes(self):
        passo = self._passo_atual
        self.btn_voltar.setVisible(0 < passo < 5)
        self.btn_cancelar.setVisible(passo < 5)

        if passo == 0:
            self.btn_proximo.setText("Começar  →")
        elif passo == 4:
            self.btn_proximo.setText("🚀  Instalar agora!")
        elif passo == 6:
            self.btn_proximo.setText("↺  Reiniciar agora")
        else:
            self.btn_proximo.setText("Próximo  →")

        if passo == 3:
            self.btn_proximo.setEnabled(self.tela_usuario.is_valido())
        else:
            self.btn_proximo.setEnabled(True)

    def _ao_validar_usuario(self, valido):
        if self._passo_atual == 3:
            self.btn_proximo.setEnabled(valido)

    def _proximo(self):
        passo = self._passo_atual

        if passo == 4:  # Confirmar → instalar
            self._iniciar_instalacao()
            return
        if passo == 5:  # Aguardar instalação
            return
        if passo == 6:  # Reiniciar
            subprocess.Popen(['shutdown', '-r', 'now'])
            return

        if passo == 4:
            self.tela_resumo.atualizar()

        self._passo_atual += 1

        if self._passo_atual == 4:
            self.tela_resumo.atualizar()

        self.stack.setCurrentIndex(self._passo_atual)
        self._atualizar_sidebar()
        self._atualizar_botoes()

    def _voltar(self):
        if self._passo_atual > 0:
            self._passo_atual -= 1
            self.stack.setCurrentIndex(self._passo_atual)
            self._atualizar_sidebar()
            self._atualizar_botoes()

    def _iniciar_instalacao(self):
        self._passo_atual = 5
        self.stack.setCurrentIndex(5)
        self._atualizar_sidebar()
        self._atualizar_botoes()
        self.btn_proximo.setEnabled(False)
        self.btn_voltar.hide()
        self.btn_cancelar.hide()

        # Lançar Calamares
        opcao = self.tela_disco.get_opcao()
        dados = self.tela_usuario.get_dados()

        # Calamares lê configurações de /etc/calamares/ — apenas lançar
        try:
            self._calamares_proc = subprocess.Popen(
                ['pkexec', 'calamares', '-D', '8'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
        except FileNotFoundError:
            self.tela_instalando.lbl_etapa.setText(
                "Calamares não encontrado. Certifique-se de estar no ambiente live.")
            return

        # Timer para feedback visual enquanto Calamares roda
        self._prog = 0
        self._timer = QTimer()
        self._timer.timeout.connect(self._tick_progresso)
        self._timer.start(800)

    def _tick_progresso(self):
        etapas = [
            (10,  "Preparando o sistema de arquivos…"),
            (20,  "Copiando arquivos do sistema…"),
            (45,  "Instalando arquivos (pode demorar alguns minutos)…"),
            (60,  "Configurando idioma e teclado…"),
            (70,  "Configurando o usuário…"),
            (80,  "Instalando o gerenciador de inicialização…"),
            (90,  "Ajustes finais…"),
            (98,  "Finalizando…"),
        ]

        if self._calamares_proc and self._calamares_proc.poll() is not None:
            self._timer.stop()
            if self._calamares_proc.returncode == 0:
                self._prog = 100
                self.tela_instalando.set_progresso(100, "Instalação concluída!")
                QTimer.singleShot(1500, self._ao_concluir)
            else:
                self.tela_instalando.lbl_etapa.setText(
                    "Ocorreu um erro durante a instalação. Verifique os logs do Calamares.")
            return

        for limite, texto in etapas:
            if self._prog < limite:
                self._prog = min(self._prog + 2, limite)
                self.tela_instalando.set_progresso(self._prog, texto)
                break

    def _ao_concluir(self):
        self._passo_atual = 6
        self.stack.setCurrentIndex(6)
        self._atualizar_sidebar()
        self.btn_proximo.setEnabled(True)
        self.btn_proximo.setText("↺  Reiniciar agora")
        self.btn_cancelar.hide()
        self.btn_voltar.hide()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Katu Instalador")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Katu OS")

    w = KatuInstalador()
    w.show()

    sys.exit(app.exec_() if QT == 'PyQt5' else app.exec())


if __name__ == '__main__':
    main()
