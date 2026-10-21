import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd
from models.keystroke_model import KeystrokeModel
from models.mouse_model import MouseModel
from fusion.score_fusion import ScoreFusion
from fusion.trust_score import TrustScoreEngine
from fusion.decision_engine import DecisionEngine
from scripts.generate_synthetic_data import generate_keystroke_samples, generate_mouse_samples

def run_test():
    km = KeystrokeModel.load("data/profiles/Lovepreet/keystroke_model.joblib")
    mm = MouseModel.load("data/profiles/Lovepreet/mouse_model.joblib")

    print(f"Loaded Lovepreet models:")
    print(f"  Keystroke calibration: mean={km.train_mean:.4f}, std={km.train_std:.4f}")
    print(f"  Mouse calibration:     mean={mm.train_mean:.4f}, std={mm.train_std:.4f}")

    k_df = pd.read_csv("data/profiles/Lovepreet/keystroke_samples.csv")
    m_df = pd.read_csv("data/profiles/Lovepreet/mouse_samples.csv")

    fusion = ScoreFusion()
    trust = TrustScoreEngine()
    decision = DecisionEngine()

    print("\n--- Testing Genuine User Streaming (20 windows) ---")
    decisions = []
    trust_scores = []
    for i in range(20):
        k_s = km.score(k_df.values[i])
        m_s = mm.score(m_df.values[i])
        fused = fusion.fuse({"keystroke": k_s, "mouse": m_s})
        t_score = trust.update(fused)
        d_info = decision.evaluate(t_score)
        decisions.append(d_info["decision"])
        trust_scores.append(t_score)
        if i % 5 == 0 or i == 19:
            print(f"  Window {i+1:2d}: Key={k_s:.3f}, Mouse={m_s:.3f} | Fused={fused:.3f} | Trust={t_score:.1f} -> {d_info['decision']}")

    print(f"Genuine final trust: {trust_scores[-1]:.1f}, Decisions: {dict(pd.Series(decisions).value_counts())}")

    print("\n--- Testing Impostor Stealing Session (10 windows) ---")
    np.random.seed(123)
    k_imp = generate_keystroke_samples(20, is_genuine=False)
    m_imp = generate_mouse_samples(20, is_genuine=False)

    imp_decisions = []
    imp_trust_scores = []
    for i in range(10):
        k_s = km.score(k_imp.values[i])
        m_s = mm.score(m_imp.values[i])
        fused = fusion.fuse({"keystroke": k_s, "mouse": m_s})
        t_score = trust.update(fused)
        d_info = decision.evaluate(t_score)
        imp_decisions.append(d_info["decision"])
        imp_trust_scores.append(t_score)
        print(f"  Impostor Window {i+1:2d}: Key={k_s:.3f}, Mouse={m_s:.3f} | Fused={fused:.3f} | Trust={t_score:.1f} -> {d_info['decision']}")

    print(f"\nFinal outcome:")
    print(f"  Impostor locked out? {'YES (LOCK triggered)' if 'LOCK' in imp_decisions else 'NO'}")
    assert "LOCK" in imp_decisions, "Impostor was not locked!"
    assert decisions[-1] == "ALLOW", "Genuine user did not reach ALLOW state!"
    print("\nALL PHASE 1 CRITERIA PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_test()
