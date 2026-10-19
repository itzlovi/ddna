import time
import threading
from typing import List, Dict, Any

class TouchCollector:
    def __init__(self):
        self._lock = threading.Lock()
        self._events: List[Dict[str, Any]] = []
        self._running = False

    def ingest_touch_event(self, action: str, x: float, y: float, pressure: float = 1.0, area: float = 1.0, timestamp: float = None):
        t = timestamp if timestamp is not None else time.time()
        with self._lock:
            self._events.append({
                "type": action,
                "x": x,
                "y": y,
                "pressure": pressure,
                "area": area,
                "timestamp": t
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
