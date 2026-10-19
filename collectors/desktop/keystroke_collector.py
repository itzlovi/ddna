import time
import hashlib
import threading
from typing import List, Dict, Any, Optional
from pynput import keyboard

class KeystrokeCollector:
    def __init__(self, salt: str = "ddna_salt"):
        self._salt = salt
        self._listener: Optional[keyboard.Listener] = None
        self._press_times: Dict[str, float] = {}
        self._last_release_time: Optional[float] = None
        self._lock = threading.Lock()
        self._events: List[Dict[str, Any]] = []
        self._running = False

    def _anonymize_key(self, key) -> str:
        if isinstance(key, keyboard.Key):
            name = key.name
            if name in {"backspace", "delete"}:
                return "KEY_DELETE"
            elif name in {"enter"}:
                return "KEY_ENTER"
            elif name in {"space"}:
                return "KEY_SPACE"
            elif name in {"shift", "shift_r", "ctrl", "ctrl_r", "alt", "alt_r", "cmd", "cmd_r"}:
                return "KEY_MODIFIER"
            return f"KEY_SPECIAL_{name.upper()}"
        raw_val = str(getattr(key, "vk", getattr(key, "char", "UNKNOWN")))
        hashed = hashlib.sha256((raw_val + self._salt).encode("utf-8")).hexdigest()[:8]
        return f"KEY_{hashed}"

    def _on_press(self, key):
        if not self._running:
            return
        now = time.time()
        key_id = self._anonymize_key(key)
        with self._lock:
            self._press_times[key_id] = now
            flight_time = (now - self._last_release_time) if self._last_release_time is not None else 0.0
            is_backspace = key_id == "KEY_DELETE"
            self._events.append({
                "type": "press",
                "key_id": key_id,
                "timestamp": now,
                "flight_time": max(0.0, flight_time),
                "is_error_key": is_backspace
            })

    def _on_release(self, key):
        if not self._running:
            return
        now = time.time()
        key_id = self._anonymize_key(key)
        with self._lock:
            press_time = self._press_times.pop(key_id, None)
            dwell_time = (now - press_time) if press_time is not None else 0.0
            self._last_release_time = now
            self._events.append({
                "type": "release",
                "key_id": key_id,
                "timestamp": now,
                "dwell_time": max(0.0, dwell_time),
                "is_error_key": key_id == "KEY_DELETE"
            })

    def start(self):
        if self._running:
            return
        self._running = True
        self._listener = keyboard.Listener(on_press=self._on_press, on_release=self._on_release)
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
