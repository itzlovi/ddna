from pathlib import Path
from typing import Any
import joblib
import numpy as np

def save_model(model: Any, filepath: str):
    p = Path(filepath)
    p.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, p)

def load_model(filepath: str) -> Any:
    return joblib.load(filepath)

def decision_function_to_score(raw_scores: np.ndarray, shift: float = 0.0, scale: float = 1.0) -> np.ndarray:
    scaled = (raw_scores - shift) * scale
    return 1.0 / (1.0 + np.exp(-np.clip(scaled, -15.0, 15.0)))

def isolation_score_to_similarity(score_samples: np.ndarray) -> np.ndarray:
    return np.clip((score_samples + 0.5) / 1.0, 0.0, 1.0)
