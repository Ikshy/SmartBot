"""
logger.py — Centralized logging system.
"""
import logging, csv, os
from datetime import datetime
from logging.handlers import RotatingFileHandler

LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "logs")
LOG_FILE = os.path.join(LOG_DIR, "smartbot.log")
CSV_LOG_FILE = os.path.join(LOG_DIR, "actions.csv")
CSV_HEADERS = ["timestamp", "level", "module", "action", "detail"]

def _ensure_log_dir():
    os.makedirs(LOG_DIR, exist_ok=True)

def get_logger(name: str) -> logging.Logger:
    _ensure_log_dir()
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)-8s %(name)s — %(message)s", "%H:%M:%S"))
    fh = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=3)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"))
    logger.addHandler(ch)
    logger.addHandler(fh)
    return logger

def log_action(module, action, detail, level="INFO"):
    _ensure_log_dir()
    file_exists = os.path.isfile(CSV_LOG_FILE)
    with open(CSV_LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "level": level, "module": module, "action": action, "detail": detail
        })

def read_action_log() -> list:
    if not os.path.isfile(CSV_LOG_FILE):
        return []
    with open(CSV_LOG_FILE, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))