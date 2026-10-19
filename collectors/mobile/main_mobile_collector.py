import time
import uuid
from typing import Dict, Any, Optional
from .motion_collector import MotionCollector
from .touch_collector import TouchCollector

class MobileCollector:
    def __init__(self, user_id: str = "mobile_user", session_id: Optional[str] = None):
        self.user_id = user_id
        self.session_id = session_id or str(uuid.uuid4())
        self.motion = MotionCollector()
        self.touch = TouchCollector()
        self._running = False

    def start(self):
        self._running = True
        self.motion.start()
        self.touch.start()

    def stop(self):
        self._running = False
        self.motion.stop()
        self.touch.stop()

    def collect_window(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "session_id": self.session_id,
            "timestamp": time.time(),
            "raw_events": {
                "motion": self.motion.flush_events(),
                "touch": self.touch.flush_events()
            }
        }
