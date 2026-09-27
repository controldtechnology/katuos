"""Package management integration for Katu OS.

Wraps APT and Flatpak. Never executes arbitrary strings as commands.
All package names are validated before use.
"""
import re, subprocess
from typing import List, Tuple


_SAFE_PKG = re.compile(r"^[a-z0-9][a-z0-9.+\-]{0,127}$")
_SAFE_FLATPAK = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9.\-]{0,255}$")


def _validate_pkg(name: str) -> bool:
    return bool(_SAFE_PKG.match(name))


def _validate_flatpak(name: str) -> bool:
    return bool(_SAFE_FLATPAK.match(name))


def apt_update(callback=None):
    try:
        p = subprocess.Popen(
            ["pkexec", "apt-get", "update", "-q"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )
        for line in p.stdout:
            if callback:
                callback(line.rstrip())
        p.wait()
        return p.returncode == 0
    except Exception as e:
        return False


def apt_upgrade(callback=None):
    try:
        p = subprocess.Popen(
            ["pkexec", "apt-get", "upgrade", "-y", "-q"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )
        for line in p.stdout:
            if callback:
                callback(line.rstrip())
        p.wait()
        return p.returncode == 0
    except Exception:
        return False


def apt_install(package: str, callback=None) -> bool:
    if not _validate_pkg(package):
        return False
    try:
        p = subprocess.Popen(
            ["pkexec", "apt-get", "install", "-y", package],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )
        for line in p.stdout:
            if callback:
                callback(line.rstrip())
        p.wait()
        return p.returncode == 0
    except Exception:
        return False


def apt_remove(package: str, callback=None) -> bool:
    if not _validate_pkg(package):
        return False
    try:
        p = subprocess.Popen(
            ["pkexec", "apt-get", "remove", "-y", package],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )
        for line in p.stdout:
            if callback:
                callback(line.rstrip())
        p.wait()
        return p.returncode == 0
    except Exception:
        return False


def apt_is_installed(package: str) -> bool:
    if not _validate_pkg(package):
        return False
    try:
        out = subprocess.check_output(
            ["dpkg-query", "-W", "-f=${Status}", package],
            stderr=subprocess.DEVNULL, text=True
        )
        return "install ok installed" in out
    except Exception:
        return False


def apt_list_upgradable() -> List[Tuple[str, str, str]]:
    result = []
    try:
        out = subprocess.check_output(
            ["apt-get", "--simulate", "upgrade"],
            stderr=subprocess.DEVNULL, text=True
        )
        for line in out.splitlines():
            if line.startswith("Inst "):
                parts = line.split()
                name = parts[1] if len(parts) > 1 else ""
                ver = parts[2].strip("[]()") if len(parts) > 2 else ""
                result.append((name, ver, "apt"))
    except Exception:
        pass
    return result


def flatpak_install(app_id: str, callback=None) -> bool:
    if not _validate_flatpak(app_id):
        return False
    try:
        p = subprocess.Popen(
            ["flatpak", "install", "--noninteractive", "flathub", app_id],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )
        for line in p.stdout:
            if callback:
                callback(line.rstrip())
        p.wait()
        return p.returncode == 0
    except Exception:
        return False


def flatpak_remove(app_id: str, callback=None) -> bool:
    if not _validate_flatpak(app_id):
        return False
    try:
        p = subprocess.Popen(
            ["flatpak", "uninstall", "--noninteractive", app_id],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )
        for line in p.stdout:
            if callback:
                callback(line.rstrip())
        p.wait()
        return p.returncode == 0
    except Exception:
        return False


def flatpak_is_installed(app_id: str) -> bool:
    if not _validate_flatpak(app_id):
        return False
    try:
        out = subprocess.check_output(
            ["flatpak", "list", "--app", "--columns=application"],
            stderr=subprocess.DEVNULL, text=True
        )
        return app_id in out.splitlines()
    except Exception:
        return False


def flatpak_list_upgradable() -> List[Tuple[str, str, str]]:
    result = []
    try:
        out = subprocess.check_output(
            ["flatpak", "remote-ls", "--updates", "--columns=application,version"],
            stderr=subprocess.DEVNULL, text=True
        )
        for line in out.splitlines():
            parts = line.split()
            if parts:
                result.append((parts[0], parts[1] if len(parts) > 1 else "", "flatpak"))
    except Exception:
        pass
    return result


def flatpak_ensure_flathub():
    try:
        out = subprocess.check_output(
            ["flatpak", "remotes"], stderr=subprocess.DEVNULL, text=True
        )
        if "flathub" in out.lower():
            return True
        subprocess.run(
            ["flatpak", "remote-add", "--if-not-exists", "flathub",
             "https://dl.flathub.org/repo/flathub.flatpakrepo"],
            check=False
        )
        return True
    except Exception:
        return False
