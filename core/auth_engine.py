import time
import sys
import threading
from typing import Dict, Any, Optional, Callable
from collectors.desktop.main_collector import DesktopCollector
from features.feature_pipeline import FeaturePipeline
from models.keystroke_model import KeystrokeModel
from models.mouse_model import MouseModel
from models.ensemble_scorer import BiometricEnsemble
from fusion.score_fusion import ScoreFusion
from fusion.trust_score import TrustScoreEngine
from fusion.decision_engine import DecisionEngine
from .profile_manager import ProfileManager
from .continuous_learner import ContinuousLearner
from .config import config

class ContinuousAuthEngine:
    def __init__(
        self,
        user_id: str,
        profile_manager: Optional[ProfileManager] = None,
        on_tick: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_decision: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_continuous_update: Optional[Callable[[Dict[str, Any]], None]] = None,
        auto_lock_system: bool = False
    ):
        self.user_id = user_id
        self.profile_manager = profile_manager or ProfileManager()
        self.on_tick = on_tick
        self.on_decision = on_decision
        self.on_continuous_update = on_continuous_update
        self.auto_lock_system = auto_lock_system

        self.collector = DesktopCollector(user_id=self.user_id)
        self.score_fusion = ScoreFusion()
        self.trust_engine = TrustScoreEngine(alpha=config.fusion.ema_alpha)
        self.decision_engine = DecisionEngine(
            threshold_allow=config.fusion.threshold_allow,
            threshold_warn=config.fusion.threshold_warn,
            max_consecutive_violations=config.fusion.consecutive_violations_lock
        )

        self.continuous_learner = ContinuousLearner(
            user_id=self.user_id,
            profile_manager=self.profile_manager,
            on_model_updated=self._on_continuous_retrain
        )

        self.keystroke_model: Optional[KeystrokeModel] = None
        self.mouse_model: Optional[MouseModel] = None
        self._load_models()

        self._running = False
        self._thread: Optional[threading.Thread] = None

    def _load_models(self):
        p_dir = self.profile_manager.get_profile_path(self.user_id)
        k_ens_path = p_dir / "keystroke_ensemble.joblib"
        m_ens_path = p_dir / "mouse_ensemble.joblib"
        k_path = p_dir / "keystroke_model.joblib"
        m_path = p_dir / "mouse_model.joblib"

        if k_ens_path.exists():
            self.keystroke_model = BiometricEnsemble.load(str(k_ens_path))
        elif k_path.exists():
            self.keystroke_model = KeystrokeModel.load(str(k_path))
        else:
            self.keystroke_model = None

        if m_ens_path.exists():
            self.mouse_model = BiometricEnsemble.load(str(m_ens_path))
        elif m_path.exists():
            self.mouse_model = MouseModel.load(str(m_path))
        else:
            self.mouse_model = None

    def reload_models(self):
        self._load_models()
        self.continuous_learner.user_id = self.user_id
        self.continuous_learner.reset()

    def _on_continuous_retrain(self, update_info: Dict[str, Any]):
        if "cand_k" in update_info:
            self.keystroke_model = update_info["cand_k"]
        if "cand_m" in update_info:
            self.mouse_model = update_info["cand_m"]
        if self.on_continuous_update is not None:
            self.on_continuous_update(update_info)

    def _is_window_sparse(self, raw_events: Dict[str, Any]) -> bool:
        """
        Check if a window has too little activity to produce meaningful features.

        Scoring a sparse window produces mostly-zero feature vectors, which models
        treat as anomalies. This causes false lockouts during brief idle moments
        (reading, thinking, watching a video).
        """
        k_events = raw_events.get("keystroke", [])
        m_events = raw_events.get("mouse", [])

        k_count = len(k_events)
        m_count = len([e for e in m_events if e.get("type") == "move"])

        has_enough_keys = k_count >= config.window.min_keystrokes_per_window
        has_enough_mouse = m_count >= config.window.min_mouse_events_per_window

        # Need at least one modality with enough data
        return not (has_enough_keys or has_enough_mouse)

    def process_window(self, raw_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        data = raw_data if raw_data is not None else self.collector.collect_window()
        raw_events = data.get("raw_events", {})

        # Skip sparse windows — treat as idle instead of scoring zeros
        if self._is_window_sparse(raw_events):
            trust_score = self.trust_engine.update(None, is_idle=True)
            decision_info = self.decision_engine.evaluate(trust_score, is_idle=True)
            result = {
                "timestamp": time.time(),
                "user_id": self.user_id,
                "modality_scores": {"keystroke": None, "mouse": None},
                "fused_similarity": None,
                "trust_score": trust_score,
                "decision": decision_info["decision"],
                "consecutive_violations": decision_info["consecutive_violations"],
                "is_idle": True
            }
            if self.on_tick is not None:
                self.on_tick(result)
            return result

        features = FeaturePipeline.extract_all(data)
        k_feats = features.get("keystroke", {})
        m_feats = features.get("mouse", {})

        k_score = None
        m_score = None

        if self.keystroke_model is not None and (k_feats.get("mean_dwell_time", 0.0) > 0.0 or k_feats.get("words_per_minute", 0.0) > 0.0):
            k_score = self.keystroke_model.score(list(k_feats.values()))

        if self.mouse_model is not None and m_feats.get("mean_speed", 0.0) > 0.0:
            m_score = self.mouse_model.score(list(m_feats.values()))

        is_idle = (k_score is None and m_score is None)

        fused_similarity = self.score_fusion.fuse({
            "keystroke": k_score,
            "mouse": m_score
        }) if not is_idle else None

        trust_score = self.trust_engine.update(fused_similarity, is_idle=is_idle)
        decision_info = self.decision_engine.evaluate(trust_score, is_idle=is_idle)

        result = {
            "timestamp": time.time(),
            "user_id": self.user_id,
            "modality_scores": {
                "keystroke": k_score,
                "mouse": m_score
            },
            "fused_similarity": fused_similarity,
            "trust_score": trust_score,
            "decision": decision_info["decision"],
            "consecutive_violations": decision_info["consecutive_violations"],
            "is_idle": is_idle
        }

        if decision_info["decision"] == "LOCK" and self.auto_lock_system:
            self._lock_workstation()

        if self.on_tick is not None:
            self.on_tick(result)

        # Accumulate confirmed genuine samples for continuous learning & adaptation
        if not is_idle:
            try:
                self.continuous_learner.process_authenticated_window(
                    features=features,
                    trust_score=trust_score,
                    decision=decision_info["decision"],
                    fused_similarity=fused_similarity
                )
            except Exception:
                pass

        return result

    def _lock_workstation(self):
        if sys.platform == "win32":
            try:
                import ctypes
                ctypes.windll.user32.LockWorkStation()
            except Exception:
                pass
        elif sys.platform == "darwin":
            try:
                import subprocess
                subprocess.run(["pmset", "displaysleepnow"], check=False)
            except Exception:
                pass
        elif sys.platform.startswith("linux"):
            try:
                import subprocess
                res = subprocess.run(["loginctl", "lock-session"], check=False)
                if res.returncode != 0:
                    subprocess.run(["xdg-screensaver", "lock"], check=False)
            except Exception:
                pass

    def _loop(self):
        while self._running:
            time.sleep(config.window.step_duration_seconds)
            self.process_window()

    def start(self):
        if self._running:
            return
        self._running = True
        self.collector.start()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        self.collector.stop()
        if self._thread is not None:
            self._thread.join(timeout=2.0)
            self._thread = None
