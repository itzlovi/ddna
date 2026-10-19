import argparse
import numpy as np
import pandas as pd
from scipy.optimize import brentq
from scipy.interpolate import interp1d
from sklearn.metrics import roc_curve
from models.keystroke_model import KeystrokeModel
from models.mouse_model import MouseModel

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
        "mean_impostor_score": float(np.mean(imp_scores))
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--genuine", required=True)
    parser.add_argument("--impostor", required=True)
    args = parser.parse_args()

    gen_df = pd.read_csv(args.genuine)
    imp_df = pd.read_csv(args.impostor)

    model = KeystrokeModel.load(args.model)
    res = evaluate_model(model, gen_df.values, imp_df.values)
    print(res)

if __name__ == "__main__":
    main()
