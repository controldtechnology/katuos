#!/usr/bin/env python3
"""
Katu IA — Hub de Inteligência Artificial para Desenvolvedores
Suporta: Claude (Anthropic), GPT-4 (OpenAI), Gemini (Google), Ollama (local)
"""

import sys, os, json, subprocess, threading, shutil
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

# ── Paleta ───────────────────────────────────────────────────────────────────
BG      = "#0d1117"; BG_ALT = "#161b22"; BG_CARD = "#1c2128"
BORDER  = "#30363d"; GREEN  = "#00c853"; GREEN_H = "#00e676"
AMBER   = "#ffab00"; TEXT   = "#e6edf3"; MUTED   = "#8b949e"
NEG     = "#f85149"; LINK   = "#58a6ff"; PURPLE  = "#bc8cff"

CONF_DIR  = Path.home() / ".config" / "katu" / "ai"
CONF_FILE = CONF_DIR / "config.json"

STYLE = f"""
* {{ font-family: 'Noto Sans','Liberation Sans',sans-serif; font-size:13px; color:{TEXT}; }}
QMainWindow,QWidget#root {{ background:{BG}; }}
QWidget {{ background:transparent; }}
QTabWidget::pane {{ border:1px solid {BORDER}; border-radius:8px; background:{BG_ALT}; }}
QTabBar::tab {{
    background:{BG}; color:{MUTED}; padding:10px 22px;
    border-bottom:2px solid transparent; font-size:13px;
}}
QTabBar::tab:selected {{ color:{GREEN}; border-bottom:2px solid {GREEN}; font-weight:bold; }}
QTabBar::tab:hover {{ color:{TEXT}; }}
QTextEdit,QPlainTextEdit {{
    background:{BG_CARD}; border:1px solid {BORDER}; border-radius:8px;
    padding:12px; color:{TEXT}; font-size:13px; line-height:1.6;
    selection-background-color:{GREEN}; selection-color:{BG};
}}
QLineEdit {{
    background:{BG_ALT}; border:1px solid {BORDER}; border-radius:8px;
    padding:10px 14px; color:{TEXT};
}}
QLineEdit:focus {{ border-color:{GREEN}; border-width:2px; }}
QPushButton#verde {{
    background:{GREEN}; color:{BG}; border:none; border-radius:8px;
    padding:10px 24px; font-weight:bold;
}}
QPushButton#verde:hover {{ background:{GREEN_H}; }}
QPushButton#verde:disabled {{ background:{BORDER}; color:{MUTED}; }}
QPushButton#outline {{
    background:transparent; color:{MUTED}; border:1px solid {BORDER};
    border-radius:8px; padding:10px 20px;
}}
QPushButton#outline:hover {{ border-color:{TEXT}; color:{TEXT}; }}
QPushButton#chip {{
    background:{BG_CARD}; color:{MUTED}; border:1px solid {BORDER};
    border-radius:16px; padding:6px 14px; font-size:12px;
}}
QPushButton#chip:hover {{ border-color:{GREEN}; color:{GREEN}; }}
QComboBox {{
    background:{BG_ALT}; border:1px solid {BORDER}; border-radius:8px;
    padding:8px 14px; color:{TEXT};
}}
QComboBox::drop-down {{ border:none; padding-right:10px; }}
QComboBox QAbstractItemView {{ background:{BG_CARD}; border:1px solid {BORDER}; color:{TEXT}; }}
QScrollBar:vertical {{
    background:{BG}; width:6px; border-radius:3px;
}}
QScrollBar::handle:vertical {{ background:{BORDER}; border-radius:3px; min-height:30px; }}
QScrollBar::handle:vertical:hover {{ background:{MUTED}; }}
QScrollBar::add-line,QScrollBar::sub-line {{ height:0; }}
QSplitter::handle {{ background:{BORDER}; width:1px; }}
QListWidget {{
    background:{BG_CARD}; border:1px solid {BORDER}; border-radius:8px;
    padding:4px;
}}
QListWidget::item {{ padding:10px 14px; border-radius:6px; color:{MUTED}; }}
QListWidget::item:selected {{ background:{BG_ALT}; color:{TEXT}; border-left:3px solid {GREEN}; }}
QListWidget::item:hover {{ background:{BG_ALT}; color:{TEXT}; }}
"""

