import sys
import shutil
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.profile_manager import ProfileManager
from core.enrollment import EnrollmentManager
from core.raw_event_store import RawEventStore
from core.window_buffer import WindowBuffer
from core.config import config

def test_phase2():
    pm = ProfileManager()
    test_user = "test_phase2_user"
    em = EnrollmentManager(test_user, pm)

    # 1. Simulate recording windows with raw events
    print("1. Simulating recording 5 windows with raw events...")
    for i in range(5):
        raw_window = {
            "timestamp": time.time(),
            "raw_events": {
                "keystroke": [
                    {"type": "press", "timestamp": time.time(), "key_id": "KEY_a", "flight_time": 0.12},
                    {"type": "release", "timestamp": time.time() + 0.08, "key_id": "KEY_a", "dwell_time": 0.08},
                    {"type": "press", "timestamp": time.time() + 0.20, "key_id": "KEY_b", "flight_time": 0.12},
                    {"type": "release", "timestamp": time.time() + 0.28, "key_id": "KEY_b", "dwell_time": 0.08},
                ],
                "mouse": [
                    {"type": "move", "x": 100 + i * 10, "y": 200 + i * 5, "speed": 150.0, "acceleration": 20.0, "distance": 15.0},
                    {"type": "move", "x": 115 + i * 10, "y": 205 + i * 5, "speed": 160.0, "acceleration": 10.0, "distance": 15.0},
                    {"type": "click_press", "x": 120, "y": 210, "timestamp": time.time()},
                    {"type": "click_release", "x": 120, "y": 210, "duration": 0.09, "timestamp": time.time() + 0.09},
                ]
            }
        }
        em.add_window(raw_window)

    # Verify raw events were stored to disk
    session_files = em.raw_store.list_sessions()
    print(f"  Sessions found: {session_files}")
    assert len(session_files) > 0, "No raw session file created!"

    raw_records = em.raw_store.load_session(session_files[0])
    print(f"  Raw window records in session JSONL: {len(raw_records)}")
    assert len(raw_records) == 5, f"Expected 5 raw records, got {len(raw_records)}"

    # Verify window buffer holds multi-scale events
    ms = em.window_buffer.get_multiscale_events()
    print(f"  Multi-scale short keystrokes: {len(ms['short']['keystroke'])}, medium: {len(ms['medium']['keystroke'])}")
    assert len(ms['short']['keystroke']) > 0, "Multi-scale buffer empty!"

    # 2. Test Deletion / Clear All
    print("2. Testing Clear / Delete...")
    deleted = pm.delete_profile(test_user)
    print(f"  Profile directory deleted: {deleted}")
    assert not pm.get_profile_path(test_user).exists(), "Profile path still exists after deletion!"

    em.reset_session(test_user)
    assert len(em.keystroke_samples) == 0, "Keystroke samples not cleared!"
    assert len(em.mouse_samples) == 0, "Mouse samples not cleared!"
    assert em.window_buffer.window_count == 0, "Window buffer not cleared!"
    print("  In-memory buffers cleared successfully!")

    print("\nALL PHASE 2 CORE CRITERIA PASSED!")

if __name__ == "__main__":
    test_phase2()
