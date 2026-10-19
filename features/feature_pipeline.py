from typing import Dict, Any, List
import pandas as pd
from .keystroke_features import extract_keystroke_features, KEYSTROKE_FEATURE_NAMES
from .mouse_features import extract_mouse_features, MOUSE_FEATURE_NAMES
from .motion_features import extract_motion_features, MOTION_FEATURE_NAMES
from .touch_features import extract_touch_features, TOUCH_FEATURE_NAMES

class FeaturePipeline:
    @staticmethod
    def extract_keystroke(events: List[Dict[str, Any]]) -> Dict[str, float]:
        return extract_keystroke_features(events)

    @staticmethod
    def extract_mouse(events: List[Dict[str, Any]]) -> Dict[str, float]:
        return extract_mouse_features(events)

    @staticmethod
    def extract_motion(events: List[Dict[str, Any]]) -> Dict[str, float]:
        return extract_motion_features(events)

    @staticmethod
    def extract_touch(events: List[Dict[str, Any]]) -> Dict[str, float]:
        return extract_touch_features(events)

    @classmethod
    def extract_all(cls, raw_data: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
        raw_events = raw_data.get("raw_events", {})
        k_events = raw_events.get("keystroke", [])
        m_events = raw_events.get("mouse", [])
        mot_events = raw_events.get("motion", [])
        tch_events = raw_events.get("touch", [])

        return {
            "keystroke": cls.extract_keystroke(k_events),
            "mouse": cls.extract_mouse(m_events),
            "motion": cls.extract_motion(mot_events),
            "touch": cls.extract_touch(tch_events)
        }

    @classmethod
    def to_dataframe(cls, feature_dict: Dict[str, float]) -> pd.DataFrame:
        return pd.DataFrame([feature_dict])

    @staticmethod
    def get_feature_names(modality: str) -> List[str]:
        if modality == "keystroke":
            return KEYSTROKE_FEATURE_NAMES
        elif modality == "mouse":
            return MOUSE_FEATURE_NAMES
        elif modality == "motion":
            return MOTION_FEATURE_NAMES
        elif modality == "touch":
            return TOUCH_FEATURE_NAMES
        return []
