from typing import Dict, Optional

class ScoreFusion:
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.default_weights = weights or {
            "keystroke": 0.45,
            "mouse": 0.45,
            "motion": 0.05,
            "touch": 0.05
        }

    def fuse(self, modality_scores: Dict[str, Optional[float]]) -> float:
        valid_scores = {k: v for k, v in modality_scores.items() if v is not None and k in self.default_weights}
        if not valid_scores:
            return 0.5
        total_weight = sum(self.default_weights[k] for k in valid_scores.keys())
        if total_weight <= 0:
            return 0.5
        fused = sum(self.default_weights[k] * valid_scores[k] for k in valid_scores.keys()) / total_weight
        return max(0.0, min(1.0, fused))
