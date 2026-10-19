from typing import Union, List
import numpy as np
import pandas as pd
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from .model_utils import save_model, load_model, decision_function_to_score

class MotionModel:
    def __init__(self, nu: float = 0.05, kernel: str = "rbf", gamma: str = "scale"):
        self.nu = nu
        self.kernel = kernel
        self.gamma = gamma
        self.pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("svm", OneClassSVM(nu=self.nu, kernel=self.kernel, gamma=self.gamma))
        ])
        self.is_fitted = False

    def fit(self, X: Union[np.ndarray, pd.DataFrame, List[List[float]]]) -> "MotionModel":
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
        decision = self.pipeline.decision_function(arr)
        sim = decision_function_to_score(decision)
        return float(np.mean(sim))

    def save(self, filepath: str):
        save_model(self, filepath)

    @classmethod
    def load(cls, filepath: str) -> "MotionModel":
        return load_model(filepath)
