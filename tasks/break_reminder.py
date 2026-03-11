
import json, os
from utils import get_logger, log_action, info

logger = get_logger(__name__)
_CFG = os.path.join(os.path.dirname(__file__), "..", "config", "config.json")

def run():
    cfg = json.load(open(_CFG))
    msg = cfg.get("break_reminder", {}).get("message", "Time to take a break!")
    info("SmartBot — Break Reminder", msg)
    log_action("break_reminder", "SENT", msg)
    return {"status": "sent", "message": msg}