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