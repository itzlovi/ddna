import json
import re
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

_SAFE_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_\-]{1,64}$")


def _sanitize_id(identifier: str) -> str:
    if not _SAFE_ID_PATTERN.match(identifier):
        raise ValueError(f"Invalid identifier '{identifier}': must be alphanumeric/underscore/hyphen, 1-64 chars")
    return identifier


class RawEventStore:
    def __init__(self, profile_dir: Path, session_id: str):
        self.sessions_dir = profile_dir / "sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.session_id = _sanitize_id(session_id)
        self.session_file = self.sessions_dir / f"{self.session_id}.jsonl"

    def append(self, window_data: Dict[str, Any]):
        if not isinstance(window_data, dict):
            return

        ts = window_data.get("timestamp")
        if not isinstance(ts, (int, float)) or ts <= 0:
            ts = time.time()

        raw_events = window_data.get("raw_events")
        if not isinstance(raw_events, dict):
            raw_events = {}

        record = {
            "timestamp": float(ts),
            "raw_events": raw_events,
        }
        with open(self.session_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

    def load_session(self, session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sid = _sanitize_id(session_id) if session_id else self.session_id
        target = self.sessions_dir / f"{sid}.jsonl"
        if not target.exists():
            return []
        records = []
        with open(target, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        data = json.loads(line)
                        if isinstance(data, dict) and "timestamp" in data and "raw_events" in data:
                            records.append(data)
                    except json.JSONDecodeError:
                        continue
        return records

    def list_sessions(self) -> List[str]:
        if not self.sessions_dir.exists():
            return []
        return sorted([
            f.stem for f in self.sessions_dir.iterdir()
            if f.is_file() and f.suffix == ".jsonl" and _SAFE_ID_PATTERN.match(f.stem)
        ])

    def load_all_sessions(self) -> List[Dict[str, Any]]:
        all_records = []
        for sid in self.list_sessions():
            all_records.extend(self.load_session(sid))
        return sorted(all_records, key=lambda r: r.get("timestamp", 0))

    def get_total_window_count(self) -> int:
        count = 0
        for sid in self.list_sessions():
            fpath = self.sessions_dir / f"{sid}.jsonl"
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    count += sum(1 for line in f if line.strip())
            except OSError:
                continue
        return count
