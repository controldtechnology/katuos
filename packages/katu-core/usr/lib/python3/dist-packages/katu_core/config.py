"""Configuration management for Katu OS applications."""
import json, os
from pathlib import Path


class KatuConfig:
    def __init__(self, app_name: str):
        self._path = Path.home() / ".config" / "katu" / app_name / "config.json"
        self._data = {}
        self._load()

    def _load(self):
        try:
            if self._path.exists():
                self._data = json.loads(self._path.read_text())
        except Exception:
            self._data = {}

    def save(self):
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(self._data, indent=2, ensure_ascii=False))

    def get(self, key: str, default=None):
        return self._data.get(key, default)

    def set(self, key: str, value):
        self._data[key] = value
        self.save()

    def delete(self, key: str):
        self._data.pop(key, None)
        self.save()

    def all(self) -> dict:
        return dict(self._data)


def get_first_boot_flag(app_name: str) -> Path:
    return Path.home() / ".config" / "katu" / app_name / ".first-boot-done"


def mark_first_boot_done(app_name: str):
    flag = get_first_boot_flag(app_name)
    flag.parent.mkdir(parents=True, exist_ok=True)
    flag.touch()


def is_first_boot(app_name: str) -> bool:
    return not get_first_boot_flag(app_name).exists()


def is_live_session() -> bool:
    try:
        import subprocess
        out = subprocess.check_output(["id", "-un"], text=True).strip()
        return out in ("katu", "user", "live")
    except Exception:
        return False
