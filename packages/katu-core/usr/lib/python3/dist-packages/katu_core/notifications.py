"""Desktop notifications for Katu OS applications."""
import subprocess


def notify(title: str, body: str = "", icon: str = "katu-logo", urgency: str = "normal"):
    try:
        subprocess.Popen([
            "notify-send",
            "--app-name=Katu OS",
            f"--icon={icon}",
            f"--urgency={urgency}",
            title,
            body,
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass


def notify_info(title: str, body: str = ""):
    notify(title, body, icon="dialog-information", urgency="normal")


def notify_warning(title: str, body: str = ""):
    notify(title, body, icon="dialog-warning", urgency="normal")


def notify_error(title: str, body: str = ""):
    notify(title, body, icon="dialog-error", urgency="critical")


def notify_success(title: str, body: str = ""):
    notify(title, body, icon="katu-logo", urgency="low")
