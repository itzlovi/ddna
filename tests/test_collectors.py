import time
import pytest
from collectors.desktop.keystroke_collector import KeystrokeCollector
from collectors.desktop.mouse_collector import MouseCollector
from collectors.desktop.app_usage_collector import AppUsageCollector
from collectors.desktop.main_collector import DesktopCollector

def test_keystroke_collector_init():
    collector = KeystrokeCollector()
    assert collector.get_event_count() == 0
    collector.start()
    assert collector._running is True
    collector.stop()
    assert collector._running is False

def test_mouse_collector_init():
    collector = MouseCollector()
    assert collector.get_event_count() == 0
    collector.start()
    assert collector._running is True
    collector.stop()
    assert collector._running is False

def test_app_usage_collector_init():
    collector = AppUsageCollector()
    collector.start()
    assert collector._running is True
    time.sleep(0.1)
    collector.stop()
    assert collector._running is False

def test_desktop_collector_collect_window():
    collector = DesktopCollector(user_id="test_user")
    collector.start()
    window = collector.collect_window()
    assert window["user_id"] == "test_user"
    assert "raw_events" in window
    assert "keystroke" in window["raw_events"]
    assert "mouse" in window["raw_events"]
    collector.stop()
