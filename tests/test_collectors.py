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

def test_mobile_collector():
    from collectors.mobile.main_mobile_collector import MobileCollector
    mobile = MobileCollector(user_id="mobile_test")
    mobile.start()
    assert mobile._running is True

    # Ingest sensor reading
    mobile.motion.ingest_sensor_reading(ax=0.1, ay=0.2, az=9.8, gx=0.01, gy=0.02, gz=0.03)
    mobile.touch.ingest_touch_event(action="down", x=120.0, y=340.0, pressure=1.2, area=12.0)

    window = mobile.collect_window()
    assert window["user_id"] == "mobile_test"
    assert len(window["raw_events"]["motion"]) == 1
    assert len(window["raw_events"]["touch"]) == 1
    assert window["raw_events"]["motion"][0]["az"] == 9.8
    assert window["raw_events"]["touch"][0]["type"] == "down"

    mobile.stop()
    assert mobile._running is False
