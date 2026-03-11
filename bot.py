"""
bot.py — SmartBot main orchestrator.
"""
import json, os, sys, time, schedule, threading
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils.logger import get_logger, log_action
from utils.reports import generate_daily_report
import utils.notifier as notifier

logger = get_logger("SmartBot")
SCHEDULER_CONFIG = os.path.join("config", "scheduler.json")

def _load_task(name):
    import importlib
    try:
        return importlib.import_module(f"tasks.{name}")
    except ImportError as e:
        logger.error(f"Could not load task '{name}': {e}")
        return None

def _safe_run(task_name, task_module):
    def wrapper():
        logger.info(f"Running task: {task_name}")
        start = time.time()
        try:
            result = task_module.run()
            elapsed = time.time() - start
            log_action("bot", f"TASK_COMPLETE:{task_name}", f"{elapsed:.2f}s")
            logger.info(f"Task {task_name} done in {elapsed:.2f}s | {result}")
        except Exception as e:
            logger.error(f"Task {task_name} failed: {e}", exc_info=True)
            log_action("bot", f"TASK_ERROR:{task_name}", str(e), level="ERROR")
            notifier.error("SmartBot - Task Error", f"{task_name} failed: {e}")
    return wrapper

def _register_tasks(cfg):
    tasks_cfg = cfg.get("tasks", {})
    intervals = cfg.get("intervals", {})
    for task_name, task_cfg in tasks_cfg.items():
        if not task_cfg.get("enabled", False):
            continue
        module = _load_task(task_name)
        if module is None:
            continue
        runner = _safe_run(task_name, module)
        interval_key = task_cfg.get("interval", "hourly")
        run_time = task_cfg.get("time")
        if interval_key == "daily" and run_time:
            schedule.every().day.at(run_time).do(runner)
        else:
            minutes = intervals.get(interval_key, 60)
            schedule.every(minutes).minutes.do(runner)
        threading.Thread(target=runner, daemon=True).start()
        logger.info(f"Registered: {task_name}")

def main():
    logger.info(f"SmartBot starting — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if not os.path.isfile(SCHEDULER_CONFIG):
        logger.error(f"Scheduler config not found: {SCHEDULER_CONFIG}")
        sys.exit(1)
    with open(SCHEDULER_CONFIG) as f:
        cfg = json.load(f)
    _register_tasks(cfg)
    schedule.every().day.at("23:59").do(generate_daily_report)
    notifier.info("SmartBot Started", f"{len(schedule.jobs)} jobs scheduled.")
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("SmartBot stopped.")
        generate_daily_report()

if __name__ == "__main__":
    main()