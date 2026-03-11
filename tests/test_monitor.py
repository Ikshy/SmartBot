import os, sys, time, tempfile, shutil, pytest
from unittest.mock import MagicMock, patch
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.monitor import AppMonitor

def test_start_stop():
    m = AppMonitor(["no_app"], threshold_minutes=999)
    m.start(); assert m._running; time.sleep(0.1); m.stop(); assert not m._running

def test_empty_usage():
    assert AppMonitor(["x"]).get_usage_summary() == {}

def test_reset():
    m = AppMonitor(["chrome"]); m._usage = {"chrome": 90}; m._alerted = {"chrome"}
    m.reset_daily(); assert m._usage == {} and m._alerted == set()

def test_running_apps_is_set():
    assert isinstance(AppMonitor([])._get_running_apps(), set)

def test_folder_monitor_bad_path():
    from utils.monitor import FolderMonitor, WATCHDOG_AVAILABLE
    if not WATCHDOG_AVAILABLE: pytest.skip("watchdog missing")
    m = FolderMonitor("/no/path"); m.start(); assert not m.is_running()

def test_folder_monitor_valid_path():
    from utils.monitor import FolderMonitor, WATCHDOG_AVAILABLE
    if not WATCHDOG_AVAILABLE: pytest.skip("watchdog missing")
    tmp = tempfile.mkdtemp()
    try:
        m = FolderMonitor(tmp); m.start(); assert m.is_running(); m.stop()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)