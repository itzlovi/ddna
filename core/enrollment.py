import time
from typing import Dict, Any, List, Optional
import pandas as pd
from features.feature_pipeline import FeaturePipeline
from models.keystroke_model import KeystrokeModel
from models.mouse_model import MouseModel
from models.ensemble_scorer import BiometricEnsemble
from .profile_manager import ProfileManager
from .raw_event_store import RawEventStore
from .window_buffer import WindowBuffer
from .config import config

class EnrollmentManager:
    def __init__(self, user_id: str, profile_manager: ProfileManager):
        self.user_id = user_id
        self.profile_manager = profile_manager
        self.keystroke_samples: List[Dict[str, float]] = []
        self.mouse_samples: List[Dict[str, float]] = []
        self.window_buffer = WindowBuffer(step_seconds=config.window.step_duration_seconds)
        self.raw_store = RawEventStore(
            self.profile_manager.get_profile_path(self.user_id),
            session_id=f"session_{int(time.time())}"
        )

    def reset_session(self, new_user_id: Optional[str] = None):
        if new_user_id:
            self.user_id = new_user_id
        self.keystroke_samples.clear()
        self.mouse_samples.clear()
        self.window_buffer.clear()
        self.raw_store = RawEventStore(
            self.profile_manager.get_profile_path(self.user_id),
            session_id=f"session_{int(time.time())}"
        )

    def add_window(self, raw_window_data: Dict[str, Any]):
        # Persist raw events to session JSONL
        try:
            self.raw_store.append(raw_window_data)
        except Exception:
            pass

        # Rolling window buffer for multi-scale analysis
        self.window_buffer.add(raw_window_data)

        features = FeaturePipeline.extract_all(raw_window_data)
        k_feats = features.get("keystroke", {})
        m_feats = features.get("mouse", {})

        if k_feats.get("mean_dwell_time", 0.0) > 0.0 or k_feats.get("words_per_minute", 0.0) > 0.0:
            self.keystroke_samples.append(k_feats)

        if m_feats.get("mean_speed", 0.0) > 0.0:
            self.mouse_samples.append(m_feats)

    def is_ready(self, min_samples: Optional[int] = None) -> bool:
        thresh = min_samples if min_samples is not None else config.window.min_training_windows
        return len(self.keystroke_samples) >= thresh and len(self.mouse_samples) >= thresh

    def train_and_save(self) -> Dict[str, Any]:
        k_df = pd.DataFrame(self.keystroke_samples)
        m_df = pd.DataFrame(self.mouse_samples)

        # Fit Tri-Model Biometric Ensembles (Primary + Mahalanobis + Autoencoder)
        k_ensemble = BiometricEnsemble(modality="keystroke").fit(k_df.values)
        m_ensemble = BiometricEnsemble(modality="mouse").fit(m_df.values)

        p_dir = self.profile_manager.get_profile_path(self.user_id)
        p_dir.mkdir(parents=True, exist_ok=True)

        k_ens_path = str(p_dir / "keystroke_ensemble.joblib")
        m_ens_path = str(p_dir / "mouse_ensemble.joblib")
        k_ensemble.save(k_ens_path)
        m_ensemble.save(m_ens_path)

        # Also save primary models for backward compatibility
        k_path = str(p_dir / "keystroke_model.joblib")
        m_path = str(p_dir / "mouse_model.joblib")
        k_ensemble.primary_model.save(k_path)
        m_ensemble.primary_model.save(m_path)

        metadata = {
            "user_id": self.user_id,
            "enrolled_at": time.time(),
            "keystroke_samples_count": len(self.keystroke_samples),
            "mouse_samples_count": len(self.mouse_samples),
            "keystroke_model_path": k_path,
            "mouse_model_path": m_path,
            "keystroke_ensemble_path": k_ens_path,
            "mouse_ensemble_path": m_ens_path,
            "calibration": {
                "keystroke_mean": getattr(k_ensemble.primary_model, "train_mean", 0.0),
                "keystroke_std": getattr(k_ensemble.primary_model, "train_std", 1.0),
                "mouse_mean": getattr(m_ensemble.primary_model, "train_mean", 0.0),
                "mouse_std": getattr(m_ensemble.primary_model, "train_std", 1.0),
                "keystroke_mahal_mean": getattr(k_ensemble.mahal_model, "train_mean", 0.0),
                "mouse_mahal_mean": getattr(m_ensemble.mahal_model, "train_mean", 0.0),
                "keystroke_ae_mean": getattr(k_ensemble.ae_model, "train_mean", 0.0),
                "mouse_ae_mean": getattr(m_ensemble.ae_model, "train_mean", 0.0),
            }
        }
        self.profile_manager.create_or_update_metadata(self.user_id, metadata)
        self.save_samples()
        return metadata

    def save_samples(self):
        """Persist collected feature samples to disk in the profile folder."""
        p_dir = self.profile_manager.get_profile_path(self.user_id)
        p_dir.mkdir(parents=True, exist_ok=True)
        if self.keystroke_samples:
            pd.DataFrame(self.keystroke_samples).to_csv(p_dir / "keystroke_samples.csv", index=False)
        if self.mouse_samples:
            pd.DataFrame(self.mouse_samples).to_csv(p_dir / "mouse_samples.csv", index=False)

    def load_samples(self) -> bool:
        """Load previously saved feature samples from disk if they exist."""
        p_dir = self.profile_manager.get_profile_path(self.user_id)
        k_file = p_dir / "keystroke_samples.csv"
        m_file = p_dir / "mouse_samples.csv"
        loaded = False
        if k_file.exists():
            try:
                df = pd.read_csv(k_file)
                self.keystroke_samples = df.to_dict(orient="records")
                loaded = True
            except Exception:
                pass
        if m_file.exists():
            try:
                df = pd.read_csv(m_file)
                self.mouse_samples = df.to_dict(orient="records")
                loaded = True
            except Exception:
                pass
        return loaded
