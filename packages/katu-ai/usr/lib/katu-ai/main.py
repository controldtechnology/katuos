#!/usr/bin/env python3
"""
Katu AI — Assistente de Inteligência Artificial
Para todos os usuários do Katu OS.
Suporta: Katu (futuro), OpenAI, Claude (Anthropic), Gemini, Local (Ollama)

SEGURANÇA:
- Nenhuma resposta de IA é executada como comando shell.
- Todas as ações passam pelo Action Registry.
- Chaves armazenadas em ~/.config/katu/secrets/ (permissão 600).
- Nenhuma chave é incluída no código, ISO ou git.
"""
import sys, os, json, subprocess, threading, re
from pathlib import Path
from datetime import datetime

try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize, QEvent
    from PyQt5.QtGui import *
    QT = 'PyQt5'
except ImportError:
    from PySide6.QtWidgets import *
    from PySide6.QtCore import Qt, QThread, Signal as pyqtSignal, QTimer, QSize, QEvent
    from PySide6.QtGui import *
    QT = 'PySide6'

sys.path.insert(0, '/usr/lib/python3/dist-packages')
try:
    from katu_core import ui, system
    from katu_core.config import KatuConfig
    from katu_core.secrets import store_secret, get_secret, has_secret, mask_key, delete_secret
    from katu_core.actions import ACTION_REGISTRY, execute_action, list_actions
    CORE = True
except ImportError:
    CORE = False
    class _FakeUI:
        STYLESHEET = ""
        BG = "#0d1117"; SURFACE = "#161b22"; CARD = "#1c2128"
        BORDER = "#30363d"; ACCENT = "#00c853"; ACCENT_H = "#00e676"
        ACCENT_A = "#00a040"; TEXT = "#e6edf3"; MUTED = "#8b949e"
        ERROR = "#f85149"; AMBER = "#ffab00"; SUCCESS = "#3fb950"
        INFO = "#58a6ff"; TEXT_INV = "#0d1117"
    ui = _FakeUI()
    def get_secret(s, k, d=""): return d
    def store_secret(s, k, v): pass
    def has_secret(s, k): return False
    def mask_key(k): return "••••••••"
    def delete_secret(s, k=None): pass
    def list_actions(): return []
    def execute_action(*a, **k): return False

CONF_DIR = Path.home() / ".config" / "katu" / "ai"
HISTORY_FILE = CONF_DIR / "history.json"

# ── Providers ─────────────────────────────────────────────────────────────────
PROVIDERS = {
    "katu":       {"name": "Katu",    "icon": "🐆", "status": "beta",    "color": ui.ACCENT},
    "openai":     {"name": "OpenAI",  "icon": "🟢", "status": "ok",      "color": "#74aa9c"},
    "claude":     {"name": "Claude",  "icon": "🔶", "status": "ok",      "color": "#d97706"},
    "gemini":     {"name": "Gemini",  "icon": "🔷", "status": "ok",      "color": "#4285f4"},
    "local":      {"name": "Local",   "icon": "💻", "status": "opcional", "color": ui.MUTED},
}

# ── Config ────────────────────────────────────────────────────────────────────
def load_config():
    CONF_DIR.mkdir(parents=True, exist_ok=True)
    f = CONF_DIR / "config.json"
    defaults = {
        "provider": "openai",
        "model": {
            "openai": "gpt-4o",
            "claude": "claude-sonnet-4-6",
            "gemini": "gemini-1.5-pro",
            "local":  "llama3",
        },
        "save_history": True,
        "system_context": True,
        "temperature": 0.7,
    }
    if f.exists():
        try:
            saved = json.loads(f.read_text())
            defaults.update(saved)
        except Exception:
            pass
    return defaults

def save_config(cfg):
    CONF_DIR.mkdir(parents=True, exist_ok=True)
    f = CONF_DIR / "config.json"
    f.write_text(json.dumps(cfg, indent=2, ensure_ascii=False))

def load_history():
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text())
        except Exception:
            pass
    return []

def save_history(hist):
    CONF_DIR.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(json.dumps(hist[-200:], indent=2, ensure_ascii=False))

