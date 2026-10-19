import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from .config import config

class ProfileManager:
    def __init__(self, profiles_dir: Optional[Path] = None):
        self.profiles_dir = profiles_dir or config.paths.profiles_dir
        self.profiles_dir.mkdir(parents=True, exist_ok=True)

    def get_profile_path(self, user_id: str) -> Path:
        return self.profiles_dir / user_id

    def exists(self, user_id: str) -> bool:
        p = self.get_profile_path(user_id)
        return (p / "metadata.json").exists()

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
        return [d.name for d in self.profiles_dir.iterdir() if d.is_dir() and (d / "metadata.json").exists()]
