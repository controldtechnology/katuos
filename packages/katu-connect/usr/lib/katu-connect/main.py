#!/usr/bin/env python3
"""Katu Connect — Device Connection Manager (wraps KDE Connect)."""
import sys, subprocess, json
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
    from katu_core import ui
    CORE = True
except ImportError:
    CORE = False
    class _FakeUI:
        STYLESHEET = ""; BG = "#0d1117"; SURFACE = "#161b22"; CARD = "#1c2128"
        BORDER = "#30363d"; ACCENT = "#00c853"; TEXT = "#e6edf3"; MUTED = "#8b949e"
        ERROR = "#f85149"; AMBER = "#ffab00"; SUCCESS = "#3fb950"
    ui = _FakeUI()


def _run(cmd):
    try:
        return subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True, timeout=5).strip()
    except Exception:
        return ""


def kde_connect_available():
    try:
        subprocess.check_output(["kdeconnect-cli", "--version"], stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False


def get_devices():
    devices = []
    out = _run(["kdeconnect-cli", "-l"])
    if not out:
        return devices
    for line in out.splitlines():
        if not line.strip():
            continue
        # Format: - Device Name: ID (type=phone/tablet, connected/disconnected)
        m_name = line.strip().lstrip("- ")
        parts = m_name.split(":")
        if len(parts) >= 2:
            name = parts[0].strip()
            rest = ":".join(parts[1:])
            dev_id_match = rest.split("(")
            dev_id = dev_id_match[0].strip()
            connected = "connected" in rest.lower() and "disconnected" not in rest.lower()
            dev_type = "phone"
            if "tablet" in rest.lower():
                dev_type = "tablet"
            elif "computer" in rest.lower() or "laptop" in rest.lower():
                dev_type = "computer"
            devices.append({
                "name": name,
                "id": dev_id,
                "connected": connected,
                "type": dev_type,
                "battery": _get_battery(dev_id) if connected else None,
            })
    return devices


def _get_battery(device_id):
    out = _run(["kdeconnect-cli", "-d", device_id, "--get-battery"])
    try:
        return int(out.strip().rstrip("%"))
    except Exception:
        return None


def send_file(device_id, filepath):
    try:
        subprocess.Popen(["kdeconnect-cli", "-d", device_id, "--share", filepath])
        return True
    except Exception:
        return False


def find_device(device_id):
    try:
        subprocess.Popen(["kdeconnect-cli", "-d", device_id, "--ring"])
        return True
    except Exception:
        return False


def send_sms(device_id, number, msg):
    try:
        subprocess.Popen(["kdeconnect-cli", "-d", device_id, "--send-sms", msg, "--destination", number])
        return True
    except Exception:
        return False


class ScanThread(QThread):
    done = pyqtSignal(list)
    def run(self):
        self.done.emit(get_devices())


class DeviceCard(QFrame):
    send_file_requested = pyqtSignal(str)
    find_requested = pyqtSignal(str)

    def __init__(self, device, parent=None):
        super().__init__(parent)
        self._dev = device
        self.setObjectName("devCard")
        self.setMinimumHeight(110)
        connected = device.get("connected", False)
        border_col = ui.SUCCESS if connected else ui.BORDER
        self.setStyleSheet(f"QFrame#devCard{{background:{ui.CARD};border:1px solid {border_col};border-radius:10px;}}")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(8)

        h = QHBoxLayout()
        type_icons = {"phone": "📱", "tablet": "📟", "computer": "💻"}
        ico = QLabel(type_icons.get(device.get("type", "phone"), "📱"))
        ico.setStyleSheet("font-size:28px;")
        info = QVBoxLayout()
        info.setSpacing(2)
        name = QLabel(device.get("name", "Dispositivo"))
        name.setStyleSheet(f"font-weight:bold; color:{ui.TEXT}; font-size:14px;")
        status = QLabel("● Conectado" if connected else "○ Desconectado")
        status.setStyleSheet(f"color:{ui.SUCCESS if connected else ui.MUTED}; font-size:12px;")
        info.addWidget(name)
        info.addWidget(status)
        bat = device.get("battery")
        if bat is not None:
            bat_lbl = QLabel(f"🔋 Bateria: {bat}%")
            bat_lbl.setStyleSheet(f"color:{ui.MUTED}; font-size:12px;")
            info.addWidget(bat_lbl)
        h.addWidget(ico)
        h.addLayout(info, 1)
        lay.addLayout(h)

        if connected:
            btn_row = QHBoxLayout()
            send_btn = QPushButton("Enviar arquivo")
            send_btn.setFixedHeight(32)
            send_btn.clicked.connect(lambda _, d=device["id"]: self.send_file_requested.emit(d))
            find_btn = QPushButton("Encontrar")
            find_btn.setFixedHeight(32)
            find_btn.clicked.connect(lambda _, d=device["id"]: self.find_requested.emit(d))
            btn_row.addWidget(send_btn)
            btn_row.addWidget(find_btn)
            lay.addLayout(btn_row)


class KatuConnect(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Katu Connect")
        self.setMinimumSize(600, 500)
        self.resize(680, 560)
        self.setWindowIcon(QIcon("/usr/share/icons/hicolor/256x256/apps/katu-logo.png"))
        self._build_ui()
        QTimer.singleShot(500, self._scan)

    def _build_ui(self):
        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)
        lay = QVBoxLayout(root)
        lay.setContentsMargins(32, 32, 32, 32)
        lay.setSpacing(16)

        h = QHBoxLayout()
        ico = QLabel("📱")
        ico.setStyleSheet("font-size:32px;")
        info = QVBoxLayout()
        t = QLabel("Katu Connect")
        t.setStyleSheet(f"font-size:20px; font-weight:bold; color:{ui.TEXT};")
        self._sub = QLabel("Conecte e gerencie seus dispositivos")
        self._sub.setStyleSheet(f"color:{ui.MUTED};")
        info.addWidget(t)
        info.addWidget(self._sub)
        h.addWidget(ico)
        h.addLayout(info, 1)
        lay.addLayout(h)

        if not kde_connect_available():
            warn = QFrame()
            warn.setStyleSheet(f"background:{ui.CARD};border:1px solid {ui.AMBER};border-radius:8px;padding:16px;")
            wl = QVBoxLayout(warn)
            wl.addWidget(QLabel("⚠ KDE Connect não está instalado.").setStyleSheet or QLabel("⚠ KDE Connect não está instalado."))
            wl_t = QLabel("⚠ KDE Connect não está instalado.")
            wl_t.setStyleSheet(f"color:{ui.AMBER}; font-weight:bold;")
            wl_sub = QLabel("Instale via: Katu Store → Utilitários → KDE Connect")
            wl_sub.setStyleSheet(f"color:{ui.MUTED};")
            wl.addWidget(wl_t)
            wl.addWidget(wl_sub)
            lay.addWidget(warn)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        self._devices_widget = QWidget()
        self._devices_lay = QVBoxLayout(self._devices_widget)
        self._devices_lay.setContentsMargins(0, 0, 0, 0)
        self._devices_lay.setSpacing(10)
        empty = QLabel("Escaneando dispositivos...")
        empty.setAlignment(Qt.AlignCenter)
        empty.setStyleSheet(f"color:{ui.MUTED};")
        self._devices_lay.addWidget(empty)
        self._devices_lay.addStretch()
        scroll.setWidget(self._devices_widget)
        lay.addWidget(scroll, 1)

        note = QLabel("💡 Instale o KDE Connect no seu smartphone para conectar.\nDisponível para Android e iOS.")
        note.setStyleSheet(f"color:{ui.MUTED}; font-size:12px;")
        note.setAlignment(Qt.AlignCenter)
        lay.addWidget(note)

        refresh_btn = QPushButton("Verificar dispositivos")
        refresh_btn.setObjectName("primary")
        refresh_btn.setFixedHeight(40)
        refresh_btn.clicked.connect(self._scan)
        lay.addWidget(refresh_btn)

        open_kde_btn = QPushButton("Abrir KDE Connect")
        open_kde_btn.setFixedHeight(36)
        open_kde_btn.clicked.connect(lambda: subprocess.Popen(["kdeconnect-app"]))
        lay.addWidget(open_kde_btn)

    def _scan(self):
        self._sub.setText("Verificando dispositivos...")
        t = ScanThread()
        t.done.connect(self._on_scan)
        t.start()
        self._scan_thread = t

    def _on_scan(self, devices):
        for i in reversed(range(self._devices_lay.count())):
            w = self._devices_lay.itemAt(i).widget()
            if w:
                w.deleteLater()
        if not devices:
            empty = QLabel("Nenhum dispositivo encontrado.\n\nCertifique-se de que o KDE Connect está instalado no smartphone\ne que ambos estão na mesma rede Wi-Fi.")
            empty.setAlignment(Qt.AlignCenter)
            empty.setWordWrap(True)
            empty.setStyleSheet(f"color:{ui.MUTED};")
            self._devices_lay.addWidget(empty)
        else:
            connected = sum(1 for d in devices if d.get("connected"))
            self._sub.setText(f"{len(devices)} dispositivo(s) — {connected} conectado(s)")
            for dev in devices:
                card = DeviceCard(dev)
                card.send_file_requested.connect(self._send_file)
                card.find_requested.connect(lambda d: find_device(d))
                self._devices_lay.addWidget(card)
        self._devices_lay.addStretch()

    def _send_file(self, device_id):
        f, _ = QFileDialog.getOpenFileName(self, "Selecionar arquivo para enviar")
        if f:
            send_file(device_id, f)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Katu Connect")
    if CORE:
        app.setStyleSheet(ui.STYLESHEET)
    win = KatuConnect()
    win.show()
    sys.exit(app.exec_() if QT == 'PyQt5' else app.exec())


if __name__ == "__main__":
    main()
