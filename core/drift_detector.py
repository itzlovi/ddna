from collections import deque
from typing import Dict, Any, Optional
import numpy as np


class ConceptDriftDetector:
    """
    Monitors long-term behavioral score trajectories to distinguish between:
    1. Natural behavioral drift (gradual shift due to fatigue, posture, new keyboard)
    2. Impostor attacks (instant drop to zero similarity)
    3. Stable user performance
    """

    def __init__(self, window_size: int = 60, drift_threshold: float = 0.12):
        self.window_size = window_size
        self.drift_threshold = drift_threshold
        self._scores: deque = deque(maxlen=window_size)
        self.total_processed: int = 0

    def add_score(self, score: float) -> Dict[str, Any]:
        """
        Record a similarity score (0.0 to 1.0) and evaluate drift status.
        """
        self._scores.append(float(score))
        self.total_processed += 1

        if len(self._scores) < 20:
            return {
                "status": "INITIALIZING",
                "drift_detected": False,
                "recent_mean": float(np.mean(self._scores)),
                "baseline_mean": float(np.mean(self._scores)),
                "drift_magnitude": 0.0
            }

        scores_list = list(self._scores)
        half = len(scores_list) // 2
        baseline_half = scores_list[:half]
        recent_half = scores_list[half:]

        baseline_mean = float(np.mean(baseline_half))
        recent_mean = float(np.mean(recent_half))
        drift_magnitude = baseline_mean - recent_mean

        # If recent scores dropped gradually but are still in genuine range (e.g. > 0.55),
        # that's natural concept drift -> triggers profile fine-tuning
        if drift_magnitude >= self.drift_threshold and recent_mean >= 0.50:
            status = "GRADUAL_DRIFT"
            drift_detected = True
        elif recent_mean < 0.30:
            status = "ANOMALY_IMPOSTOR"
            drift_detected = False
        else:
            status = "STABLE"
            drift_detected = False

        return {
            "status": status,
            "drift_detected": drift_detected,
            "recent_mean": round(recent_mean, 3),
            "baseline_mean": round(baseline_mean, 3),
            "drift_magnitude": round(drift_magnitude, 3)
        }

    def reset(self):
        self._scores.clear()
        self.total_processed = 0
