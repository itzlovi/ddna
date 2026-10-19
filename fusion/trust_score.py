from typing import Optional

class TrustScoreEngine:
    def __init__(self, alpha: float = 0.35, initial_score: float = 85.0):
        self.alpha = alpha
        self.current_score = initial_score

    def update(self, raw_similarity: float) -> float:
        instant_score = max(0.0, min(100.0, raw_similarity * 100.0))
        self.current_score = (self.alpha * instant_score) + ((1.0 - self.alpha) * self.current_score)
        return round(self.current_score, 2)

    def get_score(self) -> float:
        return round(self.current_score, 2)

    def reset(self, score: float = 85.0):
        self.current_score = score
