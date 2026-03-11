import os, csv
from datetime import datetime, date
from collections import defaultdict
from utils.logger import get_logger, read_action_log

logger = get_logger(__name__)
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "..", "reports", "daily")
HEADERS = ["date", "module", "action", "count", "details"]

def _ensure_dir():
    os.makedirs(REPORTS_DIR, exist_ok=True)

def generate_daily_report(target_date=None):
    _ensure_dir()
    target_date = target_date or date.today().isoformat()
    records = [r for r in read_action_log() if r.get("timestamp","").startswith(target_date)]
    agg = defaultdict(lambda: {"count": 0, "details": []})
    for row in records:
        key = (row.get("module","unknown"), row.get("action","unknown"))
        agg[key]["count"] += 1
        agg[key]["details"].append(row.get("detail",""))
    report_path = os.path.join(REPORTS_DIR, f"{target_date}.csv")
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
        for (module, action), data in sorted(agg.items()):
            writer.writerow({
                "date": target_date, "module": module, "action": action,
                "count": data["count"], "details": " | ".join(data["details"][:5])
            })
    logger.info(f"Report: {report_path}")
    return report_path

def get_report(target_date=None):
    target_date = target_date or date.today().isoformat()
    path = os.path.join(REPORTS_DIR, f"{target_date}.csv")
    if not os.path.isfile(path):
        generate_daily_report(target_date)
    if not os.path.isfile(path):
        return []
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))

def get_summary_stats(target_date=None):
    rows = get_report(target_date)
    if not rows:
        return {"date": target_date, "total_actions": 0}
    by_module, by_action = defaultdict(int), defaultdict(int)
    for row in rows:
        by_module[row["module"]] += int(row["count"])
        by_action[row["action"]] += int(row["count"])
    return {
        "date": target_date or date.today().isoformat(),
        "total_actions": sum(int(r["count"]) for r in rows),
        "by_module": dict(by_module),
        "by_action": dict(by_action)
    }

def list_reports():
    _ensure_dir()
    return sorted([f.replace(".csv","") for f in os.listdir(REPORTS_DIR) if f.endswith(".csv")])