# ── Config ───────────────────────────────────────────────────────────────────
def carregar_config():
    CONF_DIR.mkdir(parents=True, exist_ok=True)
    if CONF_FILE.exists():
        try:
            return json.loads(CONF_FILE.read_text())
        except Exception:
            pass
    return {
        "provider":   "claude",
        "claude_key": "",
        "openai_key": "",
        "gemini_key": "",
        "ollama_url": "http://localhost:11434",
        "modelo":     {"claude":"claude-sonnet-4-6","openai":"gpt-4o","gemini":"gemini-1.5-pro","ollama":"llama3"},
        "temperatura": 0.7,
        "historico":  []
    }

def salvar_config(cfg):
    CONF_DIR.mkdir(parents=True, exist_ok=True)
    CONF_FILE.write_text(json.dumps(cfg, indent=2, ensure_ascii=False))

# ── Prompts de desenvolvedor ─────────────────────────────────────────────────
PROMPTS = {
    "🐛  Corrigir bug": {
        "desc": "Analisa e corrige um trecho de código com bug.",
        "template": "Analise o código abaixo, identifique o bug e forneça a versão corrigida com explicação em português:\n\n```\n{codigo}\n```"
    },
    "📖  Explicar código": {
        "desc": "Explica o que um trecho de código faz em linguagem simples.",
        "template": "Explique o que o seguinte código faz em português simples, linha por linha se necessário:\n\n```\n{codigo}\n```"
    },
    "✍️  Gerar código": {
        "desc": "Gera código a partir de uma descrição em português.",
        "template": "Escreva o código para: {descricao}\n\nUse boas práticas, adicione comentários explicativos em português e trate erros possíveis."
    },
    "🔄  Refatorar": {
        "desc": "Melhora a qualidade e legibilidade do código.",
        "template": "Refatore o código abaixo melhorando: legibilidade, performance, nomes de variáveis e estrutura. Explique as mudanças em português:\n\n```\n{codigo}\n```"
    },
    "🧪  Gerar testes": {
        "desc": "Cria testes unitários para uma função ou classe.",
        "template": "Crie testes unitários completos para o seguinte código. Use o framework de testes padrão da linguagem. Explique cada teste em português:\n\n```\n{codigo}\n```"
    },
    "📚  Documentar": {
        "desc": "Adiciona docstrings e comentários ao código.",
        "template": "Adicione documentação completa ao código abaixo: docstrings, parâmetros, retornos e exemplos de uso. Em português:\n\n```\n{codigo}\n```"
    },
    "🔒  Revisar segurança": {
        "desc": "Identifica vulnerabilidades de segurança no código.",
        "template": "Revise o código abaixo procurando vulnerabilidades de segurança (injection, XSS, buffer overflow, etc.). Liste os problemas e soluções em português:\n\n```\n{codigo}\n```"
    },
    "🗄️  SQL helper": {
        "desc": "Escreve e otimiza queries SQL.",
        "template": "Escreva uma query SQL para: {descricao}\n\nOtimize a query e explique o que cada parte faz em português. Informe o banco de dados se relevante."
    },
    "🌐  API REST": {
        "desc": "Design e implementação de endpoints REST.",
        "template": "Crie um endpoint REST para: {descricao}\n\nInclua: rota, método HTTP, validação, tratamento de erros, exemplo de request/response e código de implementação."
    },
    "🐳  Docker/DevOps": {
        "desc": "Gera Dockerfiles, docker-compose e configurações DevOps.",
        "template": "Crie a configuração Docker/DevOps para: {descricao}\n\nInclua Dockerfile otimizado, docker-compose.yml se necessário, e explique cada configuração em português."
    },
    "⚡  Terminal/Shell": {
        "desc": "Comandos bash, scripts e automações de terminal.",
        "template": "Escreva um script bash para: {descricao}\n\nUse boas práticas de shell scripting, tratamento de erros com set -e, e adicione comentários em português."
    },
    "🤖  Git helper": {
        "desc": "Mensagens de commit, estratégias de branch e workflow Git.",
        "template": "Ajude com Git: {descricao}\n\nForneça comandos exatos, explique cada passo em português e sugira boas práticas de versionamento."
    },
}

