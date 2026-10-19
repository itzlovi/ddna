from typing import Union, List
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import RobustScaler
from sklearn.pipeline import Pipeline
from .model_utils import save_model, load_model, isolation_score_to_similarity

class MouseModel:
    def __init__(self, contamination: float = 0.05, n_estimators: int = 150, random_state: int = 42):
        self.contamination = contamination
        self.n_estimators = n_estimators
        self.random_state = random_state
        self.pipeline = Pipeline([
            ("scaler", RobustScaler()),
            ("forest", IsolationForest(
                contamination=self.contamination,
                n_estimators=self.n_estimators,
                random_state=self.random_state
            ))
        ])
        self.is_fitted = False

    def fit(self, X: Union[np.ndarray, pd.DataFrame, List[List[float]]]) -> "MouseModel":
        arr = np.asarray(X, dtype=np.float64)
        if arr.ndim == 1:
            arr = arr.reshape(1, -1)
        self.pipeline.fit(arr)
        self.is_fitted = True
        return self

    def score(self, X: Union[np.ndarray, pd.DataFrame, List[float], List[List[float]]]) -> float:
        if not self.is_fitted:
            return 0.5
        arr = np.asarray(X, dtype=np.float64)
        if arr.ndim == 1:
            arr = arr.reshape(1, -1)
        raw_scores = self.pipeline.score_samples(arr)
        sim = isolation_score_to_similarity(raw_scores)
        return float(np.mean(sim))

    def predict(self, X: Union[np.ndarray, pd.DataFrame, List[List[float]]]) -> np.ndarray:
        if not self.is_fitted:
            return np.array([1])
        arr = np.asarray(X, dtype=np.float64)
        if arr.ndim == 1:
            arr = arr.reshape(1, -1)
        return self.pipeline.predict(arr)

    def save(self, filepath: str):
        save_model(self, filepath)

    @classmethod
    def load(cls, filepath: str) -> "MouseModel":
        return load_model(filepath)
