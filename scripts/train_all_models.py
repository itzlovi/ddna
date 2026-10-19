import sys
import argparse
import pandas as pd
from pathlib import Path
from features.feature_pipeline import FeaturePipeline
from models.keystroke_model import KeystrokeModel
from models.mouse_model import MouseModel
from core.profile_manager import ProfileManager
from core.config import config

def train_models_for_user(user_id: str, data_csv_or_dir: str):
    p_mgr = ProfileManager()
    path = Path(data_csv_or_dir)

    k_df = None
    m_df = None

    if path.is_file() and path.suffix == ".csv":
        df = pd.read_csv(path)
        k_cols = [c for c in FeaturePipeline.get_feature_names("keystroke") if c in df.columns]
        m_cols = [c for c in FeaturePipeline.get_feature_names("mouse") if c in df.columns]
        if k_cols:
            k_df = df[k_cols].dropna()
        if m_cols:
            m_df = df[m_cols].dropna()

    p_dir = p_mgr.get_profile_path(user_id)
    p_dir.mkdir(parents=True, exist_ok=True)

    if k_df is not None and not k_df.empty:
        k_model = KeystrokeModel().fit(k_df.values)
        k_model.save(str(p_dir / "keystroke_model.joblib"))

    if m_df is not None and not m_df.empty:
        m_model = MouseModel().fit(m_df.values)
        m_model.save(str(p_dir / "mouse_model.joblib"))

    p_mgr.create_or_update_metadata(user_id, {
        "user_id": user_id,
        "trained_from": str(path),
        "keystroke_count": len(k_df) if k_df is not None else 0,
        "mouse_count": len(m_df) if m_df is not None else 0
    })

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--user", required=True)
    parser.add_argument("--data", required=True)
    args = parser.parse_args()
    train_models_for_user(args.user, args.data)

if __name__ == "__main__":
    main()
