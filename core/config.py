import os
import secrets
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class PathConfig:
    base_dir: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent)
    data_dir: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent / "data")
    raw_dir: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent / "data" / "raw")
    processed_dir: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent / "data" / "processed")
    profiles_dir: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent / "data" / "profiles")
    models_dir: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent / "models" / "saved")

    def __post_init__(self):
        for path in [self.data_dir, self.raw_dir, self.processed_dir, self.profiles_dir, self.models_dir]:
            path.mkdir(parents=True, exist_ok=True)


@dataclass
class CollectorConfig:
    sampling_rate_ms: int = 20
    keystroke_buffer_max_events: int = 5000
    mouse_buffer_max_events: int = 10000
    flush_interval_seconds: float = 10.0
    anonymize_keys: bool = True
    salt: str = field(default_factory=lambda: os.environ.get("DDNA_KEY_SALT", secrets.token_hex(16)))


@dataclass
class WindowConfig:
    window_duration_seconds: float = 30.0
    step_duration_seconds: float = 5.0
    min_keystrokes_per_window: int = 15
    min_mouse_events_per_window: int = 30
    min_training_windows: int = 30
    recommended_training_windows: int = 60


@dataclass
class ModelConfig:
    keystroke_algorithm: str = "ocsvm"
    mouse_algorithm: str = "isolation_forest"
    contamination: float = 0.05
    ocsvm_nu: float = 0.05
    ocsvm_gamma: str = "scale"
    n_estimators: int = 150
    random_state: int = 42


@dataclass
class FusionConfig:
    keystroke_weight: float = 0.50
    mouse_weight: float = 0.40
    app_usage_weight: float = 0.10
    ema_alpha: float = 0.35
    threshold_allow: float = 75.0
    threshold_warn: float = 50.0
    consecutive_violations_lock: int = 3


@dataclass
class AppConfig:
    paths: PathConfig = field(default_factory=PathConfig)
    collector: CollectorConfig = field(default_factory=CollectorConfig)
    window: WindowConfig = field(default_factory=WindowConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    fusion: FusionConfig = field(default_factory=FusionConfig)


config = AppConfig()
