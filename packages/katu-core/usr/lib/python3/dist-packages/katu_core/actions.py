"""Action Registry — closed set of safe actions for Katu AI.

SECURITY: No AI response text may be executed as a shell command.
All actions pass through this registry with explicit user confirmation.
"""
import subprocess
from typing import Callable, Dict, Any, Optional


ACTION_REGISTRY: Dict[str, Dict] = {
    "open_settings": {
        "label": "Abrir Configurações",
        "description": "Abre as configurações do sistema KDE",
        "requires_confirm": False,
        "requires_root": False,
        "handler": lambda p: subprocess.Popen(["systemsettings5"]),
    },
    "open_wifi": {
        "label": "Abrir Wi-Fi",
        "description": "Abre as configurações de rede",
        "requires_confirm": False,
        "requires_root": False,
        "handler": lambda p: subprocess.Popen(["plasma-nm"]),
    },
    "open_bluetooth": {
        "label": "Abrir Bluetooth",
        "description": "Abre as configurações de Bluetooth",
        "requires_confirm": False,
        "requires_root": False,
        "handler": lambda p: subprocess.Popen(["bluedevil-wizard"]),
    },
    "check_updates": {
        "label": "Verificar Atualizações",
        "description": "Abre o Katu Update para verificar atualizações",
        "requires_confirm": False,
        "requires_root": False,
        "handler": lambda p: subprocess.Popen(["katu-update"]),
    },
    "open_store": {
        "label": "Abrir Katu Store",
        "description": "Abre a loja de aplicativos",
        "requires_confirm": False,
        "requires_root": False,
        "handler": lambda p: subprocess.Popen(["katu-store"]),
    },
    "open_file_manager": {
        "label": "Abrir Gerenciador de Arquivos",
        "description": "Abre o Dolphin",
        "requires_confirm": False,
        "requires_root": False,
        "handler": lambda p: subprocess.Popen(["dolphin"]),
    },
    "show_disk_usage": {
        "label": "Ver Uso do Disco",
        "description": "Abre informações de armazenamento",
        "requires_confirm": False,
        "requires_root": False,
        "handler": lambda p: subprocess.Popen(["katu-diagnostic"]),
    },
    "open_backup": {
        "label": "Abrir Backup",
        "description": "Abre o Katu Backup",
        "requires_confirm": False,
        "requires_root": False,
        "handler": lambda p: subprocess.Popen(["katu-backup"]),
    },
    "run_diagnostic": {
        "label": "Executar Diagnóstico",
        "description": "Abre o Katu Diagnostic",
        "requires_confirm": False,
        "requires_root": False,
        "handler": lambda p: subprocess.Popen(["katu-diagnostic"]),
    },
    "open_central": {
        "label": "Abrir Katu Central",
        "description": "Abre o painel central do Katu OS",
        "requires_confirm": False,
        "requires_root": False,
        "handler": lambda p: subprocess.Popen(["katu-central"]),
    },
    "install_package": {
        "label": "Instalar aplicativo",
        "description": "Instala um pacote via Flatpak ou APT (requer confirmação)",
        "requires_confirm": True,
        "requires_root": True,
        "params": {"package": str, "source": str},
        "handler": lambda p: None,  # handled by caller with UI confirmation
    },
    "empty_trash": {
        "label": "Esvaziar Lixeira",
        "description": "Esvazia a lixeira do usuário",
        "requires_confirm": True,
        "requires_root": False,
        "handler": lambda p: subprocess.Popen(["kioclient5", "empty", "trash:/"]),
    },
}


def get_action(action_id: str) -> Optional[Dict]:
    return ACTION_REGISTRY.get(action_id)


def execute_action(action_id: str, params: Dict = None, confirmed: bool = False) -> bool:
    action = get_action(action_id)
    if not action:
        return False
    if action.get("requires_confirm") and not confirmed:
        return False
    try:
        action["handler"](params or {})
        return True
    except Exception:
        return False


def list_actions() -> list:
    return [
        {"id": k, "label": v["label"], "description": v["description"],
         "requires_confirm": v.get("requires_confirm", False)}
        for k, v in ACTION_REGISTRY.items()
    ]
