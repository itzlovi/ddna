import pytest
from features.keystroke_features import extract_keystroke_features, KEYSTROKE_FEATURE_NAMES
from features.mouse_features import extract_mouse_features, MOUSE_FEATURE_NAMES
from features.motion_features import extract_motion_features, MOTION_FEATURE_NAMES
from features.touch_features import extract_touch_features, TOUCH_FEATURE_NAMES
from features.feature_pipeline import FeaturePipeline

def test_keystroke_features_empty():
    feats = extract_keystroke_features([])
    for name in KEYSTROKE_FEATURE_NAMES:
        assert name in feats
        assert feats[name] == 0.0

def test_keystroke_features_synthetic():
    events = [
        {"type": "press", "key_id": "KEY_1", "timestamp": 1000.0, "flight_time": 0.0, "is_error_key": False},
        {"type": "release", "key_id": "KEY_1", "timestamp": 1000.1, "dwell_time": 0.1, "is_error_key": False},
        {"type": "press", "key_id": "KEY_2", "timestamp": 1000.25, "flight_time": 0.15, "is_error_key": False},
        {"type": "release", "key_id": "KEY_2", "timestamp": 1000.35, "dwell_time": 0.1, "is_error_key": False},
        {"type": "press", "key_id": "KEY_DELETE", "timestamp": 1000.5, "flight_time": 0.15, "is_error_key": True},
        {"type": "release", "key_id": "KEY_DELETE", "timestamp": 1000.6, "dwell_time": 0.1, "is_error_key": True},
    ]
    feats = extract_keystroke_features(events)
    assert feats["mean_dwell_time"] > 0.0
    assert feats["error_rate"] > 0.0

def test_mouse_features_empty():
    feats = extract_mouse_features([])
    for name in MOUSE_FEATURE_NAMES:
        assert name in feats
        assert feats[name] == 0.0

def test_mouse_features_synthetic():
    events = [
        {"type": "move", "x": 10, "y": 10, "timestamp": 100.0, "distance": 0.0, "dt": 0.01, "speed": 0.0, "acceleration": 0.0},
        {"type": "move", "x": 30, "y": 40, "timestamp": 100.05, "distance": 36.0, "dt": 0.05, "speed": 720.0, "acceleration": 100.0},
        {"type": "move", "x": 60, "y": 80, "timestamp": 100.10, "distance": 50.0, "dt": 0.05, "speed": 1000.0, "acceleration": 200.0},
        {"type": "click_press", "x": 60, "y": 80, "button": "left", "timestamp": 100.15},
        {"type": "click_release", "x": 60, "y": 80, "button": "left", "timestamp": 100.25, "duration": 0.10},
    ]
    feats = extract_mouse_features(events)
    assert feats["mean_speed"] > 0.0
    assert feats["mean_click_duration"] > 0.0

def test_feature_pipeline():
    raw_data = {
        "raw_events": {
            "keystroke": [],
            "mouse": []
        }
    }
    extracted = FeaturePipeline.extract_all(raw_data)
    assert "keystroke" in extracted
    assert "mouse" in extracted
    assert "motion" in extracted
    assert "touch" in extracted
