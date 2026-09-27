#!/usr/bin/env python3
"""Katu Feedback — User Feedback for Katu OS."""
import sys, json, subprocess
from pathlib import Path
from datetime import datetime

try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import Qt, QThread, pyqtSignal
    from PyQt5.QtGui import *
    QT = 'PyQt5'
except ImportError:
    from PySide6.QtWidgets import *
    from PySide6.QtCore import Qt, QThread, Signal as pyqtSignal
    from PySide6.QtGui import *
    QT = 'PySide6'

sys.path.insert(0, '/usr/lib/python3/dist-packages')
try:
    from katu_core import ui, system
    CORE = True
except ImportError:
    CORE = False
    class _FakeUI:
        STYLESHEET = ""; BG = "#0d1117"; SURFACE = "#161b22"; CARD = "#1c2128"
        BORDER = "#30363d"; ACCENT = "#00c853"; TEXT = "#e6edf3"; MUTED = "#8b949e"
        ERROR = "#f85149"; AMBER = "#ffab00"; SUCCESS = "#3fb950"
    ui = _FakeUI()
    class system:
        @staticmethod
        def get_katu_version(): return "1.0"

FEEDBACK_DIR = Path.home() / ".config" / "katu" / "feedback"
FEEDBACK_DIR.mkdir(parents=True, exist_ok=True)

TYPES = [
    ("🐛", "Reportar problema",    "Encontrou um bug ou algo que não funciona?"),
    ("💡", "Sugerir melhoria",     "Tem uma ideia para melhorar o Katu OS?"),
    ("👏", "Enviar elogio",        "O que você mais gostou no Katu OS?"),
    ("🖥️",  "Problema de hardware","Seu hardware não funciona corretamente?"),
    ("🌐", "Problema de tradução", "Encontrou algo mal traduzido para português?"),
]


class SendThread(QThread):
    done = pyqtSignal(bool, str)

    def __init__(self, data):
        super().__init__()
        self._data = data

    def run(self):
        # Save locally (the user's feedback — future: send to API)
        try:
            stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            f = FEEDBACK_DIR / f"feedback-{stamp}.json"
            f.write_text(json.dumps(self._data, indent=2, ensure_ascii=False))
            self.done.emit(True, str(f))
        except Exception as e:
            self.done.emit(False, str(e))


