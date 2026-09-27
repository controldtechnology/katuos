#!/usr/bin/env python3
"""Katu Diagnostic — System Health Check for Katu OS."""
import sys, os, subprocess, re
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

sys.path.insert(0, '/usr/lib/python3/dist-packages')
try:
    from katu_core import ui, system
    CORE = True
except ImportError:
    CORE = False
    class _FakeUI:
        STYLESHEET = ""; BG = "#0d1117"; SURFACE = "#161b22"; CARD = "#1c2128"
        BORDER = "#30363d"; ACCENT = "#00c853"; TEXT = "#e6edf3"; MUTED = "#8b949e"
        ERROR = "#f85149"; AMBER = "#ffab00"; SUCCESS = "#3fb950"; TEXT_INV = "#0d1117"
    ui = _FakeUI()
    class system:
        @staticmethod
        def get_memory_info(): return {}
        @staticmethod
        def get_disk_info(): return []
        @staticmethod
        def get_network_status(): return {}
        @staticmethod
        def get_bluetooth_status(): return {}
        @staticmethod
        def get_audio_status(): return False
        @staticmethod
        def get_pending_updates(): return -1


def _run(cmd, default=""):
    try:
        return subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True, timeout=10).strip()
    except Exception:
        return default


STATUS_OK   = "ok"
STATUS_WARN = "warn"
STATUS_FAIL = "fail"
STATUS_NA   = "na"


def run_all_checks():
    results = []

    # CPU
    try:
        load = os.getloadavg()
        cpus = os.cpu_count() or 1
        pct  = load[0] / cpus * 100
        status = STATUS_FAIL if pct > 90 else STATUS_WARN if pct > 70 else STATUS_OK
        results.append({
            "name": "Processador",
            "icon": "🧠",
            "status": status,
            "detail": f"Carga: {pct:.0f}% ({load[0]:.2f} / {cpus} núcleos)",
            "tip": "Carga muito alta. Feche programas desnecessários." if pct > 90 else "",
        })
    except Exception:
        results.append({"name": "Processador", "icon": "🧠", "status": STATUS_NA, "detail": "Não disponível", "tip": ""})

    # RAM
    try:
        mem = system.get_memory_info()
        pct = mem.get("percent", 0)
        total_gb = mem.get("total_mb", 0) / 1024
        avail_gb = mem.get("avail_mb", 0) / 1024
        status = STATUS_FAIL if pct > 90 else STATUS_WARN if pct > 75 else STATUS_OK
        results.append({
            "name": "Memória RAM",
            "icon": "💾",
            "status": status,
            "detail": f"{avail_gb:.1f} GB livres de {total_gb:.1f} GB ({pct}% em uso)",
            "tip": "Memória quase esgotada." if pct > 90 else "",
        })
    except Exception:
        results.append({"name": "Memória RAM", "icon": "💾", "status": STATUS_NA, "detail": "Não disponível", "tip": ""})

    # Disk
    try:
        disks = system.get_disk_info()
        for d in disks:
            pct_str = d.get("percent", "0%").rstrip("%")
            pct = int(pct_str) if pct_str.isdigit() else 0
            status = STATUS_FAIL if pct > 90 else STATUS_WARN if pct > 80 else STATUS_OK
            results.append({
                "name": f"Armazenamento ({d['mount']})",
                "icon": "💿",
                "status": status,
                "detail": f"{d['used']} usados / {d['size']} total ({d['avail']} livres)",
                "tip": "Disco quase cheio! Libere espaço." if pct > 90 else "",
            })
    except Exception:
        results.append({"name": "Armazenamento", "icon": "💿", "status": STATUS_NA, "detail": "Não disponível", "tip": ""})

    # Network
    try:
        net = system.get_network_status()
        connected = net.get("connected", False)
        # Test DNS
        dns_ok = False
        try:
            import socket
            socket.setdefaulttimeout(3)
            socket.getaddrinfo("debian.org", 80)
            dns_ok = True
        except Exception:
            pass
        if not connected:
            status = STATUS_WARN
            detail = "Sem conexão com a internet"
        elif not dns_ok:
            status = STATUS_WARN
            detail = "Conectado mas DNS não resolve"
        else:
            kind = "Wi-Fi" if net.get("wifi") else "Ethernet"
            status = STATUS_OK
            detail = f"Conectado via {kind}"
        results.append({
            "name": "Rede",
            "icon": "🌐",
            "status": status,
            "detail": detail,
            "tip": "Verifique o cabo ou Wi-Fi." if not connected else "",
        })
    except Exception:
        results.append({"name": "Rede", "icon": "🌐", "status": STATUS_NA, "detail": "Não disponível", "tip": ""})

    # Audio
    try:
        audio_ok = system.get_audio_status()
        results.append({
            "name": "Áudio",
            "icon": "🔊",
            "status": STATUS_OK if audio_ok else STATUS_WARN,
            "detail": "PipeWire/PulseAudio ativo" if audio_ok else "Serviço de áudio não detectado",
            "tip": "Tente reiniciar o PipeWire." if not audio_ok else "",
        })
    except Exception:
        results.append({"name": "Áudio", "icon": "🔊", "status": STATUS_NA, "detail": "Não disponível", "tip": ""})

    # Bluetooth
    try:
        bt = system.get_bluetooth_status()
        results.append({
            "name": "Bluetooth",
            "icon": "🔵",
            "status": STATUS_OK if bt.get("available") else STATUS_NA,
            "detail": ("Ativo" if bt.get("powered") else "Disponível mas desligado") if bt.get("available") else "Não disponível neste computador",
            "tip": "",
        })
    except Exception:
        results.append({"name": "Bluetooth", "icon": "🔵", "status": STATUS_NA, "detail": "Não disponível", "tip": ""})

    # Updates
    try:
        upd = system.get_pending_updates()
        if upd == 0:
            status = STATUS_OK
            detail = "Sistema atualizado"
            tip = ""
        elif upd > 0:
            status = STATUS_WARN
            detail = f"{upd} atualização(ões) pendente(s)"
            tip = "Execute o Katu Update."
        else:
            status = STATUS_NA
            detail = "Não verificado"
            tip = ""
        results.append({"name": "Atualizações", "icon": "🔄", "status": status, "detail": detail, "tip": tip})
    except Exception:
        results.append({"name": "Atualizações", "icon": "🔄", "status": STATUS_NA, "detail": "Não verificado", "tip": ""})

    # Firewall
    try:
        ufw_out = _run(["ufw", "status"])
        fw_ok = "active" in ufw_out.lower()
        results.append({
            "name": "Firewall",
            "icon": "🔒",
            "status": STATUS_OK if fw_ok else STATUS_WARN,
            "detail": "UFW ativo e configurado" if fw_ok else "UFW inativo",
            "tip": "Ative o firewall: sudo ufw enable" if not fw_ok else "",
        })
    except Exception:
        results.append({"name": "Firewall", "icon": "🔒", "status": STATUS_NA, "detail": "Não verificado", "tip": ""})

    # Failed services
    try:
        failed = _run(["systemctl", "--failed", "--no-legend"])
        n_failed = len([l for l in failed.splitlines() if l.strip()])
        results.append({
            "name": "Serviços do sistema",
            "icon": "⚙️",
            "status": STATUS_FAIL if n_failed > 0 else STATUS_OK,
            "detail": f"{n_failed} serviço(s) com falha" if n_failed > 0 else "Todos os serviços ativos",
            "tip": "Execute 'systemctl --failed' para detalhes." if n_failed > 0 else "",
        })
    except Exception:
        results.append({"name": "Serviços", "icon": "⚙️", "status": STATUS_NA, "detail": "Não verificado", "tip": ""})

    return results


