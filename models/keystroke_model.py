from typing import Union, List

import numpy as np
import pandas as pd
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

from .model_utils import save_model, load_model, calibrated_score


class KeystrokeModel:
    def __init__(self, nu: float = 0.05, kernel: str = "rbf", gamma: str = "scale"):
        self.nu = nu
        self.kernel = kernel
        self.gamma = gamma
        self.pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("svm", OneClassSVM(nu=self.nu, kernel=self.kernel, gamma=self.gamma)),
        ])
        self.is_fitted = False
        self.train_mean: float = 0.0
        self.train_std: float = 1.0

    def fit(self, X: Union[np.ndarray, pd.DataFrame, List[List[float]]]) -> "KeystrokeModel":
        arr = np.asarray(X, dtype=np.float64)
        if arr.ndim == 1:
            arr = arr.reshape(1, -1)
        self.pipeline.fit(arr)

        train_scores = self.pipeline.decision_function(arr)
        self.train_mean = float(np.mean(train_scores))
        self.train_std = max(float(np.std(train_scores)), 1e-4) if len(train_scores) > 1 else 1.0

        self.is_fitted = True
        return self

    def score(self, X: Union[np.ndarray, pd.DataFrame, List[float], List[List[float]]]) -> float:
        if not self.is_fitted:
            return 0.5
        arr = np.asarray(X, dtype=np.float64)
        if arr.ndim == 1:
            arr = arr.reshape(1, -1)
        raw = self.pipeline.decision_function(arr)
        sim = calibrated_score(raw, self.train_mean, self.train_std)
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
    def load(cls, filepath: str) -> "KeystrokeModel":
        return load_model(filepath)
