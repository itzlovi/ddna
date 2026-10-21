"""
Synthetic Benchmark Dataset and Seed Profile Generator for Digital DNA.
Generates genuine and impostor behavioral biometrics data and initializes default profile.
"""

import os
import sys
import time
import json
from pathlib import Path

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import numpy as np
import pandas as pd

from features.keystroke_features import KEYSTROKE_FEATURE_NAMES
from features.mouse_features import MOUSE_FEATURE_NAMES
from models.keystroke_model import KeystrokeModel
from models.mouse_model import MouseModel
from core.profile_manager import ProfileManager
from core.config import config

np.random.seed(42)

def generate_keystroke_samples(n_samples: int, is_genuine: bool = True) -> pd.DataFrame:
    if is_genuine:
        dwell = np.random.normal(0.095, 0.012, n_samples).clip(0.04, 0.20)
        dwell_std = np.random.normal(0.025, 0.005, n_samples).clip(0.01, 0.06)
        flight = np.random.normal(0.140, 0.020, n_samples).clip(0.06, 0.25)
        flight_std = np.random.normal(0.040, 0.008, n_samples).clip(0.015, 0.09)
        digraph = np.random.normal(0.240, 0.025, n_samples).clip(0.12, 0.40)
        trigraph = np.random.normal(0.480, 0.040, n_samples).clip(0.25, 0.75)
        rhythm = (flight_std / (flight + 1e-6)).clip(0.1, 0.5)
        error_rate = np.random.normal(0.03, 0.01, n_samples).clip(0.0, 0.08)
        wpm = np.random.normal(64.0, 6.0, n_samples).clip(45.0, 85.0)
        pause_500 = np.random.normal(0.08, 0.02, n_samples).clip(0.01, 0.20)
        pause_1000 = np.random.normal(0.02, 0.01, n_samples).clip(0.0, 0.08)
        max_pause = np.random.normal(1.2, 0.25, n_samples).clip(0.4, 2.5)
        pause_ratio = np.random.normal(0.07, 0.02, n_samples).clip(0.01, 0.18)
    else:
        # Impostor: noticeably slower, more variable, higher pause rate
        dwell = np.random.normal(0.165, 0.025, n_samples).clip(0.08, 0.35)
        dwell_std = np.random.normal(0.055, 0.012, n_samples).clip(0.02, 0.12)
        flight = np.random.normal(0.260, 0.035, n_samples).clip(0.12, 0.50)
        flight_std = np.random.normal(0.085, 0.018, n_samples).clip(0.03, 0.18)
        digraph = np.random.normal(0.420, 0.050, n_samples).clip(0.20, 0.70)
        trigraph = np.random.normal(0.820, 0.080, n_samples).clip(0.45, 1.30)
        rhythm = (flight_std / (flight + 1e-6)).clip(0.25, 0.8)
        error_rate = np.random.normal(0.11, 0.03, n_samples).clip(0.04, 0.25)
        wpm = np.random.normal(32.0, 7.0, n_samples).clip(15.0, 48.0)
        pause_500 = np.random.normal(0.22, 0.05, n_samples).clip(0.08, 0.45)
        pause_1000 = np.random.normal(0.09, 0.03, n_samples).clip(0.02, 0.25)
        max_pause = np.random.normal(2.8, 0.6, n_samples).clip(1.2, 6.0)
        pause_ratio = np.random.normal(0.20, 0.05, n_samples).clip(0.06, 0.45)

    data = {
        "mean_dwell_time": dwell,
        "std_dwell_time": dwell_std,
        "median_dwell_time": dwell * 0.98,
        "iqr_dwell_time": dwell_std * 0.85,
        "mean_flight_time": flight,
        "std_flight_time": flight_std,
        "median_flight_time": flight * 0.96,
        "iqr_flight_time": flight_std * 0.82,
        "mean_digraph_time": digraph,
        "std_digraph_time": digraph * 0.22,
        "mean_trigraph_time": trigraph,
        "std_trigraph_time": trigraph * 0.24,
        "rhythm_consistency": rhythm,
        "error_rate": error_rate,
        "words_per_minute": wpm,
        "pause_rate_500ms": pause_500,
        "pause_rate_1000ms": pause_1000,
        "max_pause_duration": max_pause,
        "pause_ratio": pause_ratio,
        "label": 1 if is_genuine else 0
    }
    return pd.DataFrame(data)