# ── Thread de chamada à IA ───────────────────────────────────────────────────
class IAThread(QThread):
    resposta_chunk = pyqtSignal(str)
    resposta_fim   = pyqtSignal()
    erro           = pyqtSignal(str)

    def __init__(self, cfg, mensagens):
        super().__init__()
        self.cfg       = cfg
        self.mensagens = mensagens

    def run(self):
        provider = self.cfg.get("provider", "claude")
        try:
            if provider == "claude":
                self._claude()
            elif provider == "openai":
                self._openai()
            elif provider == "gemini":
                self._gemini()
            elif provider == "ollama":
                self._ollama()
        except ImportError as e:
            self.erro.emit(f"Biblioteca não instalada: {e}\nInstale com: pip3 install anthropic openai google-generativeai")
        except Exception as e:
            self.erro.emit(f"Erro: {e}")

    def _claude(self):
        import anthropic
        chave = self.cfg.get("claude_key", "") or os.environ.get("ANTHROPIC_API_KEY", "")
        if not chave:
            self.erro.emit("Chave da API Anthropic não configurada.\nVá em Configurações → Chaves de API.")
            return
        client = anthropic.Anthropic(api_key=chave)
        modelo = self.cfg.get("modelo", {}).get("claude", "claude-sonnet-4-6")
        with client.messages.stream(
            model=modelo, max_tokens=4096,
            messages=self.mensagens,
            system="Você é um assistente de programação especializado. Responda sempre em português do Brasil. Seja preciso, use exemplos de código quando útil e explique conceitos de forma clara."
        ) as stream:
            for texto in stream.text_stream:
                self.resposta_chunk.emit(texto)
        self.resposta_fim.emit()

    def _openai(self):
        from openai import OpenAI
        chave = self.cfg.get("openai_key", "") or os.environ.get("OPENAI_API_KEY", "")
        if not chave:
            self.erro.emit("Chave da API OpenAI não configurada.")
            return
        client = OpenAI(api_key=chave)
        modelo = self.cfg.get("modelo", {}).get("openai", "gpt-4o")
        msgs = [{"role":"system","content":"Você é um assistente de programação. Responda em português do Brasil."}]
        msgs += self.mensagens
        stream = client.chat.completions.create(model=modelo, messages=msgs, stream=True, max_tokens=4096)
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                self.resposta_chunk.emit(delta)
        self.resposta_fim.emit()

    def _gemini(self):
        import google.generativeai as genai
        chave = self.cfg.get("gemini_key", "") or os.environ.get("GOOGLE_API_KEY", "")
        if not chave:
            self.erro.emit("Chave da API Google Gemini não configurada.")
            return
        genai.configure(api_key=chave)
        modelo = self.cfg.get("modelo", {}).get("gemini", "gemini-1.5-pro")
        m = genai.GenerativeModel(modelo, system_instruction="Você é um assistente de programação. Responda em português do Brasil.")
        chat = m.start_chat()
        texto_completo = " ".join(
            msg["content"] for msg in self.mensagens if msg["role"] == "user"
        )
        response = chat.send_message(texto_completo, stream=True)
        for chunk in response:
            if chunk.text:
                self.resposta_chunk.emit(chunk.text)
        self.resposta_fim.emit()

    def _ollama(self):
        import urllib.request, json as js
        url = self.cfg.get("ollama_url", "http://localhost:11434") + "/api/chat"
        modelo = self.cfg.get("modelo", {}).get("ollama", "llama3")
        payload = js.dumps({
            "model": modelo, "stream": True,
            "messages": [{"role":"system","content":"Responda em português do Brasil."}] + self.mensagens
        }).encode()
        req = urllib.request.Request(url, data=payload, headers={"Content-Type":"application/json"})
        with urllib.request.urlopen(req, timeout=120) as resp:
            for linha in resp:
                obj = js.loads(linha.decode())
                if obj.get("message", {}).get("content"):
                    self.resposta_chunk.emit(obj["message"]["content"])
                if obj.get("done"):
                    break
        self.resposta_fim.emit()


