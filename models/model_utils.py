import hashlib
import hmac
import os
from pathlib import Path
from typing import Any

import joblib
import numpy as np

_HMAC_KEY = os.environ.get("DDNA_MODEL_HMAC_KEY", "ddna_default_hmac_key_v1").encode()
_SIG_SUFFIX = ".sig"


def _compute_file_hmac(filepath: Path) -> str:
    h = hmac.new(_HMAC_KEY, digestmod=hashlib.sha256)
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def save_model(model: Any, filepath: str):
    p = Path(filepath)
    p.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, p)
    sig = _compute_file_hmac(p)
    (p.parent / (p.name + _SIG_SUFFIX)).write_text(sig, encoding="utf-8")


def load_model(filepath: str) -> Any:
    p = Path(filepath)
    sig_path = p.parent / (p.name + _SIG_SUFFIX)
    if sig_path.exists():
        expected = sig_path.read_text(encoding="utf-8").strip()
        actual = _compute_file_hmac(p)
        if not hmac.compare_digest(expected, actual):
            raise SecurityError(f"Model integrity check failed for {p.name}")
    return joblib.load(p)


def calibrated_score(
    raw_scores: np.ndarray,
    train_mean: float,
    train_std: float,
    shift: float = 1.8,
    scale: float = 1.0,
) -> np.ndarray:
    safe_std = max(float(train_std), 1e-4) if train_std is not None else 1.0
    safe_mean = float(train_mean) if train_mean is not None else 0.0
    z = (raw_scores - safe_mean) / safe_std
    return _shifted_sigmoid(z, shift, scale)


def inverted_calibrated_score(
    distances: np.ndarray,
    train_mean: float,
    train_std: float,
    shift: float = 1.8,
    scale: float = 1.0,
) -> np.ndarray:
    z = (train_mean - distances) / max(float(train_std), 1e-4)
    return _shifted_sigmoid(z, shift, scale)


def _shifted_sigmoid(z: np.ndarray, shift: float, scale: float) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip((z + shift) * scale, -10.0, 10.0)))


def decision_function_to_score(decision: np.ndarray, scale: float = 1.0) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-scale * np.clip(decision, -10.0, 10.0)))


def isolation_score_to_similarity(scores: np.ndarray) -> np.ndarray:
    return np.clip(scores + 0.5, 0.0, 1.0)


class SecurityError(Exception):
    pass
