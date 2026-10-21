"""
Window Buffer — maintains a sliding window of recent raw events for multi-scale feature extraction.

Instead of scoring only 30-second windows, this buffer enables extracting features at
three time scales:
- 30s (micro-patterns: individual dwell/flight times)
- 2min (meso-patterns: sustained rhythm, trajectory style)
- 5min (macro-patterns: overall work rhythm, app switching cadence)

The concatenated multi-scale feature vector (35 × 3 = 105 features) provides much
richer input to the models.
"""

from collections import deque
from typing import Dict, Any, List, Optional


class WindowBuffer:
    """Sliding buffer that accumulates recent windows and can merge them for multi-scale features."""

    def __init__(self, step_seconds: float = 5.0, max_duration_seconds: float = 300.0):
        """
        Parameters
        ----------
        step_seconds : seconds between windows (the collector flush interval)
        max_duration_seconds : maximum history to retain (default 5 minutes)
        """
        self.step_seconds = step_seconds
        max_windows = int(max_duration_seconds / step_seconds)
        self._windows: deque = deque(maxlen=max_windows)

    def add(self, raw_events: Dict[str, Any]):
        """Add a single window's raw events to the buffer."""
        self._windows.append(raw_events)

    def get_merged(self, last_n: int) -> Dict[str, List[Dict[str, Any]]]:
        """
        Merge the last N windows' raw events into one combined event dict.

        Parameters
        ----------
        last_n : number of recent windows to merge

        Returns
        -------
        Dict with 'keystroke' and 'mouse' keys containing merged event lists
        """
        merged: Dict[str, List] = {"keystroke": [], "mouse": [], "app_usage": []}
        windows_to_merge = list(self._windows)[-last_n:]
        for w in windows_to_merge:
            events = w.get("raw_events", w)  # Handle both formats
            for key in merged:
                merged[key].extend(events.get(key, []))
        return merged

    def get_multiscale_events(self) -> Dict[str, Dict[str, List]]:
        """
        Return raw events merged at three time scales.

        Returns
        -------
        Dict with keys 'short' (30s), 'medium' (2min), 'long' (5min),
        each containing merged keystroke and mouse event lists.
        """
        short_n = max(1, int(30 / self.step_seconds))     # ~6 windows for 30s
        medium_n = max(1, int(120 / self.step_seconds))    # ~24 windows for 2min
        long_n = max(1, int(300 / self.step_seconds))      # ~60 windows for 5min

        return {
            "short": self.get_merged(short_n),
            "medium": self.get_merged(min(medium_n, len(self._windows))),
            "long": self.get_merged(min(long_n, len(self._windows))),
        }

    @property
    def window_count(self) -> int:
        return len(self._windows)

    def clear(self):
        self._windows.clear()
