import time
import sys
import threading
from typing import Dict, Any, Optional, Callable
from collectors.desktop.main_collector import DesktopCollector
from features.feature_pipeline import FeaturePipeline
from models.keystroke_model import KeystrokeModel
from models.mouse_model import MouseModel
from fusion.score_fusion import ScoreFusion
from fusion.trust_score import TrustScoreEngine
from fusion.decision_engine import DecisionEngine
from .profile_manager import ProfileManager
from .config import config

class ContinuousAuthEngine:
    def __init__(
        self,
        user_id: str,
        profile_manager: Optional[ProfileManager] = None,
        on_tick: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_decision: Optional[Callable[[Dict[str, Any]], None]] = None,
        auto_lock_system: bool = False
    ):
        self.user_id = user_id
        self.profile_manager = profile_manager or ProfileManager()
        self.on_tick = on_tick
        self.on_decision = on_decision
        self.auto_lock_system = auto_lock_system

        self.collector = DesktopCollector(user_id=self.user_id)
        self.score_fusion = ScoreFusion()
        self.trust_engine = TrustScoreEngine(alpha=config.fusion.ema_alpha)
        self.decision_engine = DecisionEngine(
            threshold_allow=config.fusion.threshold_allow,
            threshold_warn=config.fusion.threshold_warn,
            max_consecutive_violations=config.fusion.consecutive_violations_lock
        )

        self.keystroke_model: Optional[KeystrokeModel] = None
        self.mouse_model: Optional[MouseModel] = None
        self._load_models()

        self._running = False
        self._thread: Optional[threading.Thread] = None

    def _load_models(self):
        p_dir = self.profile_manager.get_profile_path(self.user_id)
        k_path = p_dir / "keystroke_model.joblib"
        m_path = p_dir / "mouse_model.joblib"

        if k_path.exists():
            self.keystroke_model = KeystrokeModel.load(str(k_path))
        if m_path.exists():
            self.mouse_model = MouseModel.load(str(m_path))

    def reload_models(self):
        self._load_models()

    def process_window(self, raw_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        data = raw_data if raw_data is not None else self.collector.collect_window()
        features = FeaturePipeline.extract_all(data)
        k_feats = features.get("keystroke", {})
        m_feats = features.get("mouse", {})

        k_score = None
        m_score = None

        if self.keystroke_model is not None and (k_feats.get("mean_dwell_time", 0.0) > 0.0 or k_feats.get("words_per_minute", 0.0) > 0.0):
            k_score = self.keystroke_model.score(list(k_feats.values()))

        if self.mouse_model is not None and m_feats.get("mean_speed", 0.0) > 0.0:
            m_score = self.mouse_model.score(list(m_feats.values()))

        fused_similarity = self.score_fusion.fuse({
            "keystroke": k_score,
            "mouse": m_score
        })

        trust_score = self.trust_engine.update(fused_similarity)
        decision_info = self.decision_engine.evaluate(trust_score)

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
            "consecutive_violations": decision_info["consecutive_violations"]
        }

        if decision_info["decision"] == "LOCK" and self.auto_lock_system:
            self._lock_workstation()

        if self.on_tick is not None:
            self.on_tick(result)

        if self.on_decision is not None and decision_info["decision"] in {"WARN", "LOCK"}:
            self.on_decision(result)

        return result

    def _lock_workstation(self):
        if sys.platform == "win32":
            try:
                import ctypes
                ctypes.windll.user32.LockWorkStation()
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
