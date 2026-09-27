#!/usr/bin/env python3
"""Katu Backup — Backup and Restore for Katu OS."""
import sys, os, subprocess, json
from pathlib import Path
from datetime import datetime

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

sys.path.insert(0, '/usr/lib/python3/dist-packages')
try:
    from katu_core import ui, notifications
    CORE = True
except ImportError:
    CORE = False
    class _FakeUI:
        STYLESHEET = ""; BG = "#0d1117"; SURFACE = "#161b22"; CARD = "#1c2128"
        BORDER = "#30363d"; ACCENT = "#00c853"; TEXT = "#e6edf3"; MUTED = "#8b949e"
        ERROR = "#f85149"; AMBER = "#ffab00"; SUCCESS = "#3fb950"; TEXT_INV = "#0d1117"
    ui = _FakeUI()
    class notifications:
        @staticmethod
        def notify_success(a, b=""): pass
        @staticmethod
        def notify_error(a, b=""): pass

HOME = Path.home()
CONF_FILE = HOME / ".config" / "katu" / "backup" / "config.json"

SOURCES = [
    {"id": "docs",     "name": "Documentos",    "icon": "📄", "path": str(HOME / "Documentos"),    "default": True},
    {"id": "photos",   "name": "Fotos",         "icon": "📷", "path": str(HOME / "Imagens"),       "default": True},
    {"id": "videos",   "name": "Vídeos",        "icon": "🎬", "path": str(HOME / "Vídeos"),        "default": False},
    {"id": "music",    "name": "Músicas",       "icon": "🎵", "path": str(HOME / "Música"),        "default": False},
    {"id": "desktop",  "name": "Área de Trabalho","icon":"🖥️", "path": str(HOME / "Área de Trabalho"), "default": True},
    {"id": "config",   "name": "Configurações", "icon": "⚙️", "path": str(HOME / ".config"),      "default": False},
]


def load_config():
    if CONF_FILE.exists():
        try:
            return json.loads(CONF_FILE.read_text())
        except Exception:
            pass
    return {"destination": str(HOME), "sources": ["docs", "photos", "desktop"]}


def save_config(cfg):
    CONF_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONF_FILE.write_text(json.dumps(cfg, indent=2))


def list_backups(dest):
    backups = []
    dest_path = Path(dest)
    if not dest_path.exists():
        return backups
    for d in sorted(dest_path.glob("katu-backup-*"), reverse=True):
        if d.is_dir():
            meta_f = d / "meta.json"
            if meta_f.exists():
                try:
                    meta = json.loads(meta_f.read_text())
                    meta["path"] = str(d)
                    backups.append(meta)
                except Exception:
                    pass
            else:
                backups.append({"path": str(d), "date": d.name.replace("katu-backup-", ""), "sources": []})
    return backups


class BackupThread(QThread):
    progress = pyqtSignal(str)
    done     = pyqtSignal(bool, str)

    def __init__(self, sources, dest):
        super().__init__()
        self._sources = sources
        self._dest = dest

    def run(self):
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_dir = Path(self._dest) / f"katu-backup-{stamp}"
        try:
            backup_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            self.done.emit(False, str(e))
            return
        ok = True
        for src_info in self._sources:
            src = src_info["path"]
            name = src_info["name"]
            if not Path(src).exists():
                self.progress.emit(f"⚠ {name}: pasta não encontrada ({src})")
                continue
            self.progress.emit(f"Copiando {name}...")
            dest = backup_dir / src_info["id"]
            dest.mkdir(parents=True, exist_ok=True)
            try:
                p = subprocess.Popen(
                    ["rsync", "-a", "--info=progress2", src + "/", str(dest) + "/"],
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
                )
                for line in p.stdout:
                    l = line.strip()
                    if l:
                        self.progress.emit(l[:80])
                p.wait()
                if p.returncode != 0:
                    ok = False
                    self.progress.emit(f"✗ Erro ao copiar {name}")
            except Exception as e:
                self.progress.emit(f"✗ {name}: {e}")
                ok = False
        # Write meta
        meta = {
            "date": datetime.now().isoformat(timespec="minutes"),
            "stamp": stamp,
            "sources": [s["id"] for s in self._sources],
            "ok": ok,
        }
        try:
            (backup_dir / "meta.json").write_text(json.dumps(meta, indent=2))
        except Exception:
            pass
        self.done.emit(ok, str(backup_dir))


