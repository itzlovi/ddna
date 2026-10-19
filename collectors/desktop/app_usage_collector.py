import time
import os
import sys
import threading
from typing import List, Dict, Any, Optional
import psutil

class AppUsageCollector:
    def __init__(self, check_interval_seconds: float = 1.0):
        self._interval = check_interval_seconds
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._events: List[Dict[str, Any]] = []
        self._last_process_name: Optional[str] = None
        self._switch_count = 0

    def _get_active_process_name(self) -> str:
        if sys.platform == "win32":
            try:
                import ctypes
                hwnd = ctypes.windll.user32.GetForegroundWindow()
                if hwnd == 0:
                    return "idle"
                pid = ctypes.c_ulong()
                ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                p = psutil.Process(pid.value)
                return p.name()
            except Exception:
                return "unknown"
        return "desktop"

    def _loop(self):
        while self._running:
            pname = self._get_active_process_name()
            now = time.time()
            with self._lock:
                if pname != self._last_process_name:
                    self._switch_count += 1
                    self._events.append({
                        "type": "app_switch",
                        "app_name": pname,
                        "timestamp": now,
                        "switch_count": self._switch_count
                    })
                    self._last_process_name = pname
            time.sleep(self._interval)

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=2.0)
            self._thread = None

    def flush_events(self) -> List[Dict[str, Any]]:
        with self._lock:
            evs = self._events
            self._events = []
            return evs
