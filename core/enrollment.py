import time
from typing import Dict, Any, List
import pandas as pd
from features.feature_pipeline import FeaturePipeline
from models.keystroke_model import KeystrokeModel
from models.mouse_model import MouseModel
from .profile_manager import ProfileManager

class EnrollmentManager:
    def __init__(self, user_id: str, profile_manager: ProfileManager):
        self.user_id = user_id
        self.profile_manager = profile_manager
        self.keystroke_samples: List[Dict[str, float]] = []
        self.mouse_samples: List[Dict[str, float]] = []

    def add_window(self, raw_window_data: Dict[str, Any]):
        features = FeaturePipeline.extract_all(raw_window_data)
        k_feats = features.get("keystroke", {})
        m_feats = features.get("mouse", {})

        if k_feats.get("mean_dwell_time", 0.0) > 0.0 or k_feats.get("words_per_minute", 0.0) > 0.0:
            self.keystroke_samples.append(k_feats)

        if m_feats.get("mean_speed", 0.0) > 0.0:
            self.mouse_samples.append(m_feats)

    def is_ready(self, min_samples: int = 5) -> bool:
        return len(self.keystroke_samples) >= min_samples and len(self.mouse_samples) >= min_samples

    def train_and_save(self) -> Dict[str, Any]:
        k_df = pd.DataFrame(self.keystroke_samples)
        m_df = pd.DataFrame(self.mouse_samples)

        k_model = KeystrokeModel().fit(k_df.values)
        m_model = MouseModel().fit(m_df.values)

        p_dir = self.profile_manager.get_profile_path(self.user_id)
        p_dir.mkdir(parents=True, exist_ok=True)

        k_path = str(p_dir / "keystroke_model.joblib")
        m_path = str(p_dir / "mouse_model.joblib")

        k_model.save(k_path)
        m_model.save(m_path)

        metadata = {
            "user_id": self.user_id,
            "enrolled_at": time.time(),
            "keystroke_samples_count": len(self.keystroke_samples),
            "mouse_samples_count": len(self.mouse_samples),
            "keystroke_model_path": k_path,
            "mouse_model_path": m_path
        }
        self.profile_manager.create_or_update_metadata(self.user_id, metadata)
        return metadata