class DiagThread(QThread):
    done = pyqtSignal(list)
    def run(self):
        self.done.emit(run_all_checks())


class ResultRow(QFrame):
    def __init__(self, check, parent=None):
        super().__init__(parent)
        self.setObjectName("resultRow")
        self.setFixedHeight(64)
        colors = {STATUS_OK: ui.SUCCESS, STATUS_WARN: ui.AMBER, STATUS_FAIL: ui.ERROR, STATUS_NA: ui.MUTED}
        icons  = {STATUS_OK: "✓", STATUS_WARN: "⚠", STATUS_FAIL: "✗", STATUS_NA: "—"}
        status = check.get("status", STATUS_NA)
        color  = colors.get(status, ui.MUTED)
        border_col = color if status != STATUS_NA else ui.BORDER
        self.setStyleSheet(f"QFrame#resultRow{{background:{ui.CARD};border:1px solid {border_col};border-radius:8px;}}")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 8, 16, 8)
        lay.setSpacing(12)
        icon_lbl = QLabel(check.get("icon", ""))
        icon_lbl.setFixedWidth(28)
        icon_lbl.setStyleSheet("font-size:18px;")
        info = QVBoxLayout()
        info.setSpacing(2)
        name = QLabel(check.get("name", ""))
        name.setStyleSheet(f"font-weight:bold; color:{ui.TEXT}; font-size:13px;")
        detail = QLabel(check.get("detail", ""))
        detail.setStyleSheet(f"color:{ui.MUTED}; font-size:12px;")
        info.addWidget(name)
        info.addWidget(detail)
        status_lbl = QLabel(f"{icons[status]}  ")
        status_lbl.setStyleSheet(f"color:{color}; font-size:18px; font-weight:bold;")
        lay.addWidget(icon_lbl)
        lay.addLayout(info, 1)
        lay.addWidget(status_lbl)


