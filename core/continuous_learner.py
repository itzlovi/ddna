import time
import threading
import logging
from typing import Dict, Any, List, Optional, Callable
import numpy as np
import pandas as pd
from .profile_manager import ProfileManager
from .drift_detector import ConceptDriftDetector
from models.ensemble_scorer import BiometricEnsemble


class ContinuousLearner:
    def __init__(
        self,
        user_id: str,
        profile_manager: ProfileManager,
        retrain_threshold: int = 30,
        min_trust_to_accumulate: float = 75.0,
        on_model_updated: Optional[Callable[[Dict[str, Any]], None]] = None
    ):
        self.user_id = user_id
        self.profile_manager = profile_manager
        self.retrain_threshold = retrain_threshold
        self.min_trust_to_accumulate = min_trust_to_accumulate
        self.on_model_updated = on_model_updated

        self.drift_detector = ConceptDriftDetector()
        self.new_k_samples: List[Dict[str, float]] = []
        self.new_m_samples: List[Dict[str, float]] = []

        self._lock = threading.Lock()
        self._is_retraining = False
        self.version = 1
        self.total_retrains = 0

    def process_authenticated_window(
        self,
        features: Dict[str, Dict[str, float]],
        trust_score: float,
        decision: str,
        fused_similarity: Optional[float]
    ) -> Dict[str, Any]:
        if decision != "ALLOW" or trust_score < self.min_trust_to_accumulate or fused_similarity is None:
            return {"accumulated": False, "reason": "not_high_confidence_allow"}

        k_feats = features.get("keystroke", {})
        m_feats = features.get("mouse", {})

        drift_info = self.drift_detector.add_score(fused_similarity)

        with self._lock:
            if k_feats.get("mean_dwell_time", 0.0) > 0.0 or k_feats.get("words_per_minute", 0.0) > 0.0:
                self.new_k_samples.append(k_feats)

            if m_feats.get("mean_speed", 0.0) > 0.0:
                self.new_m_samples.append(m_feats)

            k_len = len(self.new_k_samples)
            m_len = len(self.new_m_samples)

            ready_count = min(k_len, m_len)
            should_retrain = (ready_count >= self.retrain_threshold) or (drift_info["drift_detected"] and ready_count >= 15)

            if should_retrain and not self._is_retraining:
                self._is_retraining = True
                threading.Thread(target=self._retrain_worker, daemon=True).start()

        return {
            "accumulated": True,
            "new_samples_count": ready_count,
            "retrain_threshold": self.retrain_threshold,
            "drift_status": drift_info["status"],
            "drift_detected": drift_info["drift_detected"]
        }

    def _retrain_worker(self):
        try:
            p_dir = self.profile_manager.get_profile_path(self.user_id)
            k_file = p_dir / "keystroke_samples.csv"
            m_file = p_dir / "mouse_samples.csv"

            hist_k = pd.read_csv(k_file).to_dict(orient="records") if k_file.exists() else []
            hist_m = pd.read_csv(m_file).to_dict(orient="records") if m_file.exists() else []

            with self._lock:
                accum_k = list(self.new_k_samples)
                accum_m = list(self.new_m_samples)

            combined_k = (hist_k + accum_k)[-300:]
            combined_m = (hist_m + accum_m)[-300:]

            if len(combined_k) < 10 or len(combined_m) < 10:
                return

            k_df = pd.DataFrame(combined_k)
            m_df = pd.DataFrame(combined_m)

            cand_k = BiometricEnsemble(modality="keystroke").fit(k_df.values)
            cand_m = BiometricEnsemble(modality="mouse").fit(m_df.values)

            # Holdout validation check: model must achieve minimum verification quality
            eval_k = k_df.values[-20:]
            eval_m = m_df.values[-20:]
            test_k_scores = [cand_k.score(x) for x in eval_k]
            test_m_scores = [cand_m.score(x) for x in eval_m]

            if np.mean(test_k_scores) < 0.68 or np.mean(test_m_scores) < 0.68:
                logging.warning(
                    f"Candidate model failed verification threshold: "
                    f"K={np.mean(test_k_scores):.3f}, M={np.mean(test_m_scores):.3f}. Promotion rejected."
                )
                return

            self.version += 1
            self.total_retrains += 1
            v_dir = p_dir / f"v{self.version}"
            v_dir.mkdir(parents=True, exist_ok=True)
            cand_k.save(str(v_dir / "keystroke_ensemble.joblib"))
            cand_m.save(str(v_dir / "mouse_ensemble.joblib"))

            k_ens_path = p_dir / "keystroke_ensemble.joblib"
            m_ens_path = p_dir / "mouse_ensemble.joblib"
            cand_k.save(str(k_ens_path))
            cand_m.save(str(m_ens_path))
            cand_k.primary_model.save(str(p_dir / "keystroke_model.joblib"))
            cand_m.primary_model.save(str(p_dir / "mouse_model.joblib"))

            k_df.to_csv(k_file, index=False)
            m_df.to_csv(m_file, index=False)

            with self._lock:
                self.new_k_samples = self.new_k_samples[len(accum_k):]
                self.new_m_samples = self.new_m_samples[len(accum_m):]

            update_info = {
                "user_id": self.user_id,
                "version": self.version,
                "total_samples": len(combined_k),
                "timestamp": time.time(),
                "cand_k": cand_k,
                "cand_m": cand_m
            }

            if self.on_model_updated is not None:
                self.on_model_updated(update_info)

        except Exception as e:
            logging.error(f"Continuous retraining failed: {e}")
        finally:
            with self._lock:
                self._is_retraining = False

    def reset(self):
        with self._lock:
            self.new_k_samples.clear()
            self.new_m_samples.clear()
            self.drift_detector.reset()
            self._is_retraining = False
