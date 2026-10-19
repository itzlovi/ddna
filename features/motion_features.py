import numpy as np
from typing import List, Dict, Any

MOTION_FEATURE_NAMES = [
    "mean_accel_magnitude",
    "std_accel_magnitude",
    "max_accel_magnitude",
    "zero_crossing_rate",
    "mean_gyro_magnitude",
    "std_gyro_magnitude",
    "dominant_frequency_hz",
    "spectral_energy"
]

def extract_motion_features(raw_events: List[Dict[str, Any]]) -> Dict[str, float]:
    if not raw_events:
        return {name: 0.0 for name in MOTION_FEATURE_NAMES}

    accel_mags = []
    gyro_mags = []
    for e in raw_events:
        if e.get("type") == "motion":
            ax, ay, az = e.get("ax", 0.0), e.get("ay", 0.0), e.get("az", 0.0)
            gx, gy, gz = e.get("gx", 0.0), e.get("gy", 0.0), e.get("gz", 0.0)
            accel_mags.append(float(np.sqrt(ax * ax + ay * ay + az * az)))
            gyro_mags.append(float(np.sqrt(gx * gx + gy * gy + gz * gz)))

    if not accel_mags:
        return {name: 0.0 for name in MOTION_FEATURE_NAMES}

    mean_acc = float(np.mean(accel_mags))
    std_acc = float(np.std(accel_mags)) if len(accel_mags) > 1 else 0.0
    max_acc = float(np.max(accel_mags))

    centered = np.array(accel_mags) - mean_acc
    zero_crossings = np.sum(np.diff(np.signbit(centered)).astype(bool))
    zcr = float(zero_crossings / len(accel_mags)) if len(accel_mags) > 1 else 0.0

    mean_gyro = float(np.mean(gyro_mags)) if gyro_mags else 0.0
    std_gyro = float(np.std(gyro_mags)) if len(gyro_mags) > 1 else 0.0

    dominant_freq = 0.0
    spectral_energy = float(np.sum(np.square(centered)))
    if len(centered) >= 16:
        fft_vals = np.abs(np.fft.rfft(centered))
        dominant_freq = float(np.argmax(fft_vals[1:]) + 1)

    return {
        "mean_accel_magnitude": mean_acc,
        "std_accel_magnitude": std_acc,
        "max_accel_magnitude": max_acc,
        "zero_crossing_rate": zcr,
        "mean_gyro_magnitude": mean_gyro,
        "std_gyro_magnitude": std_gyro,
        "dominant_frequency_hz": dominant_freq,
        "spectral_energy": spectral_energy
    }
