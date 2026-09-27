#!/usr/bin/env python3
"""Katu Help — Offline Help Center for Katu OS."""
import sys, subprocess
from pathlib import Path

try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import Qt, QTimer
    from PyQt5.QtGui import *
    QT = 'PyQt5'
except ImportError:
    from PySide6.QtWidgets import *
    from PySide6.QtCore import Qt, QTimer
    from PySide6.QtGui import *
    QT = 'PySide6'

sys.path.insert(0, '/usr/lib/python3/dist-packages')
try:
    from katu_core import ui
    CORE = True
except ImportError:
    CORE = False
    class _FakeUI:
        STYLESHEET = ""; BG = "#0d1117"; SURFACE = "#161b22"; CARD = "#1c2128"
        BORDER = "#30363d"; ACCENT = "#00c853"; TEXT = "#e6edf3"; MUTED = "#8b949e"
        ERROR = "#f85149"; AMBER = "#ffab00"; SUCCESS = "#3fb950"
    ui = _FakeUI()

HELP_CONTENT = {
    "Começando": {
        "Como usar o Katu OS": """
**Bem-vindo ao Katu OS!**

O Katu OS é um sistema operacional Linux brasileiro, simples e moderno.

**Primeiros passos:**
- Seu desktop usa o KDE Plasma — um ambiente gráfico completo
- A barra de tarefas fica na parte inferior
- Clique com o botão direito no desktop para acessar opções
- O menu de aplicativos fica no canto inferior esquerdo

**Dica:** Se precisar de ajuda, o Katu AI está sempre disponível!
""",
        "Abrir aplicativos": """
**Como abrir aplicativos:**

1. Clique no ícone do menu no canto inferior esquerdo
2. Pesquise o nome do aplicativo
3. Ou clique diretamente no ícone na barra de tarefas

**Atalhos úteis:**
- Super (tecla Windows): abre o menu
- Alt + F2: executar comando
- Ctrl + Alt + T: terminal
""",
        "Instalar programas": """
**Instalar programas no Katu OS:**

Use o **Katu Store** — não precisa de terminal!

1. Abra o Katu Store pelo menu de aplicativos
2. Pesquise o programa desejado
3. Clique em "Instalar"
4. Aguarde a instalação

Se precisar de algo específico que não encontrar na Store,
abra o terminal e use: sudo apt install nome-do-programa
""",
    },
    "Internet": {
        "Conectar ao Wi-Fi": """
**Conectar ao Wi-Fi:**

1. Clique no ícone de rede na barra de tarefas (canto inferior direito)
2. Selecione sua rede Wi-Fi
3. Digite a senha
4. Clique em "Conectar"

**Problemas de conexão?**
- Verifique se o Wi-Fi está ativado no painel
- Tente desligar e religar o Wi-Fi
- Abra o Katu Diagnostic para verificar
""",
        "Navegar na internet": """
**Navegadores disponíveis:**

- **Firefox ESR**: navegador padrão do Katu OS
- **Google Chrome**: disponível no Katu Store

**Dicas:**
- Ctrl + T: nova aba
- Ctrl + L: focar a barra de endereço
- Ctrl + Shift + Delete: limpar histórico
""",
    },
    "Arquivos": {
        "Gerenciar arquivos": """
**Dolphin — Gerenciador de Arquivos:**

- Clique no ícone de pasta na barra de tarefas
- Navegue pelas pastas com um clique
- Abra arquivos com duplo clique

**Pastas principais:**
- Documentos, Fotos, Vídeos, Músicas: na pasta pessoal
- Ctrl + H: mostrar arquivos ocultos
""",
        "Compactar e extrair": """
**Compactar/descompactar arquivos:**

1. Clique com botão direito no arquivo/pasta
2. Selecione "Comprimir..." ou "Extrair aqui"

Formatos suportados: ZIP, TAR, 7Z, RAR e outros.
O Ark está instalado por padrão.
""",
    },
    "Atualizações": {
        "Atualizar o sistema": """
**Manter o Katu OS atualizado:**

1. Abra o **Katu Update** pelo menu
2. Clique em "VERIFICAR"
3. Se houver atualizações, clique em "ATUALIZAR TUDO"

**Por que atualizar?**
- Correções de segurança
- Novos recursos
- Melhor desempenho
- Correções de bugs

O sistema nunca reinicia automaticamente.
""",
    },
    "Backup": {
        "Fazer backup dos arquivos": """
**Proteja seus arquivos com o Katu Backup:**

1. Abra o **Katu Backup** pelo menu
2. Selecione as pastas (Documentos, Fotos, etc.)
3. Escolha o destino (HD externo, pendrive)
4. Clique em "FAZER BACKUP AGORA"

**Dica:** Faça backup regularmente, especialmente antes de
grandes atualizações ou mudanças no sistema.
""",
        "Restaurar arquivos": """
**Restaurar um backup:**

1. Abra o **Katu Backup**
2. Clique na aba "Restaurar"
3. Selecione o backup na lista
4. Escolha quais itens restaurar
5. Clique em "RESTAURAR BACKUP"
""",
    },
    "Drivers": {
        "Instalar drivers": """
**Instalar drivers de hardware:**

1. Abra o **Katu Drivers** pelo menu
2. Verifique a lista de dispositivos
3. Se aparecer "Driver recomendado disponível", clique em "Instalar driver"

O Katu Drivers instala apenas drivers de fontes oficiais.
""",
    },
    "Problemas": {
        "Sistema lento": """
**O que fazer quando o sistema está lento:**

1. Verifique o uso de recursos no monitor do sistema
2. Feche programas que não está usando
3. Execute o Katu Diagnostic para identificar problemas
4. Verifique se há atualizações pendentes

**Atalho:** Ctrl + Esc abre o monitor de tarefas
""",
        "Wi-Fi não funciona": """
**Wi-Fi com problemas:**

1. Clique no ícone de rede → verifique se está ativo
2. Tente desligar e religar o Wi-Fi
3. Abra o **Katu Diagnostic** e verifique o item "Rede"
4. Abra o **Katu Drivers** e verifique o adaptador Wi-Fi

Se nada funcionar, abra o terminal:
```
sudo systemctl restart NetworkManager
```
""",
        "Como reiniciar ou desligar": """
**Reiniciar ou desligar o Katu OS:**

1. Clique no menu (canto inferior esquerdo)
2. Role até o final e clique em "Desligar"
3. Escolha: Desligar, Reiniciar ou Suspender

**Atalho:** Alt + F4 no desktop abre o menu de sessão
""",
    },
    "IA": {
        "Configurar o Katu AI": """
**Usar o Katu AI:**

O Katu AI suporta múltiplos provedores de IA.

**Para usar, você precisa de uma chave de API própria (BYOK):**

1. Abra o Katu AI
2. Clique em "Configurar chave"
3. Escolha seu provedor (OpenAI, Claude, Gemini)
4. Cole sua chave de API

**Sua chave é armazenada localmente com segurança.**
Nunca é compartilhada com o Katu OS.

**Provedores disponíveis:**
- OpenAI (ChatGPT): platform.openai.com
- Claude: console.anthropic.com
- Gemini: aistudio.google.com
- Local (Ollama): ollama.ai
""",
        "IA Local": """
**Usar IA sem internet com Ollama:**

1. Instale o Ollama: visite ollama.ai
2. Baixe um modelo: ollama pull llama3
3. No Katu AI, selecione "Local" como provedor
4. Configure o endereço: http://localhost:11434

**Vantagem:** Funciona sem internet, seus dados ficam no computador.
**Desvantagem:** Requer um computador potente.
""",
    },
}


class HelpViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Katu Help")
        self.setMinimumSize(860, 600)
        self.resize(1000, 660)
        self.setWindowIcon(QIcon("/usr/share/icons/hicolor/256x256/apps/katu-logo.png"))
        self._build_ui()

    def _build_ui(self):
        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)
        hlay = QHBoxLayout(root)
        hlay.setContentsMargins(0, 0, 0, 0)
        hlay.setSpacing(0)

        # Sidebar
        sidebar = self._build_sidebar()
        hlay.addWidget(sidebar)

        # Content
        content = self._build_content()
        hlay.addWidget(content, 1)

    def _build_sidebar(self):
        sb = QWidget()
        sb.setObjectName("sidebar")
        sb.setFixedWidth(220)
        sb.setStyleSheet(f"QWidget#sidebar{{background:{ui.SURFACE};border-right:1px solid {ui.BORDER};}}")
        lay = QVBoxLayout(sb)
        lay.setContentsMargins(12, 16, 12, 12)
        lay.setSpacing(8)

        logo = QLabel("❓ Katu Help")
        logo.setStyleSheet(f"font-size:15px; font-weight:bold; color:{ui.TEXT};")
        lay.addWidget(logo)

        self._search = QLineEdit()
        self._search.setPlaceholderText("Pesquisar na ajuda...")
        self._search.setFixedHeight(32)
        self._search.textChanged.connect(self._on_search)
        lay.addWidget(self._search)

        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)
        self._tree.setStyleSheet(f"""
            QTreeWidget {{ background:{ui.SURFACE}; border:none; }}
            QTreeWidget::item {{ padding:5px 4px; color:{ui.MUTED}; }}
            QTreeWidget::item:selected {{ background:{ui.CARD}; color:{ui.TEXT}; }}
            QTreeWidget::item:hover {{ color:{ui.TEXT}; }}
        """)
        for category, articles in HELP_CONTENT.items():
            parent = QTreeWidgetItem(self._tree, [category])
            parent.setExpanded(True)
            for title in articles.keys():
                child = QTreeWidgetItem(parent, [title])
                child.setData(0, Qt.UserRole, (category, title))
        self._tree.itemClicked.connect(self._on_item_click)
        lay.addWidget(self._tree, 1)
        return sb

    def _build_content(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(32, 28, 32, 28)
        lay.setSpacing(16)

        self._article_title = QLabel("Bem-vindo à Ajuda do Katu OS")
        self._article_title.setStyleSheet(f"font-size:20px; font-weight:bold; color:{ui.TEXT};")
        lay.addWidget(self._article_title)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"color:{ui.BORDER};")
        lay.addWidget(sep)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        self._content_label = QLabel()
        self._content_label.setWordWrap(True)
        self._content_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self._content_label.setStyleSheet(f"color:{ui.TEXT}; line-height:1.8; font-size:13px;")
        self._content_label.setTextFormat(Qt.PlainText)
        scroll.setWidget(self._content_label)
        lay.addWidget(scroll, 1)

        welcome = (
            "Encontre respostas para as perguntas mais comuns sobre o Katu OS.\n\n"
            "Selecione um tópico na lista à esquerda, ou use a busca para encontrar o que procura.\n\n"
            "Toda a documentação básica funciona sem internet."
        )
        self._content_label.setText(welcome)

        # Online help button
        online_btn = QPushButton("Abrir ajuda online")
        online_btn.setFixedHeight(36)
        online_btn.clicked.connect(lambda: subprocess.Popen(["xdg-open", "https://katuos.com.br/ajuda"]))
        lay.addWidget(online_btn)
        return w

    def _on_item_click(self, item, col):
        data = item.data(0, Qt.UserRole)
        if not data:
            return
        category, title = data
        content = HELP_CONTENT.get(category, {}).get(title, "")
        self._article_title.setText(title)
        # Simple markdown-ish rendering as plain text
        text = content.strip()
        text = text.replace("**", "").replace("*", "").replace("`", "")
        self._content_label.setText(text)

    def _on_search(self, query):
        query = query.lower().strip()
        if not query:
            for i in range(self._tree.topLevelItemCount()):
                cat = self._tree.topLevelItem(i)
                cat.setHidden(False)
                for j in range(cat.childCount()):
                    cat.child(j).setHidden(False)
            return
        for i in range(self._tree.topLevelItemCount()):
            cat = self._tree.topLevelItem(i)
            visible = False
            for j in range(cat.childCount()):
                article = cat.child(j)
                title = article.text(0).lower()
                cat_name = cat.text(0).lower()
                data = article.data(0, Qt.UserRole)
                content = ""
                if data:
                    content = HELP_CONTENT.get(data[0], {}).get(data[1], "").lower()
                match = query in title or query in cat_name or query in content
                article.setHidden(not match)
                if match:
                    visible = True
            cat.setHidden(not visible)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Katu Help")
    if CORE:
        app.setStyleSheet(ui.STYLESHEET)
    win = HelpViewer()
    win.show()
    sys.exit(app.exec_() if QT == 'PyQt5' else app.exec())


if __name__ == "__main__":
    main()
