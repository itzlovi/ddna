import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.profile_manager import ProfileManager
from core.enrollment import EnrollmentManager

pm = ProfileManager()
for uid in ["Lovepreet", "user_001"]:
    em = EnrollmentManager(uid, pm)
    loaded = em.load_samples()
    print(f"Profile: {uid}, loaded={loaded}, keys={len(em.keystroke_samples)}, mouse={len(em.mouse_samples)}")
    if loaded and len(em.keystroke_samples) > 0:
        meta = em.train_and_save()
        print(f"  Successfully re-fitted and saved! Calibration: {meta.get('calibration')}")