def generate_mouse_samples(n_samples: int, is_genuine: bool = True) -> pd.DataFrame:
    if is_genuine:
        speed = np.random.normal(420.0, 45.0, n_samples).clip(250.0, 700.0)
        std_speed = np.random.normal(210.0, 30.0, n_samples).clip(100.0, 350.0)
        acc = np.random.normal(2500.0, 300.0, n_samples).clip(1400.0, 4200.0)
        std_acc = np.random.normal(1200.0, 180.0, n_samples).clip(600.0, 2200.0)
        curvature = np.random.normal(1.15, 0.08, n_samples).clip(1.01, 1.45)
        click_dur = np.random.normal(0.085, 0.012, n_samples).clip(0.04, 0.16)
        click_freq = np.random.normal(0.45, 0.10, n_samples).clip(0.15, 0.90)
        scroll_rate = np.random.normal(0.30, 0.08, n_samples).clip(0.05, 0.70)
        dir_change = np.random.normal(0.18, 0.04, n_samples).clip(0.05, 0.35)
        jerk = np.random.normal(35000.0, 4500.0, n_samples).clip(18000.0, 60000.0)
        entropy = np.random.normal(1.35, 0.15, n_samples).clip(0.8, 1.85)
    else:
        # Impostor: erratic trajectories, higher curvature, higher entropy, slower
        speed = np.random.normal(210.0, 35.0, n_samples).clip(90.0, 350.0)
        std_speed = np.random.normal(140.0, 25.0, n_samples).clip(60.0, 220.0)
        acc = np.random.normal(1100.0, 200.0, n_samples).clip(500.0, 2200.0)
        std_acc = np.random.normal(700.0, 120.0, n_samples).clip(300.0, 1200.0)
        curvature = np.random.normal(1.75, 0.22, n_samples).clip(1.30, 2.60)
        click_dur = np.random.normal(0.160, 0.030, n_samples).clip(0.09, 0.32)
        click_freq = np.random.normal(0.18, 0.06, n_samples).clip(0.04, 0.40)
        scroll_rate = np.random.normal(0.12, 0.04, n_samples).clip(0.01, 0.30)
        dir_change = np.random.normal(0.38, 0.07, n_samples).clip(0.18, 0.65)
        jerk = np.random.normal(12000.0, 2000.0, n_samples).clip(5000.0, 22000.0)
        entropy = np.random.normal(2.15, 0.25, n_samples).clip(1.5, 3.20)

    data = {
        "mean_speed": speed,
        "std_speed": std_speed,
        "max_speed": speed * 2.8,
        "median_speed": speed * 0.92,
        "mean_acceleration": acc,
        "std_acceleration": std_acc,
        "max_acceleration": acc * 3.4,
        "path_curvature": curvature,
        "mean_click_duration": click_dur,
        "std_click_duration": click_dur * 0.25,
        "click_frequency": click_freq,
        "scroll_event_rate": scroll_rate,
        "mean_scroll_magnitude": 1.2 if is_genuine else 0.7,
        "direction_change_rate": dir_change,
        "mean_jerk": jerk,
        "movement_entropy": entropy,
        "label": 1 if is_genuine else 0
    }
    return pd.DataFrame(data)

def generate_and_seed_all(n_samples: int = 200, user_id: str = "user_001"):
    processed_dir = config.paths.processed_dir
    processed_dir.mkdir(parents=True, exist_ok=True)

    print(f"Generating {n_samples} genuine and impostor samples...")
    gen_k = generate_keystroke_samples(n_samples, is_genuine=True)
    imp_k = generate_keystroke_samples(n_samples, is_genuine=False)
    gen_m = generate_mouse_samples(n_samples, is_genuine=True)
    imp_m = generate_mouse_samples(n_samples, is_genuine=False)

    # Save datasets
    gen_k.to_csv(processed_dir / "genuine_keystroke.csv", index=False)
    imp_k.to_csv(processed_dir / "impostor_keystroke.csv", index=False)
    gen_m.to_csv(processed_dir / "genuine_mouse.csv", index=False)
    imp_m.to_csv(processed_dir / "impostor_mouse.csv", index=False)

    # Save combined benchmark datasets
    k_all = pd.concat([gen_k, imp_k], ignore_index=True)
    m_all = pd.concat([gen_m, imp_m], ignore_index=True)
    k_all.to_csv(processed_dir / "benchmark_keystroke.csv", index=False)
    m_all.to_csv(processed_dir / "benchmark_mouse.csv", index=False)

    print(f"Saved benchmark CSVs to {processed_dir}")

    # Train and seed baseline models for user_id
    p_mgr = ProfileManager()
    profile_dir = p_mgr.get_profile_path(user_id)
    profile_dir.mkdir(parents=True, exist_ok=True)

    k_features = [c for c in KEYSTROKE_FEATURE_NAMES if c in gen_k.columns]
    m_features = [c for c in MOUSE_FEATURE_NAMES if c in gen_m.columns]

    print(f"Fitting KeystrokeModel for {user_id} on {len(gen_k)} genuine samples...")
    k_model = KeystrokeModel(nu=config.model.ocsvm_nu, kernel="rbf", gamma=config.model.ocsvm_gamma)
    k_model.fit(gen_k[k_features].values)
    k_path = profile_dir / "keystroke_model.joblib"
    k_model.save(str(k_path))

    print(f"Fitting MouseModel for {user_id} on {len(gen_m)} genuine samples...")
    m_model = MouseModel(contamination=config.model.contamination, n_estimators=config.model.n_estimators)
    m_model.fit(gen_m[m_features].values)
    m_path = profile_dir / "mouse_model.joblib"
    m_model.save(str(m_path))

    metadata = {
        "user_id": user_id,
        "enrolled_at": time.time(),
        "keystroke_samples_count": len(gen_k),
        "mouse_samples_count": len(gen_m),
        "keystroke_model_path": str(k_path),
        "mouse_model_path": str(m_path),
        "is_seed_profile": True
    }
    p_mgr.create_or_update_metadata(user_id, metadata)
    print(f"Profile {user_id} successfully seeded at {profile_dir}!")

if __name__ == "__main__":
    generate_and_seed_all()
