import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.drift_detector import ConceptDriftDetector
from core.continuous_learner import ContinuousLearner
from core.profile_manager import ProfileManager
from scripts.generate_synthetic_data import generate_keystroke_samples, generate_mouse_samples

def test_phase4():
    print("--- 1. Testing ConceptDriftDetector ---")
    detector = ConceptDriftDetector(window_size=30, drift_threshold=0.10)

    # 1. Feed stable scores
    for _ in range(25):
        res = detector.add_score(0.85)
    print(f"  Stable status: {res['status']} (drift={res['drift_detected']})")
    assert res["status"] == "STABLE", "Expected STABLE status!"

    # 2. Feed gradual drift
    for _ in range(20):
        res = detector.add_score(0.68)
    print(f"  Drift status: {res['status']} (drift_magnitude={res['drift_magnitude']}, detected={res['drift_detected']})")
    assert res["drift_detected"], "Concept drift was not detected!"

    print("\n--- 2. Testing ContinuousLearner Background Retraining ---")
    pm = ProfileManager()
    test_user = "test_continuous_user"
    pm.ensure_default_profile(test_user)

    # Seed initial training data
    k_gen = generate_keystroke_samples(25, is_genuine=True)
    m_gen = generate_mouse_samples(25, is_genuine=True)
    p_dir = pm.get_profile_path(test_user)
    k_gen.to_csv(p_dir / "keystroke_samples.csv", index=False)
    m_gen.to_csv(p_dir / "mouse_samples.csv", index=False)

    update_received = []

    def on_update(info):
        update_received.append(info)
        print(f"  [CALLBACK] Continuous learner updated model to version v{info['version']}!")

    learner = ContinuousLearner(
        user_id=test_user,
        profile_manager=pm,
        retrain_threshold=5,  # Trigger quickly for test
        min_trust_to_accumulate=75.0,
        on_model_updated=on_update
    )

    # Test rejection of impostor / low trust windows
    bad_res = learner.process_authenticated_window(
        features={"keystroke": {}, "mouse": {}},
        trust_score=30.0,
        decision="LOCK",
        fused_similarity=0.10
    )
    assert not bad_res["accumulated"], "Bad window was erroneously accumulated!"
    print("  Rejected low-trust / LOCK window from genuine store: PASS")

    # Feed 6 high-confidence genuine windows
    print("  Feeding 6 confirmed genuine windows to trigger background retrain...")
    for i in range(6):
        sample_k = k_gen.iloc[i].to_dict()
        sample_m = m_gen.iloc[i].to_dict()
        learner.process_authenticated_window(
            features={"keystroke": sample_k, "mouse": sample_m},
            trust_score=85.0,
            decision="ALLOW",
            fused_similarity=0.85
        )

    # Wait for background thread worker
    for _ in range(50):
        if update_received:
            break
        time.sleep(0.2)

    assert len(update_received) > 0, "Continuous retrain was not triggered!"
    print(f"  Background retrain complete! Total retrains: {learner.total_retrains}")
    assert (p_dir / "v2").exists(), "Versioned profile directory v2 was not created!"
    print("  Versioned snapshot created at v2: PASS")

    # Clean up test user
    pm.delete_profile(test_user)
    print("\nALL PHASE 4 CONTINUOUS LEARNING CRITERIA PASSED!")

if __name__ == "__main__":
    test_phase4()
