#!/usr/bin/env python3
"""Katu Web Apps — Create and manage web application shortcuts."""
import sys, os, subprocess, json, re, shutil
from pathlib import Path

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
    from katu_core import ui
    CORE = True
except ImportError:
    CORE = False
    class _FakeUI:
        STYLESHEET = ""; BG = "#0d1117"; SURFACE = "#161b22"; CARD = "#1c2128"
        BORDER = "#30363d"; ACCENT = "#00c853"; TEXT = "#e6edf3"; MUTED = "#8b949e"
        ERROR = "#f85149"; AMBER = "#ffab00"; SUCCESS = "#3fb950"
    ui = _FakeUI()

HOME = Path.home()
APPS_DIR  = HOME / ".local" / "share" / "applications"
ICONS_DIR = HOME / ".local" / "share" / "katu-webapps" / "icons"
DATA_FILE = HOME / ".config" / "katu" / "webapps" / "apps.json"


def _validate_url(url: str) -> bool:
    return bool(re.match(r"^https?://[^\s/$.?#].[^\s]*$", url))


def load_webapps():
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text())
        except Exception:
            pass
    return []


def save_webapps(apps):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(apps, indent=2, ensure_ascii=False))


def create_webapp(name, url, icon="🌐", browser="firefox-esr"):
    if not _validate_url(url):
        return False, "URL inválida"
    safe_name = re.sub(r"[^a-z0-9-]", "-", name.lower().strip())
    desktop_path = APPS_DIR / f"katu-webapp-{safe_name}.desktop"
    APPS_DIR.mkdir(parents=True, exist_ok=True)
    # Try to find a browser that supports --app=
    app_cmd = browser
    for br in ["google-chrome-stable", "chromium", "firefox-esr"]:
        if shutil.which(br):
            app_cmd = br
            break
    if "chrome" in app_cmd or "chromium" in app_cmd:
        exec_line = f"{app_cmd} --app={url} --class=KatuWebApp"
    else:
        exec_line = f"{app_cmd} {url}"
    desktop_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name={name}
