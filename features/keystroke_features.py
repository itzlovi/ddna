import numpy as np
from typing import List, Dict, Any

KEYSTROKE_FEATURE_NAMES = [
    "mean_dwell_time",
    "std_dwell_time",
    "median_dwell_time",
    "iqr_dwell_time",
    "mean_flight_time",
    "std_flight_time",
    "median_flight_time",
    "iqr_flight_time",
    "mean_digraph_time",
    "std_digraph_time",
    "mean_trigraph_time",
    "std_trigraph_time",
    "rhythm_consistency",
    "error_rate",
    "words_per_minute",
    "pause_rate_500ms",
    "pause_rate_1000ms",
    "max_pause_duration",
    "pause_ratio"
]

def extract_keystroke_features(raw_events: List[Dict[str, Any]]) -> Dict[str, float]:
    if not raw_events:
        return {name: 0.0 for name in KEYSTROKE_FEATURE_NAMES}

    dwell_times = [e["dwell_time"] for e in raw_events if e.get("type") == "release" and "dwell_time" in e]
    flight_times = [e["flight_time"] for e in raw_events if e.get("type") == "press" and "flight_time" in e and e["flight_time"] > 0.0]
    press_timestamps = sorted([e["timestamp"] for e in raw_events if e.get("type") == "press"])
    total_presses = len(press_timestamps)
    error_presses = sum(1 for e in raw_events if e.get("type") == "press" and e.get("is_error_key", False))

    mean_dwell = float(np.mean(dwell_times)) if dwell_times else 0.0
    std_dwell = float(np.std(dwell_times)) if len(dwell_times) > 1 else 0.0
    median_dwell = float(np.median(dwell_times)) if dwell_times else 0.0
    iqr_dwell = float(np.percentile(dwell_times, 75) - np.percentile(dwell_times, 25)) if len(dwell_times) >= 4 else 0.0

    mean_flight = float(np.mean(flight_times)) if flight_times else 0.0
    std_flight = float(np.std(flight_times)) if len(flight_times) > 1 else 0.0
    median_flight = float(np.median(flight_times)) if flight_times else 0.0
    iqr_flight = float(np.percentile(flight_times, 75) - np.percentile(flight_times, 25)) if len(flight_times) >= 4 else 0.0

    digraph_times = []
    if len(press_timestamps) >= 2:
        digraph_times = [press_timestamps[i] - press_timestamps[i - 1] for i in range(1, len(press_timestamps))]
    mean_digraph = float(np.mean(digraph_times)) if digraph_times else 0.0
    std_digraph = float(np.std(digraph_times)) if len(digraph_times) > 1 else 0.0

    trigraph_times = []
    if len(press_timestamps) >= 3:
        trigraph_times = [press_timestamps[i] - press_timestamps[i - 2] for i in range(2, len(press_timestamps))]
    mean_trigraph = float(np.mean(trigraph_times)) if trigraph_times else 0.0
    std_trigraph = float(np.std(trigraph_times)) if len(trigraph_times) > 1 else 0.0

    rhythm_consistency = float(std_flight / (mean_flight + 1e-6)) if flight_times else 0.0
    error_rate = float(error_presses / total_presses) if total_presses > 0 else 0.0

    wpm = 0.0
    pause_rate_500ms = 0.0
    pause_rate_1000ms = 0.0
    max_pause_duration = 0.0
    pause_ratio = 0.0

    if len(press_timestamps) >= 2:
        total_time_sec = press_timestamps[-1] - press_timestamps[0]
        if total_time_sec > 0:
            wpm = float((total_presses / 5.0) / (total_time_sec / 60.0))
        pauses_500 = [dt for dt in digraph_times if dt >= 0.5]
        pauses_1000 = [dt for dt in digraph_times if dt >= 1.0]
        pause_rate_500ms = float(len(pauses_500) / len(digraph_times)) if digraph_times else 0.0
        pause_rate_1000ms = float(len(pauses_1000) / len(digraph_times)) if digraph_times else 0.0
        max_pause_duration = float(max(digraph_times)) if digraph_times else 0.0
        total_pause_time = float(sum(pauses_500))
        pause_ratio = float(total_pause_time / (total_time_sec + 1e-6)) if total_time_sec > 0 else 0.0

    return {
        "mean_dwell_time": mean_dwell,
        "std_dwell_time": std_dwell,
        "median_dwell_time": median_dwell,
        "iqr_dwell_time": iqr_dwell,
        "mean_flight_time": mean_flight,
        "std_flight_time": std_flight,
        "median_flight_time": median_flight,
        "iqr_flight_time": iqr_flight,
        "mean_digraph_time": mean_digraph,
        "std_digraph_time": std_digraph,
        "mean_trigraph_time": mean_trigraph,
        "std_trigraph_time": std_trigraph,
        "rhythm_consistency": rhythm_consistency,
        "error_rate": error_rate,
        "words_per_minute": wpm,
        "pause_rate_500ms": pause_rate_500ms,
        "pause_rate_1000ms": pause_rate_1000ms,
        "max_pause_duration": max_pause_duration,
        "pause_ratio": pause_ratio
    }