# ── System Context ────────────────────────────────────────────────────────────
def get_system_context():
    if not CORE:
        return ""
    try:
        os_i = system.get_os_info()
        mem  = system.get_memory_info()
        net  = system.get_network_status()
        disk = system.get_disk_info()
        root_disk = next((d for d in disk if d["mount"] == "/"), {})
        ctx = (
            f"Sistema: Katu OS {os_i.get('version','?')} "
            f"(Debian 13 Trixie, KDE Plasma {os_i.get('plasma','?')})\n"
            f"Kernel: {os_i.get('kernel','?')} | Arq: {os_i.get('arch','?')}\n"
            f"RAM: {mem.get('used_mb',0)//1024:.1f} GB usados / {mem.get('total_mb',0)//1024:.1f} GB total\n"
            f"Disco /: {root_disk.get('used','?')} usados / {root_disk.get('size','?')} total ({root_disk.get('avail','?')} livres)\n"
            f"Rede: {'conectado' if net.get('connected') else 'desconectado'}"
        )
        return ctx
    except Exception:
        return ""

# ── AI Thread ─────────────────────────────────────────────────────────────────
class AIThread(QThread):
    chunk  = pyqtSignal(str)
    done   = pyqtSignal()
    error  = pyqtSignal(str)
    action = pyqtSignal(dict)  # when AI requests an action

    def __init__(self, cfg, messages, provider, model):
        super().__init__()
        self._cfg      = cfg
        self._messages = messages
        self._provider = provider
        self._model    = model
        self._cancel   = False

    def cancel(self):
        self._cancel = True

    def run(self):
        try:
            if self._provider == "openai":
                self._call_openai()
            elif self._provider == "claude":
                self._call_claude()
            elif self._provider == "gemini":
                self._call_gemini()
            elif self._provider == "local":
                self._call_local()
            elif self._provider == "katu":
                self._call_katu()
            else:
                self.error.emit(f"Provedor '{self._provider}' não reconhecido.")
        except Exception as e:
            self.error.emit(str(e))

    def _stream(self, url, headers, payload, extract_fn):
        import urllib.request, urllib.error
        data = json.dumps(payload).encode()
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                for raw in r:
                    if self._cancel:
                        break
                    line = raw.decode("utf-8").strip()
                    if not line or line == "data: [DONE]":
                        continue
                    if line.startswith("data: "):
                        line = line[6:]
                    try:
                        obj = json.loads(line)
                        text = extract_fn(obj)
                        if text:
                            self.chunk.emit(text)
                    except Exception:
                        pass
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="ignore")
            raise Exception(f"HTTP {e.code}: {body[:300]}")
        self.done.emit()

    def _call_openai(self):
        key = get_secret("katu-ai", "openai_key")
        if not key:
            self.error.emit("Chave da API OpenAI não configurada.\n\nVá em Configurações → IA → OpenAI → Configurar.")
            return
        self._stream(
            "https://api.openai.com/v1/chat/completions",
            {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            {"model": self._model, "messages": self._messages, "stream": True, "temperature": self._cfg.get("temperature", 0.7)},
            lambda obj: (obj.get("choices", [{}])[0].get("delta", {}) or {}).get("content", "") or ""
        )

    def _call_claude(self):
        key = get_secret("katu-ai", "claude_key")
        if not key:
            self.error.emit("Chave da API Anthropic não configurada.\n\nVá em Configurações → IA → Claude → Configurar.")
            return
        import urllib.request, urllib.error
        system_msg = next((m["content"] for m in self._messages if m["role"] == "system"), "")
        user_msgs  = [m for m in self._messages if m["role"] != "system"]
        payload = {
            "model": self._model,
            "max_tokens": 4096,
            "stream": True,
            "messages": user_msgs,
        }
        if system_msg:
            payload["system"] = system_msg
        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=data,
            headers={"x-api-key": key, "anthropic-version": "2023-06-01",
                     "content-type": "application/json"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                for raw in r:
                    if self._cancel:
                        break
                    line = raw.decode("utf-8").strip()
                    if not line or not line.startswith("data:"):
                        continue
                    try:
                        obj = json.loads(line[5:].strip())
                        if obj.get("type") == "content_block_delta":
                            text = obj.get("delta", {}).get("text", "")
                            if text:
                                self.chunk.emit(text)
                    except Exception:
                        pass
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="ignore")
            raise Exception(f"HTTP {e.code}: {body[:300]}")
        self.done.emit()

    def _call_gemini(self):
        key = get_secret("katu-ai", "gemini_key")
        if not key:
            self.error.emit("Chave da API Gemini não configurada.\n\nVá em Configurações → IA → Gemini → Configurar.")
            return
        import urllib.request, urllib.error
        contents = []
        for m in self._messages:
            if m["role"] == "system":
                continue
            role = "user" if m["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": m["content"]}]})
        payload = {"contents": contents, "generationConfig": {"temperature": self._cfg.get("temperature", 0.7)}}
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self._model}:streamGenerateContent?key={key}&alt=sse"
        data = json.dumps(payload).encode()
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                for raw in r:
                    if self._cancel:
                        break
                    line = raw.decode("utf-8").strip()
                    if not line or line == "data: [DONE]":
                        continue
                    if line.startswith("data:"):
                        line = line[5:].strip()
                    try:
                        obj = json.loads(line)
                        candidates = obj.get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            for p in parts:
                                text = p.get("text", "")
                                if text:
                                    self.chunk.emit(text)
                    except Exception:
                        pass
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="ignore")
            raise Exception(f"HTTP {e.code}: {body[:300]}")
        self.done.emit()

    def _call_local(self):
        ollama_url = get_secret("katu-ai", "ollama_url") or "http://localhost:11434"
        import urllib.request, urllib.error
        messages = [m for m in self._messages if m["role"] != "system"]
        system_msg = next((m["content"] for m in self._messages if m["role"] == "system"), "")
        payload = {
            "model": self._model,
            "messages": ([{"role": "system", "content": system_msg}] if system_msg else []) + messages,
            "stream": True,
        }
        url = f"{ollama_url}/api/chat"
        data = json.dumps(payload).encode()
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                for raw in r:
                    if self._cancel:
                        break
                    try:
                        obj = json.loads(raw.decode("utf-8").strip())
                        text = obj.get("message", {}).get("content", "")
                        if text:
                            self.chunk.emit(text)
                        if obj.get("done"):
                            break
                    except Exception:
                        pass
        except Exception as e:
            raise Exception(f"Ollama não disponível em {ollama_url}: {e}")
        self.done.emit()

    def _call_katu(self):
        self.chunk.emit(
            "Olá! Sou o Katu, o assistente nativo do Katu OS.\n\n"
            "Atualmente estou em fase beta. Para usar IA completa, "
            "configure um provedor em **Configurações → IA**:\n\n"
            "- **OpenAI** (ChatGPT) — adicione sua chave\n"
            "- **Claude** (Anthropic) — adicione sua chave\n"
            "- **Gemini** (Google) — adicione sua chave\n"
            "- **Local** (Ollama) — instale modelos localmente\n\n"
            "Precisa de ajuda para configurar? Posso guiar você!"
        )
        self.done.emit()


