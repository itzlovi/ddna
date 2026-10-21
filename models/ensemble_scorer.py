from typing import Dict, List, Optional, Union

import numpy as np
import pandas as pd

from .keystroke_model import KeystrokeModel
from .mouse_model import MouseModel
from .mahalanobis_model import MahalanobisModel
from .autoencoder_model import AutoencoderModel
from .model_utils import save_model, load_model


class BiometricEnsemble:
    """Tri-model weighted voting ensemble for behavioral biometrics."""

    DEFAULT_WEIGHTS = {"primary": 0.40, "mahalanobis": 0.30, "autoencoder": 0.30}

    def __init__(self, modality: str = "keystroke", weights: Optional[Dict[str, float]] = None):
        self.modality = modality
        self.weights = weights or dict(self.DEFAULT_WEIGHTS)
        self.primary_model = KeystrokeModel() if modality == "keystroke" else MouseModel()
        self.mahal_model = MahalanobisModel()
        self.ae_model = AutoencoderModel()
        self.is_fitted = False

    def fit(self, X: Union[np.ndarray, pd.DataFrame, List[List[float]]]) -> "BiometricEnsemble":
        arr = np.asarray(X, dtype=np.float64)
        if arr.ndim == 1:
            arr = arr.reshape(1, -1)
        self.primary_model.fit(arr)
        self.mahal_model.fit(arr)
        self.ae_model.fit(arr)
        self.is_fitted = True
        return self

    def score(self, X: Union[np.ndarray, pd.DataFrame, List[float], List[List[float]]]) -> float:
        if not self.is_fitted:
            return 0.5
        s_primary = self.primary_model.score(X)
        s_mahal = self.mahal_model.score(X)
        s_ae = self.ae_model.score(X)

        w_p = self.weights["primary"]
        w_m = self.weights["mahalanobis"]
        w_ae = self.weights["autoencoder"]
        total_w = w_p + w_m + w_ae

        fused = (w_p * s_primary + w_m * s_mahal + w_ae * s_ae) / max(total_w, 1e-6)
        return float(np.clip(fused, 0.0, 1.0))

    def detailed_score(self, X: Union[np.ndarray, pd.DataFrame, List[float], List[List[float]]]) -> Dict[str, float]:
        return {
            "fused": self.score(X),
            "primary": self.primary_model.score(X),
            "mahalanobis": self.mahal_model.score(X),
            "autoencoder": self.ae_model.score(X),
        }

    def predict(self, X: Union[np.ndarray, pd.DataFrame, List[List[float]]]) -> np.ndarray:
        if not self.is_fitted:
            return np.array([1])
        votes = self.primary_model.predict(X) + self.mahal_model.predict(X) + self.ae_model.predict(X)
        return np.where(votes >= 1, 1, -1)

    def save(self, filepath: str):
        save_model(self, filepath)

    @classmethod
    def load(cls, filepath: str) -> "BiometricEnsemble":
        return load_model(filepath)
