#!/usr/bin/env python3
"""Katu Drivers — Driver Manager for Katu OS."""
import sys, subprocess, re
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
    from katu_core import ui, notifications
    from katu_core.packages import apt_install, apt_is_installed
    CORE = True
except ImportError:
    CORE = False
    class _FakeUI:
        STYLESHEET = ""; BG = "#0d1117"; SURFACE = "#161b22"; CARD = "#1c2128"
        BORDER = "#30363d"; ACCENT = "#00c853"; TEXT = "#e6edf3"; MUTED = "#8b949e"
        ERROR = "#f85149"; AMBER = "#ffab00"; SUCCESS = "#3fb950"; TEXT_INV = "#0d1117"
    ui = _FakeUI()
    def apt_install(p, cb=None): return False
    def apt_is_installed(p): return False
    class notifications:
        @staticmethod
        def notify_success(a, b=""): pass


def _run(cmd):
    try:
        return subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True).strip()
    except Exception:
        return ""


def detect_hardware():
    devices = []
    lspci = _run(["lspci", "-nn"])
    lsusb = _run(["lsusb"])
    rfkill = _run(["rfkill", "list"])
    iwconfig = _run(["iwconfig"])
    aplay = _run(["aplay", "-l"])
    lspci_lower = lspci.lower()

    # GPU
    gpu_line = ""
    for line in lspci.splitlines():
        if "vga" in line.lower() or "3d" in line.lower() or "display" in line.lower():
            gpu_line = line
            break
    gpu_desc = re.sub(r"^[0-9a-f:.]+ ", "", gpu_line).strip()
    gpu_status = "ok"
    gpu_pkg = None
    gpu_rec = None
    if "nvidia" in gpu_line.lower():
        if apt_is_installed("nvidia-driver"):
            gpu_status = "ok"
        else:
            gpu_status = "driver_available"
            gpu_pkg = "nvidia-driver"
            gpu_rec = "Driver NVIDIA proprietário recomendado"
    elif "amd" in gpu_line.lower() or "radeon" in gpu_line.lower():
        gpu_status = "ok"
        gpu_rec = "Driver AMD (amdgpu) incluído no kernel"
    elif "intel" in gpu_line.lower():
        gpu_status = "ok"
        gpu_rec = "Driver Intel (i915) incluído no kernel"

    devices.append({
        "type": "gpu", "icon": "🖥️", "name": "Placa de Vídeo",
        "detail": gpu_desc or "Desconhecida",
        "status": gpu_status, "pkg": gpu_pkg, "rec": gpu_rec or "Driver incluído no kernel",
    })

    # Wi-Fi
    wifi_ok = bool(iwconfig and "ESSID" in iwconfig or "wlan" in lspci_lower or "wireless" in lspci_lower)
    rfkill_blocked = "Soft blocked: yes" in rfkill
    devices.append({
        "type": "wifi", "icon": "📶", "name": "Wi-Fi",
        "detail": "Adaptador detectado" if wifi_ok else "Não detectado",
        "status": "blocked" if rfkill_blocked else ("ok" if wifi_ok else "not_found"),
        "pkg": None, "rec": "rfkill unblock wifi" if rfkill_blocked else "",
    })

    # Bluetooth
    bt_ok = "bluetooth" in _run(["hciconfig"]).lower() or apt_is_installed("bluetooth")
    devices.append({
        "type": "bt", "icon": "🔵", "name": "Bluetooth",
        "detail": "Disponível" if bt_ok else "Não detectado",
        "status": "ok" if bt_ok else "not_found",
        "pkg": "bluetooth" if not bt_ok else None, "rec": "",
    })

    # Áudio
    audio_ok = bool(aplay)
    devices.append({
        "type": "audio", "icon": "🔊", "name": "Áudio",
        "detail": "PipeWire/ALSA detectado" if audio_ok else "Não detectado",
        "status": "ok" if audio_ok else "not_found",
        "pkg": "pipewire-audio" if not audio_ok else None, "rec": "",
    })

    # Webcam
    webcam = Path("/dev/video0").exists()
    devices.append({
        "type": "webcam", "icon": "📷", "name": "Webcam",
        "detail": "/dev/video0 disponível" if webcam else "Não detectada",
        "status": "ok" if webcam else "not_found",
        "pkg": None, "rec": "",
    })

    return devices


class DetectThread(QThread):
    done = pyqtSignal(list)
    def run(self):
        self.done.emit(detect_hardware())


class InstallDriverThread(QThread):
    progress = pyqtSignal(str)
    done = pyqtSignal(bool)
    def __init__(self, pkg):
        super().__init__()
        self._pkg = pkg
    def run(self):
        ok = apt_install(self._pkg, self.progress.emit)
        self.done.emit(ok)


