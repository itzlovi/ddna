from typing import Union, List, Optional

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.covariance import LedoitWolf, EmpiricalCovariance

from .model_utils import save_model, load_model, inverted_calibrated_score


class MahalanobisModel:
    """Mahalanobis Distance anomaly detector with Ledoit-Wolf covariance shrinkage."""

    def __init__(self, reg_covar: float = 1e-4):
        self.reg_covar = reg_covar
        self.scaler = StandardScaler()
        self.mean_vector: Optional[np.ndarray] = None
        self.inv_cov: Optional[np.ndarray] = None
        self.is_fitted = False
        self.train_mean: float = 0.0
        self.train_std: float = 1.0

    def fit(self, X: Union[np.ndarray, pd.DataFrame, List[List[float]]]) -> "MahalanobisModel":
        arr = np.asarray(X, dtype=np.float64)
        if arr.ndim == 1:
            arr = arr.reshape(1, -1)

        X_scaled = self.scaler.fit_transform(arr)
        self.mean_vector = np.mean(X_scaled, axis=0)

        try:
            cov_estimator = LedoitWolf().fit(X_scaled)
            cov_matrix = cov_estimator.covariance_
        except Exception:
            cov_estimator = EmpiricalCovariance().fit(X_scaled)
            cov_matrix = cov_estimator.covariance_

        d = cov_matrix.shape[0]
        cov_matrix += np.eye(d) * self.reg_covar
        self.inv_cov = np.linalg.pinv(cov_matrix)

        diff = X_scaled - self.mean_vector
        train_dists = np.sqrt(np.sum((diff @ self.inv_cov) * diff, axis=1))
        self.train_mean = float(np.mean(train_dists))
        self.train_std = max(float(np.std(train_dists)), 1e-4)

        self.is_fitted = True
        return self

    def _compute_distance(self, X_scaled: np.ndarray) -> np.ndarray:
        diff = X_scaled - self.mean_vector
        dist_sq = np.sum((diff @ self.inv_cov) * diff, axis=1)
        return np.sqrt(np.maximum(dist_sq, 0.0))

    def score(self, X: Union[np.ndarray, pd.DataFrame, List[float], List[List[float]]]) -> float:
        """0-1 similarity. Lower Mahalanobis distance → higher score."""
        if not self.is_fitted or self.mean_vector is None or self.inv_cov is None:
            return 0.5
        arr = np.asarray(X, dtype=np.float64)
        if arr.ndim == 1:
            arr = arr.reshape(1, -1)
        X_scaled = self.scaler.transform(arr)
        dists = self._compute_distance(X_scaled)
        sim = inverted_calibrated_score(dists, self.train_mean, self.train_std)
        return float(np.mean(sim))

    def predict(self, X: Union[np.ndarray, pd.DataFrame, List[List[float]]]) -> np.ndarray:
        if not self.is_fitted:
            return np.array([1])
        arr = np.asarray(X, dtype=np.float64)
        if arr.ndim == 1:
            arr = arr.reshape(1, -1)
        X_scaled = self.scaler.transform(arr)
        dists = self._compute_distance(X_scaled)
        thresh = self.train_mean + 2.0 * self.train_std
        return np.where(dists <= thresh, 1, -1)

    def save(self, filepath: str):
        save_model(self, filepath)

    @classmethod
    def load(cls, filepath: str) -> "MahalanobisModel":
        return load_model(filepath)
