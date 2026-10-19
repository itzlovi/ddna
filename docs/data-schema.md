# Digital DNA Data Schema

## 1. Raw Window Event Schema

```json
{
  "user_id": "user_001",
  "session_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "timestamp": 1729312000.123,
  "raw_events": {
    "keystroke": [
      {
        "type": "press",
        "key_id": "KEY_a81f3b01",
        "timestamp": 1729312000.150,
        "flight_time": 0.125,
        "is_error_key": false
      },
      {
        "type": "release",
        "key_id": "KEY_a81f3b01",
        "timestamp": 1729312000.245,
        "dwell_time": 0.095,
        "is_error_key": false
      }
    ],
    "mouse": [
      {
        "type": "move",
        "x": 450,
        "y": 320,
        "timestamp": 1729312000.180,
        "dx": 12.0,
        "dy": -8.0,
        "distance": 14.42,
        "dt": 0.015,
        "speed": 961.47,
        "acceleration": 210.3
      },
      {
        "type": "click_release",
        "x": 450,
        "y": 320,
        "button": "left",
        "timestamp": 1729312000.310,
        "duration": 0.082
      }
    ]
  }
}
```

## 2. Feature Vectors

### Keystroke Features
- `mean_dwell_time`, `std_dwell_time`, `median_dwell_time`, `iqr_dwell_time`
- `mean_flight_time`, `std_flight_time`, `median_flight_time`, `iqr_flight_time`
- `mean_digraph_time`, `std_digraph_time`, `mean_trigraph_time`, `std_trigraph_time`
- `rhythm_consistency`, `error_rate`, `words_per_minute`
- `pause_rate_500ms`, `pause_rate_1000ms`, `max_pause_duration`, `pause_ratio`

### Mouse Features
- `mean_speed`, `std_speed`, `max_speed`, `median_speed`
- `mean_acceleration`, `std_acceleration`, `max_acceleration`
- `path_curvature`, `mean_click_duration`, `std_click_duration`, `click_frequency`
- `scroll_event_rate`, `mean_scroll_magnitude`, `direction_change_rate`, `mean_jerk`, `movement_entropy`
