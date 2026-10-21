"""
Digital DNA Headless Daemon Runner.
Runs continuous behavioral biometrics authentication in the background without a GUI.
"""

import sys
import time
import signal
import argparse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from core.profile_manager import ProfileManager
from core.auth_engine import ContinuousAuthEngine
from core.config import config

class DigitalDNADaemon:
    def __init__(self, user_id: str = "user_001", auto_lock: bool = False, step_interval: float = 5.0):
        self.user_id = user_id
        self.auto_lock = auto_lock
        self.step_interval = step_interval
        self._running = False

        self.profile_manager = ProfileManager()
        self.profile_manager.ensure_default_profile(self.user_id)

        self.auth_engine = ContinuousAuthEngine(
            user_id=self.user_id,
            profile_manager=self.profile_manager,
            on_tick=self._on_tick,
            on_decision=self._on_decision,
            auto_lock_system=self.auto_lock
        )

    def _on_tick(self, result: dict):
        t_str = time.strftime("%Y-%m-%d %H:%M:%S")
        is_idle = result.get("is_idle", False)
        score = result["trust_score"]
        decision = result["decision"]
        k_s = result["modality_scores"]["keystroke"]
        m_s = result["modality_scores"]["mouse"]

        if is_idle:
            status = f"[{t_str}] IDLE | Trust Score: {score:.1f} ({decision})"
        else:
            k_disp = f"{k_s:.2f}" if k_s is not None else "--"
            m_disp = f"{m_s:.2f}" if m_s is not None else "--"
            status = f"[{t_str}] ACTIVE | Key: {k_disp}, Mouse: {m_disp} | Trust Score: {score:.1f} ({decision})"

        print(status, flush=True)

    def _on_decision(self, result: dict):
        decision = result["decision"]
        if decision in {"WARN", "LOCK"}:
            print(f"[SECURITY ALERT] Consecutive violations: {result['consecutive_violations']} -> Triggered {decision}!", flush=True)

    def start(self):
        self._running = True
        print(f"=== Digital DNA Continuous Authentication Daemon ===")
        print(f"User Profile: {self.user_id}")
        print(f"Auto-Lock System: {self.auto_lock}")
        print(f"Evaluation Window Step: {self.step_interval}s")
        print(f"Press Ctrl+C to gracefully stop.\n", flush=True)

        self.auth_engine.start()

        def _handle_exit(sig, frame):
            print("\nShutting down Digital DNA daemon...", flush=True)
            self.stop()
            sys.exit(0)

        signal.signal(signal.SIGINT, _handle_exit)
        signal.signal(signal.SIGTERM, _handle_exit)

        while self._running:
            time.sleep(1.0)

    def stop(self):
        self._running = False
        self.auth_engine.stop()

def main():
    parser = argparse.ArgumentParser(description="Digital DNA Continuous Authentication Daemon")
    parser.add_argument("--user", default="user_001", help="User profile ID to monitor")
    parser.add_argument("--auto-lock", action="store_true", help="Automatically lock workstation when impostor is detected")
    parser.add_argument("--step", type=float, default=5.0, help="Window evaluation step in seconds")
    args = parser.parse_args()

    daemon = DigitalDNADaemon(
        user_id=args.user,
        auto_lock=args.auto_lock,
        step_interval=args.step
    )
    daemon.start()

if __name__ == "__main__":
    main()
