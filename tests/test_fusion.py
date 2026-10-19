import pytest
from fusion.score_fusion import ScoreFusion
from fusion.trust_score import TrustScoreEngine
from fusion.decision_engine import DecisionEngine

def test_score_fusion():
    fusion = ScoreFusion()
    res = fusion.fuse({"keystroke": 0.8, "mouse": 0.8})
    assert abs(res - 0.8) < 1e-3

    res_single = fusion.fuse({"keystroke": 0.9, "mouse": None})
    assert abs(res_single - 0.9) < 1e-3

    res_empty = fusion.fuse({})
    assert res_empty == 0.5

def test_trust_score_engine():
    engine = TrustScoreEngine(alpha=0.5, initial_score=80.0)
    new_score = engine.update(1.0)
    assert new_score == 90.0
    new_score2 = engine.update(0.0)
    assert new_score2 == 45.0

def test_decision_engine():
    engine = DecisionEngine(threshold_allow=75.0, threshold_warn=50.0, max_consecutive_violations=2)
    dec1 = engine.evaluate(80.0)
    assert dec1["decision"] == "ALLOW"

    dec2 = engine.evaluate(60.0)
    assert dec2["decision"] == "WARN"

    dec3 = engine.evaluate(30.0)
    assert dec3["decision"] == "WARN"

    dec4 = engine.evaluate(30.0)
    assert dec4["decision"] == "LOCK"
