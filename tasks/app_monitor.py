
import json, os
from utils.monitor import AppMonitor
from utils import get_logger, log_action, warning

logger = get_logger(__name__)
_CFG = os.path.join(os.path.dirname(__file__), "..", "config", "config.json")
_monitor_instance = None

def _on_alert(app, minutes):
    warning("SmartBot — App Alert", f"{app} used for {minutes:.0f} min!")
    log_action("app_monitor", "THRESHOLD_ALERT", f"{app}:{minutes:.0f}min", level="WARNING")

def run():
    global _monitor_instance
    cfg = json.load(open(_CFG))["app_monitor"]
    if _monitor_instance is None:
        _monitor_instance = AppMonitor(
            tracked_apps=cfg["tracked_apps"],
            threshold_minutes=cfg["alert_threshold_minutes"],
            poll_interval_seconds=60,
            alert_callback=_on_alert
        )
        _monitor_instance.start()
    return _monitor_instance.get_usage_summary()

def stop():
    global _monitor_instance
    if _monitor_instance:
        _monitor_instance.stop()
        _monitor_instance = None