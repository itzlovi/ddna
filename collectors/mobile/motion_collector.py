import time
import threading
from typing import List, Dict, Any

class MotionCollector:
    def __init__(self):
        self._lock = threading.Lock()
        self._events: List[Dict[str, Any]] = []
        self._running = False

    def ingest_sensor_reading(self, ax: float, ay: float, az: float, gx: float = 0.0, gy: float = 0.0, gz: float = 0.0, timestamp: float = None):
        t = timestamp if timestamp is not None else time.time()
        with self._lock:
            self._events.append({
                "type": "motion",
                "timestamp": t,
                "ax": ax,
                "ay": ay,
                "az": az,
                "gx": gx,
                "gy": gy,
                "gz": gz
            })

    def start(self):
        self._running = True

    def stop(self):
        self._running = False

    def flush_events(self) -> List[Dict[str, Any]]:
        with self._lock:
            evs = self._events
            self._events = []
            return evs
