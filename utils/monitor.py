"""
monitor.py — Folder and application monitoring.
"""
import os, time, threading, psutil
from utils.logger import get_logger, log_action

logger = get_logger(__name__)

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    logger.warning("watchdog not installed — folder monitoring disabled.")


class SmartBotEventHandler(FileSystemEventHandler if WATCHDOG_AVAILABLE else object):
    def __init__(self, callbacks=None):
        self.callbacks = callbacks or {}
        if WATCHDOG_AVAILABLE:
            super().__init__()

    def _dispatch(self, event_type, src_path, dest_path=None):
        detail = src_path + (f" → {dest_path}" if dest_path else "")
        log_action("monitor", event_type.upper(), detail)
        if event_type in self.callbacks:
            try:
                self.callbacks[event_type](src_path, dest_path)
            except Exception as e:
                logger.error(f"Callback error: {e}")

    def on_created(self, event):
        if not event.is_directory: self._dispatch("created", event.src_path)
    def on_modified(self, event):
        if not event.is_directory: self._dispatch("modified", event.src_path)
    def on_deleted(self, event):
        if not event.is_directory: self._dispatch("deleted", event.src_path)
    def on_moved(self, event):
        if not event.is_directory: self._dispatch("moved", event.src_path, event.dest_path)


class FolderMonitor:
    def __init__(self, watch_path, callbacks=None, recursive=False):
        self.watch_path = os.path.expanduser(watch_path)
        self.callbacks = callbacks or {}
        self.recursive = recursive
        self._observer = None

    def start(self):
        if not WATCHDOG_AVAILABLE:
            logger.error("watchdog not installed.")
            return
        if not os.path.isdir(self.watch_path):
            logger.error(f"Watch path not found: {self.watch_path}")
            return
        handler = SmartBotEventHandler(self.callbacks)
        self._observer = Observer()
        self._observer.schedule(handler, self.watch_path, recursive=self.recursive)
        self._observer.start()
        logger.info(f"FolderMonitor started: {self.watch_path}")

    def stop(self):
        if self._observer and self._observer.is_alive():
            self._observer.stop()
            self._observer.join()

    def is_running(self):
        return self._observer is not None and self._observer.is_alive()


class AppMonitor:
    def __init__(self, tracked_apps, threshold_minutes=120, poll_interval_seconds=60, alert_callback=None):
        self.tracked_apps = [a.lower() for a in tracked_apps]
        self.threshold_minutes = threshold_minutes
        self.poll_interval = poll_interval_seconds
        self.alert_callback = alert_callback
        self._usage = {}
        self._alerted = set()
        self._running = False
        self._thread = None

    def _get_running_apps(self):
        running = set()
        for proc in psutil.process_iter(["name"]):
            try:
                running.add(proc.info["name"].lower().replace(".exe", ""))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return running

    def _poll(self):
        while self._running:
            running = self._get_running_apps()
            for app in self.tracked_apps:
                if app in running:
                    self._usage[app] = self._usage.get(app, 0) + (self.poll_interval / 60)
                    usage = self._usage[app]
                    if usage >= self.threshold_minutes and app not in self._alerted:
                        self._alerted.add(app)
                        if self.alert_callback:
                            self.alert_callback(app, usage)
            time.sleep(self.poll_interval)

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._poll, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)

    def reset_daily(self):
        self._usage.clear()
        self._alerted.clear()

    def get_usage_summary(self):
        return dict(self._usage)