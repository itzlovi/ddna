import math
import numpy as np
from typing import List, Dict, Any

MOUSE_FEATURE_NAMES = [
    "mean_speed",
    "std_speed",
    "max_speed",
    "median_speed",
    "mean_acceleration",
    "std_acceleration",
    "max_acceleration",
    "path_curvature",
    "mean_click_duration",
    "std_click_duration",
    "click_frequency",
    "scroll_event_rate",
    "mean_scroll_magnitude",
    "direction_change_rate",
    "mean_jerk",
    "movement_entropy"
]

def extract_mouse_features(raw_events: List[Dict[str, Any]]) -> Dict[str, float]:
    if not raw_events:
        return {name: 0.0 for name in MOUSE_FEATURE_NAMES}

    move_events = [e for e in raw_events if e.get("type") == "move"]
    click_releases = [e for e in raw_events if e.get("type") == "click_release" and "duration" in e]
    click_presses = [e for e in raw_events if e.get("type") == "click_press"]
    scroll_events = [e for e in raw_events if e.get("type") == "scroll"]

    speeds = [e["speed"] for e in move_events if "speed" in e and e["speed"] >= 0.0]
    accelerations = [e["acceleration"] for e in move_events if "acceleration" in e and e["acceleration"] >= 0.0]

    mean_speed = float(np.mean(speeds)) if speeds else 0.0
    std_speed = float(np.std(speeds)) if len(speeds) > 1 else 0.0
    max_speed = float(np.max(speeds)) if speeds else 0.0
    median_speed = float(np.median(speeds)) if speeds else 0.0

    mean_acc = float(np.mean(accelerations)) if accelerations else 0.0
    std_acc = float(np.std(accelerations)) if len(accelerations) > 1 else 0.0
    max_acc = float(np.max(accelerations)) if accelerations else 0.0

    path_curvature = 1.0
    direction_change_rate = 0.0
    mean_jerk = 0.0
    movement_entropy = 0.0

    if len(move_events) >= 3:
        trajectory_length = sum(e.get("distance", 0.0) for e in move_events)
        x0, y0 = move_events[0]["x"], move_events[0]["y"]
        x1, y1 = move_events[-1]["x"], move_events[-1]["y"]
        euclidean_dist = math.hypot(x1 - x0, y1 - y0)
        path_curvature = float(trajectory_length / (euclidean_dist + 1e-4))

        angles = []
        for i in range(1, len(move_events)):
            dx = move_events[i]["x"] - move_events[i - 1]["x"]
            dy = move_events[i]["y"] - move_events[i - 1]["y"]
            angles.append(math.atan2(dy, dx))

        angle_diffs = []
        for i in range(1, len(angles)):
            diff = abs(angles[i] - angles[i - 1])
            diff = (diff + math.pi) % (2 * math.pi) - math.pi
            angle_diffs.append(abs(diff))

        sharp_turns = sum(1 for ad in angle_diffs if ad > (math.pi / 4.0))
        direction_change_rate = float(sharp_turns / len(angle_diffs)) if angle_diffs else 0.0

        jerks = []
        for i in range(1, len(accelerations)):
            dt = move_events[i].get("dt", 0.01)
            if dt > 0:
                jerks.append(abs(accelerations[i] - accelerations[i - 1]) / dt)
        mean_jerk = float(np.mean(jerks)) if jerks else 0.0

        if speeds:
            hist, _ = np.histogram(speeds, bins=10, density=True)
            hist = hist[hist > 0]
            movement_entropy = float(-np.sum(hist * np.log2(hist + 1e-9)))

    click_durations = [e["duration"] for e in click_releases]
    mean_click_dur = float(np.mean(click_durations)) if click_durations else 0.0
    std_click_dur = float(np.std(click_durations)) if len(click_durations) > 1 else 0.0

    timestamps = [e["timestamp"] for e in raw_events if "timestamp" in e]
    total_time = (max(timestamps) - min(timestamps)) if len(timestamps) >= 2 else 1.0
    total_time = max(total_time, 1.0)

    click_freq = float(len(click_presses) / total_time)
    scroll_rate = float(len(scroll_events) / total_time)
    scroll_mags = [abs(e.get("dy", 0.0)) + abs(e.get("dx", 0.0)) for e in scroll_events]
    mean_scroll_mag = float(np.mean(scroll_mags)) if scroll_mags else 0.0

    return {
        "mean_speed": mean_speed,
        "std_speed": std_speed,
        "max_speed": max_speed,
        "median_speed": median_speed,
        "mean_acceleration": mean_acc,
        "std_acceleration": std_acc,
        "max_acceleration": max_acc,
        "path_curvature": path_curvature,
        "mean_click_duration": mean_click_dur,
        "std_click_duration": std_click_dur,
        "click_frequency": click_freq,
        "scroll_event_rate": scroll_rate,
        "mean_scroll_magnitude": mean_scroll_mag,
        "direction_change_rate": direction_change_rate,
        "mean_jerk": mean_jerk,
        "movement_entropy": movement_entropy
    }