class KatuDiagnostic(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Katu Diagnostic")
        self.setMinimumSize(660, 560)
        self.resize(720, 620)
        self.setWindowIcon(QIcon("/usr/share/icons/hicolor/256x256/apps/katu-logo.png"))
        self._build_ui()

    def _build_ui(self):
        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)
        lay = QVBoxLayout(root)
        lay.setContentsMargins(32, 32, 32, 32)
        lay.setSpacing(16)

        h = QHBoxLayout()
        ico = QLabel("🔍")
        ico.setStyleSheet("font-size:32px;")
        info = QVBoxLayout()
        t = QLabel("Katu Diagnostic")
        t.setStyleSheet(f"font-size:20px; font-weight:bold; color:{ui.TEXT};")
        self._sub = QLabel("Verifique a saúde do seu computador")
        self._sub.setStyleSheet(f"color:{ui.MUTED};")
        info.addWidget(t)
        info.addWidget(self._sub)
        h.addWidget(ico)
        h.addLayout(info, 1)
        lay.addLayout(h)

        btn = QPushButton("VERIFICAR MEU COMPUTADOR")
        btn.setObjectName("primary")
        btn.setFixedHeight(48)
        btn.clicked.connect(self._run_check)
        lay.addWidget(btn)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"color:{ui.BORDER};")
        lay.addWidget(sep)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        self._results_widget = QWidget()
        self._results_lay = QVBoxLayout(self._results_widget)
        self._results_lay.setContentsMargins(0, 0, 0, 0)
        self._results_lay.setSpacing(8)
        empty = QLabel("Clique em 'VERIFICAR MEU COMPUTADOR' para começar.")
        empty.setAlignment(Qt.AlignCenter)
        empty.setStyleSheet(f"color:{ui.MUTED}; font-size:13px;")
        self._results_lay.addWidget(empty)
        self._results_lay.addStretch()
        scroll.setWidget(self._results_widget)
        lay.addWidget(scroll, 1)

        self._summary = QLabel("")
        self._summary.setAlignment(Qt.AlignCenter)
        self._summary.setStyleSheet(f"font-size:14px; color:{ui.TEXT};")
        lay.addWidget(self._summary)

    def _run_check(self):
        self._sub.setText("Verificando...")
        self._summary.setText("")
        for i in reversed(range(self._results_lay.count())):
            w = self._results_lay.itemAt(i).widget()
            if w:
                w.deleteLater()
        loading = QLabel("Verificando componentes do sistema...")
        loading.setAlignment(Qt.AlignCenter)
        loading.setStyleSheet(f"color:{ui.MUTED};")
        self._results_lay.addWidget(loading)
        t = DiagThread()
        t.done.connect(self._on_done)
        t.start()
        self._thread = t

    def _on_done(self, results):
        for i in reversed(range(self._results_lay.count())):
            w = self._results_lay.itemAt(i).widget()
            if w:
                w.deleteLater()
        n_ok   = sum(1 for r in results if r["status"] == STATUS_OK)
        n_warn = sum(1 for r in results if r["status"] == STATUS_WARN)
        n_fail = sum(1 for r in results if r["status"] == STATUS_FAIL)
        for r in results:
            row = ResultRow(r)
            self._results_lay.addWidget(row)
            if r.get("tip"):
                tip = QLabel(f"  💡 {r['tip']}")
                tip.setStyleSheet(f"color:{ui.AMBER}; font-size:12px; padding-left:48px;")
                self._results_lay.addWidget(tip)
        self._results_lay.addStretch()

        if n_fail > 0:
            self._sub.setText(f"✗ {n_fail} problema(s) encontrado(s)")
            self._summary.setText(f"✗ {n_fail} problema(s) crítico(s) | ⚠ {n_warn} aviso(s) | ✓ {n_ok} OK")
        elif n_warn > 0:
            self._sub.setText(f"⚠ {n_warn} aviso(s)")
            self._summary.setText(f"⚠ {n_warn} item(ns) precisam de atenção | ✓ {n_ok} OK")
        else:
            self._sub.setText("✓ Tudo funcionando bem!")
            self._summary.setText(f"✓ {n_ok} verificações passaram sem problemas")


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Katu Diagnostic")
    if CORE:
        app.setStyleSheet(ui.STYLESHEET)
    win = KatuDiagnostic()
    win.show()
    sys.exit(app.exec_() if QT == 'PyQt5' else app.exec())


if __name__ == "__main__":
    main()
