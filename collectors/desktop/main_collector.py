import time
import uuid
import json
from pathlib import Path
from typing import Dict, Any, Optional
from .keystroke_collector import KeystrokeCollector
from .mouse_collector import MouseCollector
from .app_usage_collector import AppUsageCollector

class DesktopCollector:
    def __init__(self, user_id: str = "default_user", session_id: Optional[str] = None):
        self.user_id = user_id
        self.session_id = session_id or str(uuid.uuid4())
        self.keystroke = KeystrokeCollector()
        self.mouse = MouseCollector()
        self.app_usage = AppUsageCollector()
        self._running = False

    def start(self):
        if self._running:
            return
        self._running = True
        self.keystroke.start()
        self.mouse.start()
        self.app_usage.start()

    def stop(self):
        self._running = False
        self.keystroke.stop()
        self.mouse.stop()
        self.app_usage.stop()

    def collect_window(self) -> Dict[str, Any]:
        k_events = self.keystroke.flush_events()
        m_events = self.mouse.flush_events()
        a_events = self.app_usage.flush_events()
        now = time.time()
        return {
            "user_id": self.user_id,
            "session_id": self.session_id,
            "timestamp": now,
            "raw_events": {
                "keystroke": k_events,
                "mouse": m_events,
                "app_usage": a_events
            }
        }

    def save_session_data(self, output_path: str, data: Dict[str, Any]):
        p = Path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "a", encoding="utf-8") as f:
            f.write(json.dumps(data) + "\n")

if __name__ == "__main__":
    collector = DesktopCollector()
    collector.start()
    try:
        while True:
            time.sleep(5)
            data = collector.collect_window()
            print(f"Captured: {len(data['raw_events']['keystroke'])} keystrokes, {len(data['raw_events']['mouse'])} mouse events")
    except KeyboardInterrupt:
        collector.stop()
