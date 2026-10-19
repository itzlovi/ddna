import time
import math
import threading
from typing import List, Dict, Any, Optional
from pynput import mouse

class MouseCollector:
    def __init__(self, min_sample_interval_ms: float = 10.0):
        self._min_interval = min_sample_interval_ms / 1000.0
        self._listener: Optional[mouse.Listener] = None
        self._last_move_time = 0.0
        self._last_x = 0
        self._last_y = 0
        self._last_vx = 0.0
        self._last_vy = 0.0
        self._click_press_times: Dict[str, float] = {}
        self._lock = threading.Lock()
        self._events: List[Dict[str, Any]] = []
        self._running = False

    def _on_move(self, x, y):
        if not self._running:
            return
        now = time.time()
        dt = now - self._last_move_time
        if dt < self._min_interval:
            return
        dx = x - self._last_x
        dy = y - self._last_y
        dist = math.hypot(dx, dy)
        speed = dist / dt if dt > 0 else 0.0
        vx = dx / dt if dt > 0 else 0.0
        vy = dy / dt if dt > 0 else 0.0
        ax = (vx - self._last_vx) / dt if dt > 0 else 0.0
        ay = (vy - self._last_vy) / dt if dt > 0 else 0.0
        acceleration = math.hypot(ax, ay)
        with self._lock:
            self._events.append({
                "type": "move",
                "x": x,
                "y": y,
                "timestamp": now,
                "dx": dx,
                "dy": dy,
                "distance": dist,
                "dt": dt,
                "speed": speed,
                "acceleration": acceleration
            })
            self._last_move_time = now
            self._last_x = x
            self._last_y = y
            self._last_vx = vx
            self._last_vy = vy

    def _on_click(self, x, y, button, pressed):
        if not self._running:
            return
        now = time.time()
        btn_name = button.name if hasattr(button, "name") else str(button)
        with self._lock:
            if pressed:
                self._click_press_times[btn_name] = now
                self._events.append({
                    "type": "click_press",
                    "x": x,
                    "y": y,
                    "button": btn_name,
                    "timestamp": now
                })
            else:
                press_t = self._click_press_times.pop(btn_name, None)
                duration = (now - press_t) if press_t is not None else 0.0
                self._events.append({
                    "type": "click_release",
                    "x": x,
                    "y": y,
                    "button": btn_name,
                    "timestamp": now,
                    "duration": max(0.0, duration)
                })

    def _on_scroll(self, x, y, dx, dy):
        if not self._running:
            return
        now = time.time()
        with self._lock:
            self._events.append({
                "type": "scroll",
                "x": x,
                "y": y,
                "dx": dx,
                "dy": dy,
                "timestamp": now
            })

    def start(self):
        if self._running:
            return
        self._running = True
        self._last_move_time = time.time()
        self._listener = mouse.Listener(
            on_move=self._on_move,
            on_click=self._on_click,
            on_scroll=self._on_scroll
        )
        self._listener.daemon = True
        self._listener.start()

    def stop(self):
        self._running = False
        if self._listener is not None:
            self._listener.stop()
            self._listener = None

    def flush_events(self) -> List[Dict[str, Any]]:
        with self._lock:
            evs = self._events
            self._events = []
            return evs

    def get_event_count(self) -> int:
        with self._lock:
            return len(self._events)
