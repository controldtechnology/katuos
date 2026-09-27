"""System information for Katu OS applications."""
import os, platform, subprocess, re
from pathlib import Path


def _run(cmd, default=""):
    try:
        return subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True).strip()
    except Exception:
        return default


def get_katu_version():
    try:
        for line in Path("/etc/katu-release").read_text().splitlines():
            if line.startswith("KATU_VERSION="):
                return line.split("=", 1)[1].strip().strip('"')
    except Exception:
        pass
    try:
        for line in Path("/etc/os-release").read_text().splitlines():
            if line.startswith("VERSION="):
                return line.split("=", 1)[1].strip().strip('"')
    except Exception:
        pass
    return "1.0"


def get_os_info():
    info = {
        "name": "Katu OS",
        "version": get_katu_version(),
        "kernel": platform.release(),
        "arch": platform.machine(),
        "base": "Debian 13 Trixie",
        "hostname": platform.node(),
        "plasma": _get_plasma_version(),
    }
    return info


def _get_plasma_version():
    v = _run(["plasmashell", "--version"])
    m = re.search(r"[\d.]+", v)
    return m.group() if m else "6.x"


def get_cpu_info():
    model = ""
    cores = 0
    try:
        for line in Path("/proc/cpuinfo").read_text().splitlines():
            if line.startswith("model name") and not model:
                model = line.split(":", 1)[1].strip()
            if line.startswith("processor"):
                cores += 1
    except Exception:
        pass
    return {"model": model or platform.processor() or "Desconhecido", "cores": cores or os.cpu_count() or 1}


def get_memory_info():
    total_mb = avail_mb = 0
    try:
        for line in Path("/proc/meminfo").read_text().splitlines():
            if line.startswith("MemTotal:"):
                total_mb = int(line.split()[1]) // 1024
            elif line.startswith("MemAvailable:"):
                avail_mb = int(line.split()[1]) // 1024
    except Exception:
        pass
    used_mb = total_mb - avail_mb
    pct = int(used_mb * 100 / total_mb) if total_mb else 0
    return {"total_mb": total_mb, "used_mb": used_mb, "avail_mb": avail_mb, "percent": pct}


def get_disk_info():
    disks = []
    try:
        out = _run(["df", "-h", "--output=target,size,used,avail,pcent"])
        for line in out.splitlines()[1:]:
            parts = line.split()
            if len(parts) >= 5 and parts[0] in ("/", "/home", "/boot"):
                disks.append({
                    "mount": parts[0],
                    "size": parts[1],
                    "used": parts[2],
                    "avail": parts[3],
                    "percent": parts[4],
                })
    except Exception:
        pass
    return disks


def get_gpu_info():
    gpu = _run(["lspci"])
    for line in gpu.splitlines():
        if "VGA" in line or "3D" in line or "Display" in line:
            return re.sub(r"^.*?: ", "", line).strip()
    return "Desconhecido"


def get_network_status():
    try:
        out = _run(["nmcli", "-t", "-f", "STATE", "general"])
        connected = "connected" in out.lower()
        iface_out = _run(["nmcli", "-t", "-f", "DEVICE,TYPE,STATE", "device"])
        wifi = any("wifi" in l and "connected" in l for l in iface_out.splitlines())
        eth = any("ethernet" in l and "connected" in l for l in iface_out.splitlines())
        return {"connected": connected, "wifi": wifi, "ethernet": eth}
    except Exception:
        return {"connected": False, "wifi": False, "ethernet": False}


def get_bluetooth_status():
    try:
        out = _run(["bluetoothctl", "show"])
        powered = "Powered: yes" in out
        return {"available": True, "powered": powered}
    except Exception:
        return {"available": False, "powered": False}


def get_audio_status():
    try:
        out = _run(["pactl", "info"])
        return "PulseAudio" in out or "PipeWire" in out
    except Exception:
        return False


def get_pending_updates():
    try:
        out = _run(["apt-get", "--simulate", "upgrade"])
        m = re.search(r"(\d+) upgraded", out)
        return int(m.group(1)) if m else 0
    except Exception:
        return -1


def get_uptime():
    try:
        secs = float(Path("/proc/uptime").read_text().split()[0])
        h = int(secs // 3600)
        m = int((secs % 3600) // 60)
        if h > 0:
            return f"{h}h {m}min"
        return f"{m}min"
    except Exception:
        return "Desconhecido"