# ── Widgets auxiliares ───────────────────────────────────────────────────────
def _lbl(t, size=13, bold=False, cor=TEXT):
    l = QLabel(t); f = QFont()
    f.setPointSize(size)
    if bold: f.setWeight(QFont.Bold)
    l.setFont(f); l.setStyleSheet(f"color:{cor};background:transparent;")
    l.setWordWrap(True)
    return l

def _sep():
    f = QFrame(); f.setFrameShape(QFrame.HLine)
    f.setStyleSheet(f"background:{BORDER};max-height:1px;border:none;"); return f

def _btn(texto, obj="verde"):
    b = QPushButton(texto); b.setObjectName(obj); b.setCursor(Qt.PointingHandCursor); return b


# ── Aba Chat ─────────────────────────────────────────────────────────────────
class AbaChat(QWidget):
    def __init__(self, cfg_ref):
        super().__init__()
        self.cfg = cfg_ref
        self.historico = []
        self._resposta_atual = ""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        # Barra superior
        barra = QHBoxLayout()
        self.combo_provider = QComboBox()
        self.combo_provider.addItems(["Claude (Anthropic)", "GPT-4 (OpenAI)", "Gemini (Google)", "Ollama (Local)"])
        mapa = {"claude":0,"openai":1,"gemini":2,"ollama":3}
        self.combo_provider.setCurrentIndex(mapa.get(self.cfg.get("provider","claude"), 0))
        self.combo_provider.currentIndexChanged.connect(self._mudar_provider)
        self.combo_provider.setFixedWidth(220)

        btn_limpar = _btn("Limpar conversa", "outline")
        btn_limpar.clicked.connect(self._limpar)

        barra.addWidget(_lbl("Conversar com:", 12, cor=MUTED))
        barra.addWidget(self.combo_provider)
        barra.addStretch()
        barra.addWidget(btn_limpar)
        layout.addLayout(barra)

        # Histórico de mensagens
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setPlaceholderText("A conversa aparecerá aqui…")
        layout.addWidget(self.chat_display, 1)

        # Campo de entrada
        entrada_layout = QVBoxLayout()
        entrada_layout.setSpacing(8)

        self.campo_entrada = QPlainTextEdit()
        self.campo_entrada.setPlaceholderText("Digite sua mensagem… (Ctrl+Enter para enviar)")
        self.campo_entrada.setFixedHeight(100)
        self.campo_entrada.installEventFilter(self)

        rodape = QHBoxLayout()
        self.lbl_status = _lbl("", 11, cor=MUTED)
        btn_enviar = _btn("Enviar  ⏎", "verde")
        btn_enviar.setFixedWidth(140)
        btn_enviar.clicked.connect(self._enviar)

        rodape.addWidget(self.lbl_status)
        rodape.addStretch()
        rodape.addWidget(btn_enviar)

        entrada_layout.addWidget(self.campo_entrada)
        entrada_layout.addLayout(rodape)
        layout.addLayout(entrada_layout)

    def eventFilter(self, obj, event):
        from PyQt5.QtCore import QEvent
        from PyQt5.QtGui import QKeySequence
        if obj == self.campo_entrada and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Return and event.modifiers() == Qt.ControlModifier:
                self._enviar()
                return True
        return super().eventFilter(obj, event)

    def _mudar_provider(self, idx):
        mapa = {0:"claude", 1:"openai", 2:"gemini", 3:"ollama"}
        self.cfg["provider"] = mapa[idx]
        salvar_config(self.cfg)

    def _limpar(self):
        self.historico = []
        self.chat_display.clear()

    def _adicionar_msg(self, role, texto):
        cores = {"user": GREEN, "assistant": LINK, "erro": NEG}
        nomes = {"user": "Você", "assistant": "IA", "erro": "Erro"}
        cor = cores.get(role, MUTED)
        nome = nomes.get(role, role)
        html = (f'<p style="margin:8px 0 4px;">'
                f'<span style="color:{cor};font-weight:bold;">{nome}</span>'
                f'</p>'
                f'<p style="margin:0 0 16px;color:{TEXT};white-space:pre-wrap;">{texto}</p>')
        cursor = self.chat_display.textCursor()
        cursor.movePosition(cursor.End)
        self.chat_display.setTextCursor(cursor)
        self.chat_display.insertHtml(html)
        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum())

    def _enviar(self):
        texto = self.campo_entrada.toPlainText().strip()
        if not texto:
            return
        self.campo_entrada.clear()
        self.historico.append({"role": "user", "content": texto})
        self._adicionar_msg("user", texto)

        self.lbl_status.setText("⟳  Aguardando resposta…")
        self.lbl_status.setStyleSheet(f"color:{AMBER};")
        self._resposta_atual = ""

        self._thread = IAThread(self.cfg, self.historico.copy())
        self._thread.resposta_chunk.connect(self._ao_receber_chunk)
        self._thread.resposta_fim.connect(self._ao_finalizar)
        self._thread.erro.connect(self._ao_erro)
        self._thread.start()

    def _ao_receber_chunk(self, chunk):
        if not self._resposta_atual:
            self.chat_display.insertHtml(
                f'<p style="margin:8px 0 4px;"><span style="color:{LINK};font-weight:bold;">IA</span></p>'
                f'<p style="margin:0 0 16px;color:{TEXT};white-space:pre-wrap;" id="ia_resp">')
        self._resposta_atual += chunk
        cursor = self.chat_display.textCursor()
        cursor.movePosition(cursor.End)
        self.chat_display.setTextCursor(cursor)
        self.chat_display.insertPlainText(chunk)
        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum())

    def _ao_finalizar(self):
        self.historico.append({"role": "assistant", "content": self._resposta_atual})
        self._resposta_atual = ""
        self.lbl_status.setText("✓  Resposta recebida")
        self.lbl_status.setStyleSheet(f"color:{GREEN};")
        self.chat_display.insertHtml("</p>")

    def _ao_erro(self, msg):
        self._adicionar_msg("erro", msg)
        self.lbl_status.setText("✗  Erro")
        self.lbl_status.setStyleSheet(f"color:{NEG};")

    def inserir_prompt(self, texto):
        self.campo_entrada.setPlainText(texto)
        self.campo_entrada.setFocus()