# ── Configuração de Provedor ──────────────────────────────────────────────────
class ProviderConfigDialog(QDialog):
    def __init__(self, provider_id, parent=None):
        super().__init__(parent)
        self._pid = provider_id
        info = PROVIDERS.get(provider_id, {})
        self.setWindowTitle(f"Configurar {info.get('name', provider_id)}")
        self.setMinimumWidth(480)
        self.setModal(True)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 24, 24, 24)
        lay.setSpacing(16)

        title = QLabel(f"{info.get('icon','')} Configurar {info.get('name','')}")
        title.setStyleSheet(f"font-size:18px; font-weight:bold; color:{ui.TEXT};")
        lay.addWidget(title)

        if provider_id == "local":
            self._build_local_config(lay)
        elif provider_id == "katu":
            info_lbl = QLabel("O provedor Katu está em desenvolvimento.\nConfigure outro provedor enquanto isso.")
            info_lbl.setStyleSheet(f"color:{ui.MUTED};")
            lay.addWidget(info_lbl)
        else:
            self._build_api_config(lay, provider_id)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self._save)
        btns.rejected.connect(self.reject)
        lay.addWidget(btns)

    def _build_api_config(self, lay, pid):
        urls = {
            "openai": "https://platform.openai.com/api-keys",
            "claude": "https://console.anthropic.com/",
            "gemini": "https://aistudio.google.com/app/apikey",
        }
        hints = {
            "openai": "sk-...",
            "claude": "sk-ant-...",
            "gemini": "AIzaSy...",
        }
        key_names = {"openai": "openai_key", "claude": "claude_key", "gemini": "gemini_key"}
        key_name = key_names.get(pid, f"{pid}_key")
        current = get_secret("katu-ai", key_name)

        if current:
            status = QLabel(f"✓ Chave configurada: {mask_key(current)}")
            status.setStyleSheet(f"color:{ui.SUCCESS};")
            lay.addWidget(status)

        lbl = QLabel("Chave de API (BYOK — Bring Your Own Key):")
        lbl.setStyleSheet(f"color:{ui.TEXT};")
        self._key_input = QLineEdit()
        self._key_input.setEchoMode(QLineEdit.Password)
        self._key_input.setPlaceholderText(hints.get(pid, "Cole sua chave aqui"))
        lay.addWidget(lbl)
        lay.addWidget(self._key_input)

        note = QLabel(
            "⚠ Sua chave é armazenada localmente em ~/.config/katu/secrets/\n"
            "com permissão 600. Ela nunca é enviada ao Katu OS."
        )
        note.setStyleSheet(f"color:{ui.MUTED}; font-size:12px;")
        lay.addWidget(note)

        if pid in urls:
            link_btn = QPushButton(f"Obter chave em {urls[pid].split('/')[2]}")
            link_btn.setObjectName("outline")
            link_btn.clicked.connect(lambda: subprocess.Popen(["xdg-open", urls[pid]]))
            lay.addWidget(link_btn)

        if current:
            remove_btn = QPushButton("Remover chave")
            remove_btn.setObjectName("danger")
            remove_btn.clicked.connect(lambda: (delete_secret("katu-ai", key_name), self.accept()))
            lay.addWidget(remove_btn)

        self._key_name = key_name

    def _build_local_config(self, lay):
        current_url = get_secret("katu-ai", "ollama_url") or "http://localhost:11434"
        current_model = get_secret("katu-ai", "local_model") or "llama3"

        lbl_url = QLabel("URL do Ollama:")
        lbl_url.setStyleSheet(f"color:{ui.TEXT};")
        self._url_input = QLineEdit(current_url)
        lay.addWidget(lbl_url)
        lay.addWidget(self._url_input)

        lbl_model = QLabel("Modelo padrão:")
        lbl_model.setStyleSheet(f"color:{ui.TEXT};")
        self._model_input = QLineEdit(current_model)
        lay.addWidget(lbl_model)
        lay.addWidget(self._model_input)

        install_btn = QPushButton("Instalar Ollama")
        install_btn.clicked.connect(lambda: subprocess.Popen(["xdg-open", "https://ollama.ai"]))
        lay.addWidget(install_btn)
        self._key_name = None

    def _save(self):
        if hasattr(self, "_key_input") and self._key_input.text().strip():
            store_secret("katu-ai", self._key_name, self._key_input.text().strip())
        if hasattr(self, "_url_input"):
            store_secret("katu-ai", "ollama_url", self._url_input.text().strip())
        if hasattr(self, "_model_input"):
            store_secret("katu-ai", "local_model", self._model_input.text().strip())
        self.accept()


