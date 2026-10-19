import math
import numpy as np
from typing import List, Dict, Any

TOUCH_FEATURE_NAMES = [
    "mean_touch_pressure",
    "std_touch_pressure",
    "mean_touch_area",
    "mean_stroke_length",
    "mean_stroke_velocity",
    "mean_stroke_duration"
]

def extract_touch_features(raw_events: List[Dict[str, Any]]) -> Dict[str, float]:
    if not raw_events:
        return {name: 0.0 for name in TOUCH_FEATURE_NAMES}

    pressures = [e["pressure"] for e in raw_events if "pressure" in e]
    areas = [e["area"] for e in raw_events if "area" in e]

    mean_press = float(np.mean(pressures)) if pressures else 0.0
    std_press = float(np.std(pressures)) if len(pressures) > 1 else 0.0
    mean_ar = float(np.mean(areas)) if areas else 0.0

    lengths = []
    velocities = []
    durations = []

    current_stroke = []
    for e in raw_events:
        action = e.get("type")
        if action == "down":
            current_stroke = [e]
        elif action == "move" and current_stroke:
            current_stroke.append(e)
        elif action == "up" and current_stroke:
            current_stroke.append(e)
            if len(current_stroke) >= 2:
                dx = current_stroke[-1]["x"] - current_stroke[0]["x"]
                dy = current_stroke[-1]["y"] - current_stroke[0]["y"]
                dt = current_stroke[-1]["timestamp"] - current_stroke[0]["timestamp"]
                dist = math.hypot(dx, dy)
                lengths.append(dist)
                durations.append(max(0.001, dt))
                velocities.append(dist / max(0.001, dt))
            current_stroke = []

    mean_len = float(np.mean(lengths)) if lengths else 0.0
    mean_vel = float(np.mean(velocities)) if velocities else 0.0
    mean_dur = float(np.mean(durations)) if durations else 0.0

    return {
        "mean_touch_pressure": mean_press,
        "std_touch_pressure": std_press,
        "mean_touch_area": mean_ar,
        "mean_stroke_length": mean_len,
        "mean_stroke_velocity": mean_vel,
        "mean_stroke_duration": mean_dur
    }