# ── Aba Prompts ──────────────────────────────────────────────────────────────
class AbaPrompts(QWidget):
    usar_prompt = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Lista de categorias
        self.lista = QListWidget()
        self.lista.setFixedWidth(260)
        for nome in PROMPTS:
            self.lista.addItem(nome)
        self.lista.setStyleSheet(f"QListWidget{{border-right:1px solid {BORDER};border-radius:0;}}")
        self.lista.currentRowChanged.connect(self._ao_selecionar)
        layout.addWidget(self.lista)

        # Painel direito
        painel = QWidget()
        painel.setStyleSheet(f"background:{BG_ALT};")
        painel_layout = QVBoxLayout(painel)
        painel_layout.setContentsMargins(32, 28, 32, 28)
        painel_layout.setSpacing(16)

        self.lbl_titulo  = _lbl("Selecione um prompt", 18, bold=True)
        self.lbl_desc    = _lbl("", 13, cor=MUTED)
        self.txt_preview = QTextEdit()
        self.txt_preview.setReadOnly(False)
        self.txt_preview.setPlaceholderText("Preencha os campos marcados com {chaves} e clique em Usar Prompt")

        rodape = QHBoxLayout()
        self.lbl_dica = _lbl("Edite o template conforme necessário antes de enviar", 11, cor=MUTED)
        self.btn_usar = _btn("Usar este prompt  →", "verde")
        self.btn_usar.clicked.connect(self._usar)
        self.btn_usar.setEnabled(False)
        rodape.addWidget(self.lbl_dica)
        rodape.addStretch()
        rodape.addWidget(self.btn_usar)

        painel_layout.addWidget(self.lbl_titulo)
        painel_layout.addWidget(self.lbl_desc)
        painel_layout.addWidget(_sep())
        painel_layout.addWidget(self.txt_preview, 1)
        painel_layout.addLayout(rodape)
        layout.addWidget(painel, 1)

        # Selecionar primeiro
        self.lista.setCurrentRow(0)

    def _ao_selecionar(self, idx):
        if idx < 0:
            return
        nome = self.lista.item(idx).text()
        p = PROMPTS[nome]
        self.lbl_titulo.setText(nome)
        self.lbl_desc.setText(p["desc"])
        self.txt_preview.setPlainText(p["template"])
        self.btn_usar.setEnabled(True)

    def _usar(self):
        self.usar_prompt.emit(self.txt_preview.toPlainText())


