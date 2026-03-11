
import json, os
from utils.file_ops import organize_folder
from utils.learning import suggest_action
from utils import get_logger, log_action, success

logger = get_logger(__name__)
_CFG = os.path.join(os.path.dirname(__file__), "..", "config", "config.json")

def run():
    cfg = json.load(open(_CFG))
    watch = cfg["paths"]["watch_folder"]
    target = cfg["paths"]["organize_target"]
    preferred = suggest_action("file_organizer", watch, target)
    summary = organize_folder(watch, preferred)
    if summary:
        total = sum(len(v) for v in summary.values())
        details = ", ".join(f"{k}:{len(v)}" for k, v in summary.items())
        success("SmartBot", f"Moved {total} files: {details}")
        log_action("file_organizer", "COMPLETE", details)
    return summary