Comment=Web App: {url}
Exec={exec_line}
Icon=katu-logo
Terminal=false
Categories=Network;WebApplication;
StartupNotify=true
X-Katu-WebApp=true
X-Katu-URL={url}
"""
    try:
        desktop_path.write_text(desktop_content)
        desktop_path.chmod(0o755)
    except Exception as e:
        return False, str(e)
    apps = load_webapps()
    apps.append({"name": name, "url": url, "icon": icon, "desktop": str(desktop_path)})
    save_webapps(apps)
    try:
        subprocess.run(["update-desktop-database", str(APPS_DIR)], check=False)
    except Exception:
        pass
    return True, str(desktop_path)


def remove_webapp(desktop_path):
    try:
        Path(desktop_path).unlink(missing_ok=True)
        apps = [a for a in load_webapps() if a.get("desktop") != desktop_path]
        save_webapps(apps)
        return True
    except Exception:
        return False


class CreateDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Criar Web App")
        self.setModal(True)
        self.setMinimumWidth(460)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 24, 24, 24)
        lay.setSpacing(14)

        t = QLabel("🌐 Criar Web App")
        t.setStyleSheet(f"font-size:18px; font-weight:bold; color:{ui.TEXT};")
        lay.addWidget(t)

        sub = QLabel("Transforma qualquer site em um atalho no seu menu de aplicativos.")
        sub.setWordWrap(True)
        sub.setStyleSheet(f"color:{ui.MUTED};")
        lay.addWidget(sub)

        form = QFormLayout()
        form.setSpacing(10)
        self._url_input = QLineEdit()
        self._url_input.setPlaceholderText("https://exemplo.com.br")
        self._url_input.setFixedHeight(40)
        self._url_input.textChanged.connect(self._on_url_change)

        self._name_input = QLineEdit()
        self._name_input.setPlaceholderText("Nome do aplicativo")
        self._name_input.setFixedHeight(40)

        form.addRow("URL:", self._url_input)
        form.addRow("Nome:", self._name_input)
        lay.addLayout(form)

        self._url_status = QLabel("")
        self._url_status.setStyleSheet(f"color:{ui.MUTED}; font-size:12px;")
        lay.addWidget(self._url_status)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.button(QDialogButtonBox.Ok).setText("Criar Web App")
        btns.accepted.connect(self._accept)
        btns.rejected.connect(self.reject)
        lay.addWidget(btns)

    def _on_url_change(self, url):
        if not url:
            self._url_status.setText("")
            return
        if _validate_url(url):
            self._url_status.setText(f"✓ URL válida")
            self._url_status.setStyleSheet(f"color:{ui.SUCCESS}; font-size:12px;")
            if not self._name_input.text():
                try:
                    domain = url.split("//")[1].split("/")[0].replace("www.", "")
                    self._name_input.setText(domain.split(".")[0].title())
                except Exception:
                    pass
        else:
            self._url_status.setText("✗ URL inválida (deve começar com https://)")
            self._url_status.setStyleSheet(f"color:{ui.ERROR}; font-size:12px;")

    def _accept(self):
        url = self._url_input.text().strip()
        name = self._name_input.text().strip()
        if not url or not name:
            QMessageBox.warning(self, "Campos obrigatórios", "Preencha a URL e o nome.")
            return
        if not _validate_url(url):
            QMessageBox.warning(self, "URL inválida", "Digite uma URL válida (começando com https://).")
            return
        self._result = {"name": name, "url": url}
        self.accept()

    def get_result(self):
        return getattr(self, "_result", None)


class AppRow(QFrame):
    open_requested   = pyqtSignal(str)
    remove_requested = pyqtSignal(dict)

    def __init__(self, app_info, parent=None):
        super().__init__(parent)
        self._app = app_info
        self.setObjectName("appRow")
        self.setFixedHeight(60)
        self.setStyleSheet(f"QFrame#appRow{{background:{ui.CARD};border:1px solid {ui.BORDER};border-radius:8px;}}")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 6, 14, 6)
        lay.setSpacing(12)

        ico = QLabel(app_info.get("icon", "🌐"))
        ico.setStyleSheet("font-size:20px;")
        ico.setFixedWidth(28)

        info = QVBoxLayout()
        info.setSpacing(1)
        name = QLabel(app_info.get("name", ""))
        name.setStyleSheet(f"font-weight:bold; color:{ui.TEXT};")
        url  = QLabel(app_info.get("url", ""))
        url.setStyleSheet(f"color:{ui.MUTED}; font-size:11px;")
        info.addWidget(name)
        info.addWidget(url)

        open_btn = QPushButton("Abrir")
        open_btn.setObjectName("primary")
        open_btn.setFixedSize(70, 30)
        open_btn.clicked.connect(lambda: self.open_requested.emit(self._app.get("url", "")))

        del_btn = QPushButton("Remover")
        del_btn.setObjectName("danger")
        del_btn.setFixedSize(80, 30)
        del_btn.clicked.connect(lambda: self.remove_requested.emit(self._app))

        lay.addWidget(ico)
        lay.addLayout(info, 1)
        lay.addWidget(open_btn)
        lay.addWidget(del_btn)


class KatuWebApps(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Katu Web Apps")
        self.setMinimumSize(620, 500)
        self.resize(700, 560)
        self.setWindowIcon(QIcon("/usr/share/icons/hicolor/256x256/apps/katu-logo.png"))
        self._build_ui()
        self._refresh()

    def _build_ui(self):
        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)
        lay = QVBoxLayout(root)
        lay.setContentsMargins(32, 32, 32, 32)
        lay.setSpacing(16)

        h = QHBoxLayout()
        ico = QLabel("🌐")
        ico.setStyleSheet("font-size:32px;")
        info = QVBoxLayout()
        t = QLabel("Katu Web Apps")
        t.setStyleSheet(f"font-size:20px; font-weight:bold; color:{ui.TEXT};")
        sub = QLabel("Transforme sites em atalhos de aplicativo")
        sub.setStyleSheet(f"color:{ui.MUTED};")
        info.addWidget(t)
        info.addWidget(sub)
        h.addWidget(ico)
        h.addLayout(info, 1)
        create_btn = QPushButton("+ Criar Web App")
        create_btn.setObjectName("primary")
        create_btn.setFixedHeight(38)
        create_btn.clicked.connect(self._create)
        h.addWidget(create_btn)
        lay.addLayout(h)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"color:{ui.BORDER};")
        lay.addWidget(sep)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        self._list_widget = QWidget()
        self._list_lay = QVBoxLayout(self._list_widget)
        self._list_lay.setContentsMargins(0, 0, 0, 0)
        self._list_lay.setSpacing(8)
        scroll.setWidget(self._list_widget)
        lay.addWidget(scroll, 1)

    def _refresh(self):
        for i in reversed(range(self._list_lay.count())):
            w = self._list_lay.itemAt(i).widget()
            if w:
                w.deleteLater()
        apps = load_webapps()
        if not apps:
            empty = QLabel("Nenhum Web App criado ainda.\n\nClique em '+ Criar Web App' para começar.")
            empty.setAlignment(Qt.AlignCenter)
            empty.setWordWrap(True)
            empty.setStyleSheet(f"color:{ui.MUTED};")
            self._list_lay.addWidget(empty)
        else:
            for app in apps:
                row = AppRow(app)
                row.open_requested.connect(lambda url: subprocess.Popen(["xdg-open", url]))
                row.remove_requested.connect(self._remove)
                self._list_lay.addWidget(row)
        self._list_lay.addStretch()

    def _create(self):
        dlg = CreateDialog(self)
        if (dlg.exec_() if QT == 'PyQt5' else dlg.exec()) == QDialog.Accepted:
            result = dlg.get_result()
            if result:
                ok, path = create_webapp(result["name"], result["url"])
                if ok:
                    QMessageBox.information(self, "Web App criado",
                        f"'{result['name']}' adicionado ao menu de aplicativos!")
                    self._refresh()
                else:
                    QMessageBox.warning(self, "Erro", f"Não foi possível criar o Web App: {path}")

    def _remove(self, app_info):
        reply = QMessageBox.question(self, "Remover Web App",
            f"Remover '{app_info.get('name')}'?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            remove_webapp(app_info.get("desktop", ""))
            self._refresh()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Katu Web Apps")
    if CORE:
        app.setStyleSheet(ui.STYLESHEET)
    win = KatuWebApps()
    win.show()
    sys.exit(app.exec_() if QT == 'PyQt5' else app.exec())


if __name__ == "__main__":
    main()
