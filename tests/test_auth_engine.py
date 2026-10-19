import tempfile
import shutil
from pathlib import Path
import pytest
from core.profile_manager import ProfileManager
from core.enrollment import EnrollmentManager
from core.auth_engine import ContinuousAuthEngine

@pytest.fixture
def temp_profile_dir():
    d = tempfile.mkdtemp()
    yield Path(d)
    shutil.rmtree(d, ignore_errors=True)

def test_profile_manager(temp_profile_dir):
    mgr = ProfileManager(profiles_dir=temp_profile_dir)
    assert not mgr.exists("test_user")
    mgr.create_or_update_metadata("test_user", {"status": "enrolled"})
    assert mgr.exists("test_user")
    meta = mgr.get_metadata("test_user")
    assert meta.get("status") == "enrolled"
    assert "test_user" in mgr.list_profiles()

def test_continuous_auth_engine(temp_profile_dir):
    mgr = ProfileManager(profiles_dir=temp_profile_dir)
    engine = ContinuousAuthEngine(user_id="test_user", profile_manager=mgr)
    synthetic_window = {
        "user_id": "test_user",
        "raw_events": {
            "keystroke": [
                {"type": "press", "key_id": "KEY_1", "timestamp": 10.0, "flight_time": 0.0},
                {"type": "release", "key_id": "KEY_1", "timestamp": 10.1, "dwell_time": 0.1}
            ],
            "mouse": [
                {"type": "move", "x": 10, "y": 10, "timestamp": 10.0, "speed": 100.0, "acceleration": 10.0}
            ]
        }
    }
    res = engine.process_window(synthetic_window)
    assert "trust_score" in res
    assert "decision" in res
    assert res["decision"] in {"ALLOW", "WARN", "LOCK"}
