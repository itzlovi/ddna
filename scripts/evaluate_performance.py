import sys
import argparse
from pathlib import Path

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import numpy as np
import pandas as pd
from scipy.optimize import brentq
from scipy.interpolate import interp1d
from sklearn.metrics import roc_curve
from models.model_utils import load_model

def compute_eer(y_true: np.ndarray, y_scores: np.ndarray):
    fpr, tpr, thresholds = roc_curve(y_true, y_scores, pos_label=1)
    fnr = 1.0 - tpr
    eer = brentq(lambda x: 1.0 - x - interp1d(fpr, tpr)(x), 0.0, 1.0)
    thresh = interp1d(fpr, thresholds)(eer)
    return float(eer), float(thresh), fpr, fnr, thresholds

def evaluate_model(model, genuine_features: np.ndarray, impostor_features: np.ndarray):
    gen_scores = [model.score(x) for x in genuine_features]
    imp_scores = [model.score(x) for x in impostor_features]

    y_true = np.array([1] * len(gen_scores) + [0] * len(imp_scores))
    y_scores = np.array(gen_scores + imp_scores)

    eer, thresh, fpr, fnr, thresholds = compute_eer(y_true, y_scores)
    return {
        "EER": eer,
        "optimal_threshold": thresh,
        "mean_genuine_score": float(np.mean(gen_scores)),
        "mean_impostor_score": float(np.mean(imp_scores)),
        "genuine_count": len(gen_scores),
        "impostor_count": len(imp_scores)
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--genuine", required=True)
    parser.add_argument("--impostor", required=True)
    args = parser.parse_args()

    gen_df = pd.read_csv(args.genuine).drop(columns=["label"], errors="ignore")
    imp_df = pd.read_csv(args.impostor).drop(columns=["label"], errors="ignore")

    model = load_model(args.model)
    res = evaluate_model(model, gen_df.values, imp_df.values)
    import json
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
