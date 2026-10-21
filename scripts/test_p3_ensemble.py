import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd
from models.ensemble_scorer import BiometricEnsemble
from scripts.generate_synthetic_data import generate_keystroke_samples, generate_mouse_samples

def test_phase3():
    print("--- 1. Testing Tri-Model BiometricEnsemble Training ---")
    np.random.seed(42)
    k_gen = generate_keystroke_samples(100, is_genuine=True)
    m_gen = generate_mouse_samples(100, is_genuine=True)

    k_imp = generate_keystroke_samples(50, is_genuine=False)
    m_imp = generate_mouse_samples(50, is_genuine=False)

    t0 = time.time()
    k_ens = BiometricEnsemble(modality="keystroke").fit(k_gen.values)
    m_ens = BiometricEnsemble(modality="mouse").fit(m_gen.values)
    t_train = time.time() - t0
    print(f"  Ensembles fitted in {t_train:.2f}s!")

    print("\n--- 2. Evaluating Detailed Predictions on Genuine Sample ---")
    k_det_gen = k_ens.detailed_score(k_gen.values[0])
    m_det_gen = m_ens.detailed_score(m_gen.values[0])
    print(f"  Genuine Keystroke: Fused={k_det_gen['fused']:.3f} | Primary={k_det_gen['primary']:.3f}, Mahal={k_det_gen['mahalanobis']:.3f}, AE={k_det_gen['autoencoder']:.3f}")
    print(f"  Genuine Mouse:     Fused={m_det_gen['fused']:.3f} | Primary={m_det_gen['primary']:.3f}, Mahal={m_det_gen['mahalanobis']:.3f}, AE={m_det_gen['autoencoder']:.3f}")

    assert k_det_gen["fused"] >= 0.70, "Genuine keystroke score too low!"
    assert m_det_gen["fused"] >= 0.70, "Genuine mouse score too low!"

    print("\n--- 3. Evaluating Detailed Predictions on Impostor Sample ---")
    k_det_imp = k_ens.detailed_score(k_imp.values[0])
    m_det_imp = m_ens.detailed_score(m_imp.values[0])
    print(f"  Impostor Keystroke: Fused={k_det_imp['fused']:.3f} | Primary={k_det_imp['primary']:.3f}, Mahal={k_det_imp['mahalanobis']:.3f}, AE={k_det_imp['autoencoder']:.3f}")
    print(f"  Impostor Mouse:     Fused={m_det_imp['fused']:.3f} | Primary={m_det_imp['primary']:.3f}, Mahal={m_det_imp['mahalanobis']:.3f}, AE={m_det_imp['autoencoder']:.3f}")

    assert k_det_imp["fused"] <= 0.25, "Impostor keystroke score too high!"
    assert m_det_imp["fused"] <= 0.25, "Impostor mouse score too high!"

    print("\n--- 4. Full Dataset Metrics (100 Genuine vs 50 Impostors) ---")
    k_gen_scores = [k_ens.score(x) for x in k_gen.values]
    k_imp_scores = [k_ens.score(x) for x in k_imp.values]

    m_gen_scores = [m_ens.score(x) for x in m_gen.values]
    m_imp_scores = [m_ens.score(x) for x in m_imp.values]

    print(f"  Keystroke Genuine  mean={np.mean(k_gen_scores):.3f}, min={np.min(k_gen_scores):.3f}")
    print(f"  Keystroke Impostor mean={np.mean(k_imp_scores):.3f}, max={np.max(k_imp_scores):.3f}")
    print(f"  Mouse Genuine      mean={np.mean(m_gen_scores):.3f}, min={np.min(m_gen_scores):.3f}")
    print(f"  Mouse Impostor     mean={np.mean(m_imp_scores):.3f}, max={np.max(m_imp_scores):.3f}")

    # Verify separation margin
    assert np.min(k_gen_scores) > np.max(k_imp_scores), "Keystroke overlap detected!"
    assert np.median(m_gen_scores) > 0.80 and np.mean(m_imp_scores) < 0.10, "Mouse separation insufficient!"

    print("\nALL PHASE 3 TRI-MODEL ENSEMBLE CRITERIA PASSED!")

if __name__ == "__main__":
    test_phase3()