# ── Aba Configurações ────────────────────────────────────────────────────────
class AbaConfig(QWidget):
    config_salva = pyqtSignal()

    def __init__(self, cfg_ref):
        super().__init__()
        self.cfg = cfg_ref
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(20)

        layout.addWidget(_lbl("Chaves de API", 18, bold=True))
        layout.addWidget(_lbl(
            "Suas chaves ficam salvas apenas no seu computador (~/.config/katu/ai/config.json).",
            12, cor=MUTED))
        layout.addWidget(_sep())

        def campo_chave(rotulo, chave_cfg, placeholder, link=""):
            box = QVBoxLayout(); box.setSpacing(6)
            row = QHBoxLayout()
            row.addWidget(_lbl(rotulo, 13, bold=True))
            if link:
                btn_link = _btn("Obter chave gratuita ↗", "chip")
                btn_link.clicked.connect(lambda: subprocess.Popen(['xdg-open', link]))
                row.addWidget(btn_link)
            row.addStretch()
            box.addLayout(row)
            campo = QLineEdit()
            campo.setEchoMode(QLineEdit.Password)
            campo.setPlaceholderText(placeholder)
            campo.setText(self.cfg.get(chave_cfg, ""))
            campo.textChanged.connect(lambda v, k=chave_cfg: self.cfg.update({k: v}))
            box.addWidget(campo)
            layout.addLayout(box)
            return campo

        campo_chave("Anthropic (Claude)",  "claude_key", "sk-ant-api03-…",   "https://console.anthropic.com/")
        campo_chave("OpenAI (GPT-4)",      "openai_key", "sk-…",              "https://platform.openai.com/api-keys")
        campo_chave("Google (Gemini)",     "gemini_key", "AIza…",             "https://aistudio.google.com/")

        layout.addWidget(_sep())
        layout.addWidget(_lbl("Ollama (IA local — gratuita)", 13, bold=True))
        layout.addWidget(_lbl("Rode modelos como LLaMA3, Mistral e Phi-3 sem internet e sem custo.", 12, cor=MUTED))

        row_ol = QHBoxLayout()
        self.campo_ollama = QLineEdit()
        self.campo_ollama.setText(self.cfg.get("ollama_url", "http://localhost:11434"))
        self.campo_ollama.textChanged.connect(lambda v: self.cfg.update({"ollama_url": v}))
        btn_instalar = _btn("Instalar Ollama", "chip")
        btn_instalar.clicked.connect(lambda: subprocess.Popen(['xdg-open', 'https://ollama.com']))
        row_ol.addWidget(self.campo_ollama)
        row_ol.addWidget(btn_instalar)
        layout.addLayout(row_ol)

        layout.addStretch()

        btn_salvar = _btn("Salvar configurações", "verde")
        btn_salvar.setFixedWidth(200)
        btn_salvar.clicked.connect(self._salvar)
        self.lbl_ok = _lbl("", 12, cor=GREEN)
        row_save = QHBoxLayout()
        row_save.addStretch()
        row_save.addWidget(self.lbl_ok)
        row_save.addWidget(btn_salvar)
        layout.addLayout(row_save)

    def _salvar(self):
        salvar_config(self.cfg)
        self.lbl_ok.setText("✓  Salvo!")
        QTimer.singleShot(2500, lambda: self.lbl_ok.setText(""))
        self.config_salva.emit()


