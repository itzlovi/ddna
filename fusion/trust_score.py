from typing import Optional
from collections import deque
import numpy as np


class TrustScoreEngine:
    """
    Exponential Moving Average trust score with robust outlier handling.

    Key changes from the original:
    - Starts at 50.0 (neutral) instead of 85.0 (pre-trusted)
    - Uses median of recent window scores for outlier robustness
    - Decays toward neutral during idle (not frozen at last value)
    """

    def __init__(self, alpha: float = 0.35, initial_score: float = 50.0):
        self.alpha = alpha
        self.current_score = initial_score
        self._initial_score = initial_score
        self._recent_scores: deque = deque(maxlen=20)

    def update(self, raw_similarity: Optional[float] = None, is_idle: bool = False) -> float:
        if is_idle or raw_similarity is None:
            # Decay toward neutral during idle — don't hold a stale high or low score
            self.current_score = 0.97 * self.current_score + 0.03 * self._initial_score
            return round(self.current_score, 2)

        instant_score = max(0.0, min(100.0, raw_similarity * 100.0))
        self._recent_scores.append(instant_score)

        # Use median of recent scores for robustness against single-window spikes
        if len(self._recent_scores) >= 3:
            robust_instant = float(np.median(list(self._recent_scores)[-5:]))
        else:
            robust_instant = instant_score

        self.current_score = (self.alpha * robust_instant) + ((1.0 - self.alpha) * self.current_score)
        return round(self.current_score, 2)

    def get_score(self) -> float:
        return round(self.current_score, 2)

    def reset(self, score: Optional[float] = None):
        self.current_score = score if score is not None else self._initial_score
        self._recent_scores.clear()
