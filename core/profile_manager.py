import re
import json
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List

from .config import config

_SAFE_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_\-]{1,64}$")


def _sanitize_user_id(user_id: str) -> str:
    if not _SAFE_ID_PATTERN.match(user_id):
        raise ValueError(f"Invalid user_id: must be alphanumeric/underscore/hyphen, 1-64 chars")
    return user_id


class ProfileManager:
    def __init__(self, profiles_dir: Optional[Path] = None):
        self.profiles_dir = profiles_dir or config.paths.profiles_dir
        self.profiles_dir.mkdir(parents=True, exist_ok=True)

    def get_profile_path(self, user_id: str) -> Path:
        return self.profiles_dir / _sanitize_user_id(user_id)

    def exists(self, user_id: str) -> bool:
        return (self.get_profile_path(user_id) / "metadata.json").exists()

    def create_or_update_metadata(self, user_id: str, metadata: Dict[str, Any]):
        p = self.get_profile_path(user_id)
        p.mkdir(parents=True, exist_ok=True)
        meta_file = p / "metadata.json"
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

    def get_metadata(self, user_id: str) -> Dict[str, Any]:
        meta_file = self.get_profile_path(user_id) / "metadata.json"
        if not meta_file.exists():
            return {}
        with open(meta_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def list_profiles(self) -> List[str]:
        if not self.profiles_dir.exists():
            return []
        profiles = []
        for d in self.profiles_dir.iterdir():
            if d.is_dir() and _SAFE_ID_PATTERN.match(d.name):
                if (d / "metadata.json").exists() or (d / "keystroke_samples.csv").exists() or (d / "keystroke_model.joblib").exists():
                    profiles.append(d.name)
        return sorted(profiles)

    def delete_profile(self, user_id: str) -> bool:
        p = self.get_profile_path(user_id)
        if p.exists():
            shutil.rmtree(p, ignore_errors=True)
            return True
        return False

    def delete_all_profiles(self) -> int:
        count = 0
        if self.profiles_dir.exists():
            for d in list(self.profiles_dir.iterdir()):
                if d.is_dir():
                    shutil.rmtree(d, ignore_errors=True)
                    count += 1
        return count

    def ensure_default_profile(self, default_user_id: str = "user_001", auto_seed: bool = False) -> Path:
        p = self.get_profile_path(default_user_id)
        p.mkdir(parents=True, exist_ok=True)
        if auto_seed and not self.exists(default_user_id):
            try:
                from scripts.generate_synthetic_data import generate_and_seed_all
                generate_and_seed_all(n_samples=150, user_id=default_user_id)
            except Exception:
                pass
        return p
