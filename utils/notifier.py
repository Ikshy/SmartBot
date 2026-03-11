import os, json, smtplib, threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from utils.logger import get_logger

logger = get_logger(__name__)
_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "notifier.json")

def _load_config():
    with open(_CONFIG_PATH) as f:
        return json.load(f)

def _desktop(title, message, timeout=10):
    try:
        from plyer import notification
        notification.notify(title=title, message=message, app_name="SmartBot", timeout=timeout)
    except Exception as e:
        logger.error(f"Desktop notify failed: {e}")

def _email(subject, body, cfg):
    try:
        msg = MIMEMultipart()
        msg["From"] = cfg["sender"]
        msg["To"] = cfg["recipient"]
        msg["Subject"] = f"[SmartBot] {subject}"
        msg.attach(MIMEText(body, "plain"))
        with smtplib.SMTP(cfg["smtp_host"], cfg["smtp_port"]) as s:
            if cfg.get("use_tls"):
                s.starttls()
            s.login(cfg["sender"], cfg["password"])
            s.send_message(msg)
    except Exception as e:
        logger.error(f"Email notify failed: {e}")

def _slack(title, message, cfg):
    try:
        import requests
        resp = requests.post(cfg["webhook_url"], json={
            "username": cfg.get("username", "SmartBot"),
            "text": f"*{title}*\n{message}",
            "channel": cfg.get("channel", "")
        }, timeout=5)
        resp.raise_for_status()
    except Exception as e:
        logger.error(f"Slack notify failed: {e}")

def send(title, message, level="info", force_channels=None):
    try:
        cfg = _load_config()
    except FileNotFoundError:
        return
    if not cfg.get("levels", {}).get(level, True):
        return
    channels = force_channels or []
    if not channels:
        if cfg.get("desktop", {}).get("enabled"): channels.append("desktop")
        if cfg.get("email", {}).get("enabled"): channels.append("email")
        if cfg.get("slack", {}).get("enabled"): channels.append("slack")
    for ch in channels:
        if ch == "desktop":
            threading.Thread(target=_desktop, args=(title, message), daemon=True).start()
        elif ch == "email":
            threading.Thread(target=_email, args=(title, message, cfg.get("email", {})), daemon=True).start()
        elif ch == "slack":
            threading.Thread(target=_slack, args=(title, message, cfg.get("slack", {})), daemon=True).start()

def info(title, message):    send(title, message, "info")
def warning(title, message): send(title, message, "warning")
def error(title, message):   send(title, message, "error")
def success(title, message): send(title, message, "success")