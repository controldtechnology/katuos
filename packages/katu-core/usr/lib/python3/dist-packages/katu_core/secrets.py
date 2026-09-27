"""Secure storage for API keys and sensitive configuration.

Keys are stored in ~/.config/katu/secrets/ with permissions 600.
Never stored in the system, ISO, or git repository.
"""
import json, os, stat
from pathlib import Path


_SECRETS_DIR = Path.home() / ".config" / "katu" / "secrets"


def _secrets_file(service: str) -> Path:
    return _SECRETS_DIR / f"{service}.json"


def _ensure_dir():
    _SECRETS_DIR.mkdir(parents=True, exist_ok=True)
    _SECRETS_DIR.chmod(0o700)


def store_secret(service: str, key: str, value: str):
    _ensure_dir()
    f = _secrets_file(service)
    data = {}
    if f.exists():
        try:
            data = json.loads(f.read_text())
        except Exception:
            data = {}
    data[key] = value
    f.write_text(json.dumps(data))
    f.chmod(0o600)


def get_secret(service: str, key: str, default: str = "") -> str:
    f = _secrets_file(service)
    if not f.exists():
        return default
    try:
        data = json.loads(f.read_text())
        return data.get(key, default)
    except Exception:
        return default


def delete_secret(service: str, key: str = None):
    f = _secrets_file(service)
    if key is None:
        f.unlink(missing_ok=True)
        return
    if not f.exists():
        return
    try:
        data = json.loads(f.read_text())
        data.pop(key, None)
        f.write_text(json.dumps(data))
        f.chmod(0o600)
    except Exception:
        pass


def has_secret(service: str, key: str) -> bool:
    val = get_secret(service, key)
    return bool(val and val.strip())


def mask_key(key: str) -> str:
    if not key or len(key) < 8:
        return "••••••••"
    return key[:4] + "••••" + key[-4:]