class KatuFeedback(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Katu Feedback")
        self.setMinimumSize(580, 560)
        self.resize(640, 600)
        self.setWindowIcon(QIcon("/usr/share/icons/hicolor/256x256/apps/katu-feedback.png"))
        self._build_ui()

    def _build_ui(self):
        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)
        lay = QVBoxLayout(root)
        lay.setContentsMargins(32, 32, 32, 32)
        lay.setSpacing(16)

        h = QHBoxLayout()
        ico = QLabel("💬")
        ico.setStyleSheet("font-size:32px;")
        info = QVBoxLayout()
        t = QLabel("Katu Feedback")
        t.setStyleSheet(f"font-size:20px; font-weight:bold; color:{ui.TEXT};")
        sub = QLabel("Sua opinião ajuda a melhorar o Katu OS")
        sub.setStyleSheet(f"color:{ui.MUTED};")
        info.addWidget(t)
        info.addWidget(sub)
        h.addWidget(ico)
        h.addLayout(info, 1)
        lay.addLayout(h)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"color:{ui.BORDER};")
        lay.addWidget(sep)

        type_lbl = QLabel("Tipo de feedback:")
        type_lbl.setStyleSheet(f"color:{ui.TEXT}; font-weight:bold;")
        lay.addWidget(type_lbl)

        self._type_buttons = QButtonGroup()
        type_layout = QGridLayout()
        type_layout.setSpacing(8)
        for i, (icon, label, hint) in enumerate(TYPES):
            btn = QRadioButton(f"{icon}  {label}")
            btn.setStyleSheet(f"color:{ui.TEXT}; font-size:13px;")
            btn.setToolTip(hint)
            self._type_buttons.addButton(btn, i)
            type_layout.addWidget(btn, i // 2, i % 2)
        self._type_buttons.button(0).setChecked(True)
        lay.addLayout(type_layout)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight)

        self._title_input = QLineEdit()
        self._title_input.setPlaceholderText("Resumo em uma frase")
        self._title_input.setFixedHeight(40)

        self._desc_input = QPlainTextEdit()
        self._desc_input.setPlaceholderText("Descreva em detalhes. Para problemas: o que aconteceu e como reproduzir.")
        self._desc_input.setFixedHeight(100)

        self._steps_input = QPlainTextEdit()
        self._steps_input.setPlaceholderText("(Opcional) Passo a passo para reproduzir o problema")
        self._steps_input.setFixedHeight(60)

        form.addRow("Título*:", self._title_input)
        form.addRow("Descrição*:", self._desc_input)
        form.addRow("Como reproduzir:", self._steps_input)
        lay.addLayout(form)

        # System info checkbox
        self._include_sysinfo = QCheckBox("Incluir informações do sistema (versão Katu OS, kernel)")
        self._include_sysinfo.setChecked(True)
        self._include_sysinfo.setStyleSheet(f"color:{ui.TEXT};")
        lay.addWidget(self._include_sysinfo)

        note = QLabel(
            "⚠ Seu feedback é salvo localmente em ~/.config/katu/feedback/\n"
            "Não inclua informações pessoais como CPF, senha ou dados bancários."
        )
        note.setWordWrap(True)
        note.setStyleSheet(f"color:{ui.MUTED}; font-size:12px;")
        lay.addWidget(note)

        btn_row = QHBoxLayout()
        send_btn = QPushButton("ENVIAR FEEDBACK")
        send_btn.setObjectName("primary")
        send_btn.setFixedHeight(44)
        send_btn.clicked.connect(self._send)

        github_btn = QPushButton("Abrir no GitHub")
        github_btn.setFixedHeight(44)
        github_btn.clicked.connect(lambda: subprocess.Popen(
            ["xdg-open", "https://github.com/controldtechnology/katuos/issues"]))

        btn_row.addWidget(send_btn)
        btn_row.addWidget(github_btn)
        lay.addLayout(btn_row)

    def _send(self):
        title = self._title_input.text().strip()
        desc  = self._desc_input.toPlainText().strip()
        if not title or not desc:
            QMessageBox.warning(self, "Campos obrigatórios", "Preencha o título e a descrição.")
            return
        feedback_type_id = self._type_buttons.checkedId()
        feedback_type = TYPES[feedback_type_id][1] if feedback_type_id >= 0 else "Outro"
        data = {
            "type":  feedback_type,
            "title": title,
            "desc":  desc,
            "steps": self._steps_input.toPlainText().strip(),
            "date":  datetime.now().isoformat(timespec="minutes"),
        }
        if self._include_sysinfo.isChecked() and CORE:
            try:
                data["version"] = system.get_katu_version()
            except Exception:
                pass
        t = SendThread(data)
        t.done.connect(self._on_done)
        t.start()
        self._thread = t

    def _on_done(self, ok, path):
        if ok:
            QMessageBox.information(self, "Feedback enviado",
                "Obrigado pelo seu feedback!\n\n"
                "Para bugs, abra uma issue no GitHub para acompanhamento.\n"
                f"Salvo em: {path}")
            self._title_input.clear()
            self._desc_input.clear()
            self._steps_input.clear()
        else:
            QMessageBox.warning(self, "Erro", f"Não foi possível salvar o feedback: {path}")


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Katu Feedback")
    if CORE:
        app.setStyleSheet(ui.STYLESHEET)
    win = KatuFeedback()
    win.show()
    sys.exit(app.exec_() if QT == 'PyQt5' else app.exec())


if __name__ == "__main__":
    main()