class DeviceRow(QFrame):
    install_requested = pyqtSignal(str)

    def __init__(self, device, parent=None):
        super().__init__(parent)
        self._dev = device
        self.setObjectName("devRow")
        self.setFixedHeight(72)
        self.setStyleSheet(f"QFrame#devRow{{background:{ui.CARD};border:1px solid {ui.BORDER};border-radius:10px;}}")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 8, 16, 8)
        lay.setSpacing(12)

        ico = QLabel(device["icon"])
        ico.setStyleSheet("font-size:22px;")
        ico.setFixedWidth(32)

        info = QVBoxLayout()
        info.setSpacing(2)
        name = QLabel(device["name"])
        name.setStyleSheet(f"font-weight:bold; color:{ui.TEXT};")
        detail = QLabel(device["detail"])
        detail.setStyleSheet(f"color:{ui.MUTED}; font-size:12px;")
        info.addWidget(name)
        info.addWidget(detail)

        status = device["status"]
        if status == "ok":
            st_lbl = QLabel("✓ OK")
            st_lbl.setStyleSheet(f"color:{ui.SUCCESS};")
        elif status == "driver_available":
            st_lbl = QPushButton("Instalar driver")
            st_lbl.setObjectName("primary")
            st_lbl.setFixedSize(120, 32)
            pkg = device.get("pkg", "")
            st_lbl.clicked.connect(lambda _, p=pkg: self.install_requested.emit(p))
        elif status == "blocked":
            st_lbl = QLabel("⚠ Bloqueado")
            st_lbl.setStyleSheet(f"color:{ui.AMBER};")
        else:
            st_lbl = QLabel("— Não detectado")
            st_lbl.setStyleSheet(f"color:{ui.MUTED};")

        lay.addWidget(ico)
        lay.addLayout(info, 1)
        lay.addWidget(st_lbl)


class KatuDrivers(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Katu Drivers")
        self.setMinimumSize(640, 500)
        self.resize(720, 560)
        self.setWindowIcon(QIcon("/usr/share/icons/hicolor/256x256/apps/katu-logo.png"))
        self._build_ui()
        QTimer.singleShot(300, self._detect)

    def _build_ui(self):
        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)
        lay = QVBoxLayout(root)
        lay.setContentsMargins(32, 32, 32, 32)
        lay.setSpacing(16)

        h = QHBoxLayout()
        ico = QLabel("🖥️")
        ico.setStyleSheet("font-size:32px;")
        info = QVBoxLayout()
        t = QLabel("Katu Drivers")
        t.setStyleSheet(f"font-size:20px; font-weight:bold; color:{ui.TEXT};")
        self._sub = QLabel("Detectando hardware...")
        self._sub.setStyleSheet(f"color:{ui.MUTED};")
        info.addWidget(t)
        info.addWidget(self._sub)
        h.addWidget(ico)
        h.addLayout(info, 1)
        lay.addLayout(h)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"color:{ui.BORDER};")
        lay.addWidget(sep)

        self._devices_widget = QWidget()
        self._devices_lay = QVBoxLayout(self._devices_widget)
        self._devices_lay.setContentsMargins(0, 0, 0, 0)
        self._devices_lay.setSpacing(10)
        self._devices_lay.addWidget(QLabel("Detectando hardware..."))
        lay.addWidget(self._devices_widget, 1)

        self._log = QPlainTextEdit()
        self._log.setReadOnly(True)
        self._log.setFixedHeight(80)
        self._log.setVisible(False)
        lay.addWidget(self._log)

        btn_row = QHBoxLayout()
        refresh_btn = QPushButton("Verificar novamente")
        refresh_btn.setObjectName("primary")
        refresh_btn.setFixedHeight(40)
        refresh_btn.clicked.connect(self._detect)
        btn_row.addWidget(refresh_btn)
        lay.addLayout(btn_row)

    def _detect(self):
        self._sub.setText("Detectando hardware...")
        t = DetectThread()
        t.done.connect(self._on_detected)
        t.start()
        self._det_thread = t

    def _on_detected(self, devices):
        for i in reversed(range(self._devices_lay.count())):
            w = self._devices_lay.itemAt(i).widget()
            if w:
                w.deleteLater()
        need_action = sum(1 for d in devices if d["status"] == "driver_available")
        if need_action:
            self._sub.setText(f"⚠ {need_action} driver(s) recomendado(s)")
        else:
            self._sub.setText("✓ Todos os dispositivos estão configurados")
        for dev in devices:
            row = DeviceRow(dev)
            row.install_requested.connect(self._install_driver)
            self._devices_lay.addWidget(row)
        self._devices_lay.addStretch()

    def _install_driver(self, pkg):
        reply = QMessageBox.question(self, "Instalar driver",
            f"Instalar driver '{pkg}'?\nFonte: repositório oficial Katu OS.",
            QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        self._log.setVisible(True)
        t = InstallDriverThread(pkg)
        t.progress.connect(lambda l: self._log.appendPlainText(l))
        t.done.connect(lambda ok: self._on_driver_done(pkg, ok))
        t.start()
        self._inst_thread = t

    def _on_driver_done(self, pkg, ok):
        if ok:
            QMessageBox.information(self, "Driver instalado",
                f"Driver '{pkg}' instalado com sucesso!\nReinicie o sistema para aplicar.")
        else:
            QMessageBox.warning(self, "Falha", f"Não foi possível instalar '{pkg}'.")
        self._detect()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Katu Drivers")
    if CORE:
        app.setStyleSheet(ui.STYLESHEET)
    win = KatuDrivers()
    win.show()
    sys.exit(app.exec_() if QT == 'PyQt5' else app.exec())


if __name__ == "__main__":
    main()