# ── Action Confirm Dialog ─────────────────────────────────────────────────────
class ActionConfirmDialog(QDialog):
    def __init__(self, action_id, action_def, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Confirmar Ação")
        self.setModal(True)
        self.setMinimumWidth(400)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 24, 24, 24)
        lay.setSpacing(16)
        t = QLabel("Katu AI deseja executar:")
        t.setStyleSheet(f"color:{ui.MUTED};")
        lay.addWidget(t)
        action_lbl = QLabel(action_def.get("label", action_id))
        action_lbl.setStyleSheet(f"font-size:16px; font-weight:bold; color:{ui.TEXT};")
        lay.addWidget(action_lbl)
        desc = QLabel(action_def.get("description", ""))
        desc.setWordWrap(True)
        desc.setStyleSheet(f"color:{ui.MUTED};")
        lay.addWidget(desc)
        btns = QHBoxLayout()
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        ok_btn = QPushButton("Executar")
        ok_btn.setObjectName("primary")
        ok_btn.clicked.connect(self.accept)
        btns.addWidget(cancel_btn)
        btns.addWidget(ok_btn)
        lay.addLayout(btns)


# ── Chat Bubble ───────────────────────────────────────────────────────────────
class ChatBubble(QFrame):
    def __init__(self, role, content, parent=None):
        super().__init__(parent)
        self.setObjectName("chatBubble")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(4)

        if role == "user":
            self.setStyleSheet(f"""
                QFrame#chatBubble {{
                    background:{ui.SURFACE}; border:1px solid {ui.BORDER};
                    border-radius:10px; border-bottom-right-radius:2px;
                    margin-left:60px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QFrame#chatBubble {{
                    background:{ui.CARD}; border:1px solid {ui.BORDER};
                    border-radius:10px; border-bottom-left-radius:2px;
                    margin-right:60px;
                }}
            """)

        self._content = QLabel()
        self._content.setWordWrap(True)
        self._content.setTextFormat(Qt.PlainText)
        self._content.setStyleSheet(f"color:{ui.TEXT}; line-height:1.6; font-size:13px;")
        self._content.setText(content)
        lay.addWidget(self._content)

    def append_text(self, text):
        current = self._content.text()
        self._content.setText(current + text)

    def get_text(self):
        return self._content.text()