class RestoreThread(QThread):
    progress = pyqtSignal(str)
    done     = pyqtSignal(bool)

    def __init__(self, backup_path, source_ids, dest_root):
        super().__init__()
        self._backup = Path(backup_path)
        self._ids    = source_ids
        self._dest   = Path(dest_root)

    def run(self):
        ok = True
        for src_id in self._ids:
            src = self._backup / src_id
            if not src.exists():
                self.progress.emit(f"⚠ {src_id}: não encontrado no backup")
                continue
            # find original path
            orig = next((s["path"] for s in SOURCES if s["id"] == src_id), None)
            dest = Path(orig) if orig else self._dest / src_id
            dest.mkdir(parents=True, exist_ok=True)
            self.progress.emit(f"Restaurando {src_id}...")
            try:
                p = subprocess.Popen(
                    ["rsync", "-a", "--info=progress2", str(src) + "/", str(dest) + "/"],
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
                )
                for line in p.stdout:
                    l = line.strip()
                    if l:
                        self.progress.emit(l[:80])
                p.wait()
                if p.returncode != 0:
                    ok = False
            except Exception as e:
                self.progress.emit(f"✗ {src_id}: {e}")
                ok = False
        self.done.emit(ok)


class KatuBackup(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Katu Backup")
        self.setMinimumSize(700, 580)
        self.resize(780, 620)
        self.setWindowIcon(QIcon("/usr/share/icons/hicolor/256x256/apps/katu-backup.png"))
        self._cfg = load_config()
        self._build_ui()

    def _build_ui(self):
        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)
        lay = QVBoxLayout(root)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        tabs = QTabWidget()
        tabs.addTab(self._build_backup_tab(),  "☁️  Fazer Backup")
        tabs.addTab(self._build_restore_tab(), "⬇️  Restaurar")
        lay.addWidget(tabs)

    def _build_backup_tab(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(14)

        title = QLabel("Selecione o que deseja salvar:")
        title.setStyleSheet(f"font-size:15px; font-weight:bold; color:{ui.TEXT};")
        lay.addWidget(title)

        self._source_checks = {}
        selected = self._cfg.get("sources", [])
        for src in SOURCES:
            cb = QCheckBox(f"{src['icon']}  {src['name']}  ({src['path']})")
            cb.setChecked(src["id"] in selected)
            cb.setStyleSheet(f"color:{ui.TEXT};")
            cb.stateChanged.connect(lambda _, s=src["id"], c=cb: self._toggle_source(s, c))
            self._source_checks[src["id"]] = cb
            lay.addWidget(cb)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"color:{ui.BORDER};")
        lay.addWidget(sep)

        dest_row = QHBoxLayout()
        dest_label = QLabel("Destino do backup:")
        dest_label.setStyleSheet(f"color:{ui.TEXT};")
        self._dest_input = QLineEdit(self._cfg.get("destination", str(HOME)))
        browse_btn = QPushButton("Escolher pasta")
        browse_btn.clicked.connect(self._browse_dest)
        dest_row.addWidget(dest_label)
        dest_row.addWidget(self._dest_input, 1)
        dest_row.addWidget(browse_btn)
        lay.addLayout(dest_row)

        self._backup_log = QPlainTextEdit()
        self._backup_log.setReadOnly(True)
        self._backup_log.setFixedHeight(100)
        self._backup_log.setVisible(False)
        lay.addWidget(self._backup_log)

        self._backup_btn = QPushButton("FAZER BACKUP AGORA")
        self._backup_btn.setObjectName("primary")
        self._backup_btn.setFixedHeight(44)
        self._backup_btn.clicked.connect(self._do_backup)
        lay.addWidget(self._backup_btn)
        lay.addStretch()
        return w

    def _build_restore_tab(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(14)

        title = QLabel("Selecione um backup para restaurar:")
        title.setStyleSheet(f"font-size:15px; font-weight:bold; color:{ui.TEXT};")
        lay.addWidget(title)

        self._backup_list = QListWidget()
        self._backup_list.setFixedHeight(180)
        self._backup_list.currentRowChanged.connect(self._on_backup_select)
        lay.addWidget(self._backup_list)
        self._refresh_backup_list()

        self._restore_sources_widget = QWidget()
        rs_lay = QVBoxLayout(self._restore_sources_widget)
        rs_lay.setContentsMargins(0, 0, 0, 0)
        rs_lay.addWidget(QLabel("Selecione o que restaurar:").setStyleSheet or QLabel("Selecione o que restaurar:"))
        lbl2 = QLabel("Selecione o que restaurar:")
        lbl2.setStyleSheet(f"color:{ui.TEXT};")
        rs_lay.addWidget(lbl2)
        self._restore_checks = {}
        for src in SOURCES:
            cb = QCheckBox(f"{src['icon']}  {src['name']}")
            cb.setChecked(True)
            cb.setStyleSheet(f"color:{ui.TEXT};")
            self._restore_checks[src["id"]] = cb
            rs_lay.addWidget(cb)
        self._restore_sources_widget.setVisible(False)
        lay.addWidget(self._restore_sources_widget)

        self._restore_log = QPlainTextEdit()
        self._restore_log.setReadOnly(True)
        self._restore_log.setFixedHeight(80)
        self._restore_log.setVisible(False)
        lay.addWidget(self._restore_log)

        self._restore_btn = QPushButton("RESTAURAR BACKUP")
        self._restore_btn.setObjectName("primary")
        self._restore_btn.setFixedHeight(44)
        self._restore_btn.setEnabled(False)
        self._restore_btn.clicked.connect(self._do_restore)
        lay.addWidget(self._restore_btn)
        lay.addStretch()
        return w

    def _toggle_source(self, src_id, cb):
        sources = self._cfg.get("sources", [])
        if cb.isChecked() and src_id not in sources:
            sources.append(src_id)
        elif not cb.isChecked() and src_id in sources:
            sources.remove(src_id)
        self._cfg["sources"] = sources
        save_config(self._cfg)

    def _browse_dest(self):
        d = QFileDialog.getExistingDirectory(self, "Selecionar destino do backup", str(HOME))
        if d:
            self._dest_input.setText(d)
            self._cfg["destination"] = d
            save_config(self._cfg)

    def _do_backup(self):
        selected_ids = [sid for sid, cb in self._source_checks.items() if cb.isChecked()]
        if not selected_ids:
            QMessageBox.warning(self, "Aviso", "Selecione pelo menos uma pasta para fazer backup.")
            return
        dest = self._dest_input.text().strip()
        if not dest or not Path(dest).exists():
            QMessageBox.warning(self, "Aviso", "Destino do backup não existe.")
            return
        srcs = [s for s in SOURCES if s["id"] in selected_ids]
        reply = QMessageBox.question(self, "Confirmar backup",
            f"Fazer backup de {len(srcs)} pasta(s) para:\n{dest}",
            QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        self._backup_btn.setEnabled(False)
        self._backup_log.setVisible(True)
        self._backup_log.clear()
        t = BackupThread(srcs, dest)
        t.progress.connect(lambda l: self._backup_log.appendPlainText(l))
        t.done.connect(self._on_backup_done)
        t.start()
        self._backup_thread = t

    def _on_backup_done(self, ok, path):
        self._backup_btn.setEnabled(True)
        if ok:
            QMessageBox.information(self, "Backup concluído", f"Backup salvo em:\n{path}")
            if CORE:
                notifications.notify_success("Katu Backup", "Backup concluído com sucesso.")
            self._refresh_backup_list()
        else:
            QMessageBox.warning(self, "Atenção", "Backup concluído com alguns erros. Verifique o log.")

    def _refresh_backup_list(self):
        self._backup_list.clear()
        dest = self._dest_input.text().strip() if hasattr(self, "_dest_input") else str(HOME)
        for b in list_backups(dest):
            item = QListWidgetItem(f"📦  {b.get('date', b.get('stamp','?'))}")
            item.setData(Qt.UserRole, b)
            self._backup_list.addItem(item)

    def _on_backup_select(self, row):
        self._restore_sources_widget.setVisible(row >= 0)
        self._restore_btn.setEnabled(row >= 0)
        if row >= 0:
            item = self._backup_list.item(row)
            if item:
                b = item.data(Qt.UserRole)
                avail = b.get("sources", [s["id"] for s in SOURCES])
                for sid, cb in self._restore_checks.items():
                    cb.setEnabled(sid in avail)
                    cb.setChecked(sid in avail)

    def _do_restore(self):
        item = self._backup_list.currentItem()
        if not item:
            return
        b = item.data(Qt.UserRole)
        selected_ids = [sid for sid, cb in self._restore_checks.items() if cb.isChecked() and cb.isEnabled()]
        if not selected_ids:
            QMessageBox.warning(self, "Aviso", "Selecione pelo menos um item.")
            return
        reply = QMessageBox.question(self, "Confirmar restauração",
            f"Restaurar {len(selected_ids)} item(s) do backup {b.get('date','?')}?\n\nIsso vai sobrescrever os arquivos atuais.",
            QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        self._restore_btn.setEnabled(False)
        self._restore_log.setVisible(True)
        self._restore_log.clear()
        t = RestoreThread(b["path"], selected_ids, str(HOME))
        t.progress.connect(lambda l: self._restore_log.appendPlainText(l))
        t.done.connect(self._on_restore_done)
        t.start()
        self._restore_thread = t

    def _on_restore_done(self, ok):
        self._restore_btn.setEnabled(True)
        if ok:
            QMessageBox.information(self, "Restauração concluída", "Arquivos restaurados com sucesso!")
        else:
            QMessageBox.warning(self, "Atenção", "Restauração concluída com erros. Verifique o log.")


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Katu Backup")
    if CORE:
        app.setStyleSheet(ui.STYLESHEET)
    win = KatuBackup()
    win.show()
    sys.exit(app.exec_() if QT == 'PyQt5' else app.exec())


if __name__ == "__main__":
    main()