# ── Aba Terminal IA ──────────────────────────────────────────────────────────
class AbaTerminal(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        layout.addWidget(_lbl("Terminal IA", 18, bold=True))
        layout.addWidget(_lbl("Comandos de IA disponíveis no terminal do sistema.", 13, cor=MUTED))
        layout.addWidget(_sep())

        cmds = [
            ("ai  'sua pergunta'",       "Faz uma pergunta direta à IA configurada"),
            ("ai-fix",                   "Explica e corrige o último erro do terminal"),
            ("ai-explain <comando>",     "Explica o que um comando faz"),
            ("ai-code  'descrição'",     "Gera código a partir de uma descrição"),
            ("ai-review <arquivo>",      "Revisa um arquivo de código"),
            ("ai-commit",                "Gera mensagem de commit para as mudanças do git"),
            ("ai-sql  'descrição'",      "Cria query SQL a partir de uma descrição"),
            ("ai-doc  <arquivo>",        "Gera documentação para um arquivo"),
            ("ai-translate <arquivo>",   "Traduz comentários do código para português"),
            ("katu-ia",                  "Abre este hub visual"),
        ]

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        conteudo = QWidget()
        grid = QVBoxLayout(conteudo)
        grid.setSpacing(6)

        for cmd, desc in cmds:
            card = QFrame()
            card.setObjectName("card")
            card.setFixedHeight(52)
            card_l = QHBoxLayout(card)
            card_l.setContentsMargins(16, 0, 16, 0)
            lbl_cmd = QLabel(f"<code style='color:{GREEN};background:{BG};padding:2px 6px;border-radius:4px;font-size:13px;'>{cmd}</code>")
            lbl_cmd.setFixedWidth(260)
            lbl_cmd.setTextFormat(Qt.RichText)
            lbl_desc = _lbl(desc, 12, cor=MUTED)
            card_l.addWidget(lbl_cmd)
            card_l.addWidget(lbl_desc)
            grid.addWidget(card)

        scroll.setWidget(conteudo)
        layout.addWidget(scroll, 1)

        layout.addWidget(_sep())

        btn_abrir = _btn("Abrir Konsole com ambiente IA", "verde")
        btn_abrir.clicked.connect(lambda: subprocess.Popen(['konsole', '--noclose', '-e',
            'bash', '--rcfile', str(CONF_DIR / 'shell_ia.sh')]))
        layout.addWidget(btn_abrir, 0, Qt.AlignRight)


# ── Janela Principal ─────────────────────────────────────────────────────────
class KatuIA(QMainWindow):
    def __init__(self):
        super().__init__()
        self.cfg = carregar_config()
        self.setWindowTitle("Katu IA — Hub de Inteligência Artificial")
        self.setMinimumSize(1100, 720)
        self.resize(1200, 780)
        self.setStyleSheet(STYLE)

        central = QWidget(); central.setObjectName("root")
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Cabeçalho
        header = QFrame()
        header.setStyleSheet(f"background:{BG_ALT};border-bottom:1px solid {BORDER};")
        header.setFixedHeight(56)
        header_l = QHBoxLayout(header)
        header_l.setContentsMargins(24, 0, 24, 0)
        lbl_titulo = _lbl("Katu IA", 16, bold=True, cor=GREEN)
        lbl_sub    = _lbl("Hub de Inteligência Artificial para Desenvolvedores", 12, cor=MUTED)
        header_l.addWidget(lbl_titulo)
        header_l.addSpacing(12)
        header_l.addWidget(lbl_sub)
        header_l.addStretch()
        layout.addWidget(header)

        # Abas
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        layout.addWidget(self.tabs, 1)

        self.aba_chat     = AbaChat(self.cfg)
        self.aba_prompts  = AbaPrompts()
        self.aba_terminal = AbaTerminal()
        self.aba_config   = AbaConfig(self.cfg)

        self.tabs.addTab(self.aba_chat,     "💬  Chat")
        self.tabs.addTab(self.aba_prompts,  "📋  Prompts")
        self.tabs.addTab(self.aba_terminal, "⌨️   Terminal")
        self.tabs.addTab(self.aba_config,   "⚙️   Configurações")

        self.aba_prompts.usar_prompt.connect(self._usar_prompt)

    def _usar_prompt(self, texto):
        self.tabs.setCurrentIndex(0)
        self.aba_chat.inserir_prompt(texto)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Katu IA")
    app.setApplicationVersion("1.0")
    w = KatuIA()
    w.show()
    sys.exit(app.exec_() if QT == 'PyQt5' else app.exec())

if __name__ == '__main__':
    main()