# ── Main Window ───────────────────────────────────────────────────────────────
class KatuAI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Katu AI")
        self.setMinimumSize(860, 600)
        self.resize(1000, 700)
        self.setWindowIcon(QIcon("/usr/share/icons/hicolor/256x256/apps/katu-logo.png"))
        self._cfg = load_config()
        self._history = load_history()
        self._messages = []
        self._thread = None
        self._current_bubble = None
        self._build_ui()

    def _build_ui(self):
        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)
        hlay = QHBoxLayout(root)
        hlay.setContentsMargins(0, 0, 0, 0)
        hlay.setSpacing(0)

        # Left sidebar
        sidebar = self._build_sidebar()
        hlay.addWidget(sidebar)

        # Chat area
        chat_widget = self._build_chat()
        hlay.addWidget(chat_widget, 1)

    def _build_sidebar(self):
        sb = QWidget()
        sb.setObjectName("sidebar")
        sb.setFixedWidth(200)
        sb.setStyleSheet(f"QWidget#sidebar {{ background:{ui.SURFACE}; border-right:1px solid {ui.BORDER}; }}")
        lay = QVBoxLayout(sb)
        lay.setContentsMargins(12, 16, 12, 12)
        lay.setSpacing(8)

        # Header
        h = QLabel("🤖 Katu AI")
        h.setStyleSheet(f"font-size:15px; font-weight:bold; color:{ui.TEXT};")
        lay.addWidget(h)

        new_btn = QPushButton("+ Nova conversa")
        new_btn.setObjectName("primary")
        new_btn.setFixedHeight(36)
        new_btn.clicked.connect(self._new_conversation)
        lay.addWidget(new_btn)

        # Provider selector
        prov_lbl = QLabel("Provedor:")
        prov_lbl.setStyleSheet(f"color:{ui.MUTED}; font-size:12px;")
        lay.addWidget(prov_lbl)
        self._prov_combo = QComboBox()
        for pid, pdata in PROVIDERS.items():
            icon = pdata["icon"]
            name = pdata["name"]
            badge = " (beta)" if pdata["status"] == "beta" else ""
            self._prov_combo.addItem(f"{icon} {name}{badge}", pid)
        idx = list(PROVIDERS.keys()).index(self._cfg.get("provider", "openai")) if self._cfg.get("provider") in PROVIDERS else 0
        self._prov_combo.setCurrentIndex(idx)
        self._prov_combo.currentIndexChanged.connect(self._on_provider_change)
        lay.addWidget(self._prov_combo)

        config_btn = QPushButton("⚙ Configurar chave")
        config_btn.setFixedHeight(32)
        config_btn.clicked.connect(self._config_current_provider)
        lay.addWidget(config_btn)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"color:{ui.BORDER};")
        lay.addWidget(sep)

        lay.addWidget(QLabel("Histórico:").setStyleSheet or QLabel("Histórico:"))
        lbl2 = QLabel("Histórico:")
        lbl2.setStyleSheet(f"color:{ui.MUTED}; font-size:12px;")
        lay.addWidget(lbl2)

        self._history_list = QListWidget()
        self._history_list.setStyleSheet(f"""
            QListWidget {{ background:{ui.CARD}; border:1px solid {ui.BORDER}; border-radius:6px; }}
            QListWidget::item {{ padding:6px 8px; color:{ui.MUTED}; font-size:12px; }}
            QListWidget::item:selected {{ background:{ui.SURFACE}; color:{ui.TEXT}; }}
        """)
        self._history_list.itemClicked.connect(self._load_history_item)
        lay.addWidget(self._history_list, 1)

        clear_btn = QPushButton("Limpar histórico")
        clear_btn.setStyleSheet(f"color:{ui.ERROR}; font-size:12px; background:transparent; border:none;")
        clear_btn.clicked.connect(self._clear_history)
        lay.addWidget(clear_btn)
        self._refresh_history_list()
        return sb

    def _build_chat(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # Chat scroll area
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.NoFrame)
        self._chat_container = QWidget()
        self._chat_layout = QVBoxLayout(self._chat_container)
        self._chat_layout.setContentsMargins(20, 20, 20, 20)
        self._chat_layout.setSpacing(12)
        self._chat_layout.addStretch()
        self._scroll.setWidget(self._chat_container)

        # Input area
        input_area = QWidget()
        input_area.setFixedHeight(80)
        input_area.setStyleSheet(f"background:{ui.SURFACE}; border-top:1px solid {ui.BORDER};")
        ilay = QHBoxLayout(input_area)
        ilay.setContentsMargins(16, 12, 16, 12)
        ilay.setSpacing(8)

        self._input = QLineEdit()
        self._input.setPlaceholderText("Pergunte algo ao Katu AI... (Enter para enviar)")
        self._input.setFixedHeight(44)
        self._input.returnPressed.connect(self._send)

        self._send_btn = QPushButton("Enviar")
        self._send_btn.setObjectName("primary")
        self._send_btn.setFixedSize(80, 44)
        self._send_btn.clicked.connect(self._send)

        self._cancel_btn = QPushButton("Cancelar")
        self._cancel_btn.setFixedSize(80, 44)
        self._cancel_btn.setVisible(False)
        self._cancel_btn.clicked.connect(self._cancel)

        ilay.addWidget(self._input, 1)
        ilay.addWidget(self._cancel_btn)
        ilay.addWidget(self._send_btn)

        lay.addWidget(self._scroll, 1)
        lay.addWidget(input_area)
        self._show_welcome()
        return w

    def _show_welcome(self):
        prov = PROVIDERS.get(self._cfg.get("provider", "openai"), {})
        w = QWidget()
        wl = QVBoxLayout(w)
        wl.setAlignment(Qt.AlignCenter)
        wl.setSpacing(12)
        ico = QLabel("🤖")
        ico.setAlignment(Qt.AlignCenter)
        ico.setStyleSheet("font-size:48px;")
        title = QLabel("Katu AI")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"font-size:20px; font-weight:bold; color:{ui.TEXT};")
        sub = QLabel(f"Provedor ativo: {prov.get('icon','')} {prov.get('name','?')}")
        sub.setAlignment(Qt.AlignCenter)
        sub.setStyleSheet(f"color:{ui.MUTED};")
        hint = QLabel("Pergunte qualquer coisa. Exemplos:\n• \"Qual a versão do Katu OS?\"\n• \"Como instalar um programa?\"\n• \"Preciso de ajuda com Wi-Fi\"")
        hint.setAlignment(Qt.AlignCenter)
        hint.setWordWrap(True)
        hint.setStyleSheet(f"color:{ui.MUTED}; font-size:12px;")
        wl.addWidget(ico)
        wl.addWidget(title)
        wl.addWidget(sub)
        wl.addWidget(hint)
        self._chat_layout.addWidget(w, 0, Qt.AlignCenter)

    def _send(self):
        text = self._input.text().strip()
        if not text or self._thread and self._thread.isRunning():
            return
        self._input.clear()
        self._add_bubble("user", text)
        self._messages.append({"role": "user", "content": text})
        self._start_ai(text)

    def _start_ai(self, user_text):
        provider = self._cfg.get("provider", "openai")
        model = self._cfg.get("model", {}).get(provider, "")
        system_msg = "Você é o Katu AI, assistente amigável e inteligente do Katu OS, distribuição Linux brasileira.\n" \
                     "Responda sempre em português brasileiro. Seja direto, claro e útil.\n" \
                     "Para usuários leigos, evite jargão técnico. Para tarefas avançadas, seja preciso."
        if self._cfg.get("system_context"):
            ctx = get_system_context()
            if ctx:
                system_msg += f"\n\nInformações do sistema do usuário:\n{ctx}"
        messages = [{"role": "system", "content": system_msg}] + self._messages[:-1] + [self._messages[-1]]
        self._thread = AIThread(self._cfg, messages, provider, model)
        self._thread.chunk.connect(self._on_chunk)
        self._thread.done.connect(self._on_done)
        self._thread.error.connect(self._on_error)
        self._current_bubble = None
        self._send_btn.setEnabled(False)
        self._cancel_btn.setVisible(True)
        self._thread.start()

    def _on_chunk(self, text):
        if self._current_bubble is None:
            self._current_bubble = self._add_bubble("assistant", "")
        self._current_bubble.append_text(text)
        self._scroll_to_bottom()

    def _on_done(self):
        self._send_btn.setEnabled(True)
        self._cancel_btn.setVisible(False)
        if self._current_bubble:
            full = self._current_bubble.get_text()
            self._messages.append({"role": "assistant", "content": full})
            self._save_to_history(full)
        self._current_bubble = None

    def _on_error(self, msg):
        self._add_bubble("assistant", f"⚠ {msg}")
        self._send_btn.setEnabled(True)
        self._cancel_btn.setVisible(False)
        self._current_bubble = None

    def _cancel(self):
        if self._thread:
            self._thread.cancel()

    def _add_bubble(self, role, text):
        bubble = ChatBubble(role, text)
        self._chat_layout.insertWidget(self._chat_layout.count() - 1 if self._chat_layout.count() > 0 else 0, bubble)
        self._scroll_to_bottom()
        return bubble

    def _scroll_to_bottom(self):
        QTimer.singleShot(50, lambda: self._scroll.verticalScrollBar().setValue(
            self._scroll.verticalScrollBar().maximum()))

    def _new_conversation(self):
        self._messages = []
        for i in reversed(range(self._chat_layout.count())):
            w = self._chat_layout.itemAt(i).widget()
            if w:
                w.deleteLater()
        self._chat_layout.addStretch()
        self._show_welcome()

    def _on_provider_change(self):
        pid = self._prov_combo.currentData()
        self._cfg["provider"] = pid
        save_config(self._cfg)

    def _config_current_provider(self):
        pid = self._prov_combo.currentData()
        dlg = ProviderConfigDialog(pid, self)
        dlg.exec_() if QT == 'PyQt5' else dlg.exec()

    def _save_to_history(self, response):
        if not self._cfg.get("save_history", True):
            return
        if self._messages:
            last_user = next((m["content"] for m in reversed(self._messages) if m["role"] == "user"), "")
            entry = {
                "ts": datetime.now().isoformat(timespec="minutes"),
                "provider": self._cfg.get("provider"),
                "preview": last_user[:60],
                "messages": self._messages[-10:],
            }
            self._history.insert(0, entry)
            save_history(self._history)
            self._refresh_history_list()

    def _refresh_history_list(self):
        self._history_list.clear()
        for entry in self._history[:20]:
            item = QListWidgetItem(f"{entry.get('ts','')}\n{entry.get('preview','')}")
            item.setData(Qt.UserRole, entry)
            self._history_list.addItem(item)

    def _load_history_item(self, item):
        entry = item.data(Qt.UserRole)
        if not entry:
            return
        msgs = entry.get("messages", [])
        self._messages = msgs
        for i in reversed(range(self._chat_layout.count())):
            w = self._chat_layout.itemAt(i).widget()
            if w:
                w.deleteLater()
        self._chat_layout.addStretch()
        for m in msgs:
            if m["role"] != "system":
                self._add_bubble(m["role"], m["content"])

    def _clear_history(self):
        reply = QMessageBox.question(self, "Limpar histórico",
            "Deseja apagar todo o histórico de conversas?\nEsta ação não pode ser desfeita.",
            QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self._history = []
            save_history([])
            self._refresh_history_list()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Katu AI")
    app.setApplicationVersion("1.0.1")
    if CORE:
        app.setStyleSheet(ui.STYLESHEET)
    win = KatuAI()
    win.show()
    sys.exit(app.exec_() if QT == 'PyQt5' else app.exec())


if __name__ == "__main__":
    main()
