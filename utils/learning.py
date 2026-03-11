"""
learning.py — Tracks manual overrides and improves automation decisions.
"""
import os, csv, json
from datetime import datetime
from collections import defaultdict
from utils.logger import get_logger, log_action

logger = get_logger(__name__)

LEARNING_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "learning_data")
OVERRIDE_FILE = os.path.join(LEARNING_DIR, "overrides.csv")
MODEL_FILE = os.path.join(LEARNING_DIR, "preference_model.json")
HEADERS = ["timestamp", "module", "original_action", "override_action", "target", "reason"]

def _ensure_dir():
    os.makedirs(LEARNING_DIR, exist_ok=True)

def record_override(module, original_action, override_action, target, reason=""):
    _ensure_dir()
    file_exists = os.path.isfile(OVERRIDE_FILE)
    with open(OVERRIDE_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "module": module, "original_action": original_action,
            "override_action": override_action, "target": target, "reason": reason
        })
    log_action("learning", "OVERRIDE", f"{module}:{target}")
    _build_model()

def load_overrides():
    if not os.path.isfile(OVERRIDE_FILE):
        return []
    with open(OVERRIDE_FILE, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def _build_model():
    overrides = load_overrides()
    model = defaultdict(lambda: defaultdict(int))
    for row in overrides:
        ext = os.path.splitext(row["target"])[-1].lower() or row["target"]
        key = f"{row['module']}::{ext}"
        model[key][row["override_action"]] += 1
    plain = {k: dict(v) for k, v in model.items()}
    _ensure_dir()
    with open(MODEL_FILE, "w") as f:
        json.dump(plain, f, indent=2)
    return plain

def load_model():
    if not os.path.isfile(MODEL_FILE):
        return {}
    with open(MODEL_FILE) as f:
        return json.load(f)

def suggest_action(module, target, default_action):
    model = load_model()
    ext = os.path.splitext(target)[-1].lower() or target
    key = f"{module}::{ext}"
    if key not in model:
        return default_action
    prefs = model[key]
    best = max(prefs, key=prefs.get)
    confidence = prefs[best] / sum(prefs.values())
    if confidence > 0.5 and best != default_action:
        return best
    return default_action

def get_stats():
    overrides = load_overrides()
    if not overrides:
        return {"total_overrides": 0}
    by_module = defaultdict(int)
    for row in overrides:
        by_module[row["module"]] += 1
    return {
        "total_overrides": len(overrides),
        "by_module": dict(by_module),
        "model_rules": len(load_model())
    }