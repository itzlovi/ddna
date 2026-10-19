import os
import tempfile
import numpy as np
import pytest
from models.keystroke_model import KeystrokeModel
from models.mouse_model import MouseModel
from models.motion_model import MotionModel
from models.touch_model import TouchModel

def test_keystroke_model():
    X = np.random.normal(loc=0.15, scale=0.03, size=(25, 19))
    model = KeystrokeModel()
    assert model.score(X[0]) == 0.5
    model.fit(X)
    assert model.is_fitted is True
    score = model.score(X[0])
    assert 0.0 <= score <= 1.0
    preds = model.predict(X[:3])
    assert len(preds) == 3

def test_mouse_model():
    X = np.random.normal(loc=500.0, scale=50.0, size=(25, 16))
    model = MouseModel()
    assert model.score(X[0]) == 0.5
    model.fit(X)
    assert model.is_fitted is True
    score = model.score(X[0])
    assert 0.0 <= score <= 1.0

def test_save_and_load_model():
    X = np.random.normal(loc=0.15, scale=0.03, size=(20, 19))
    model = KeystrokeModel().fit(X)
    with tempfile.NamedTemporaryFile(suffix=".joblib", delete=False) as tmp:
        path = tmp.name
    try:
        model.save(path)
        loaded = KeystrokeModel.load(path)
        assert loaded.is_fitted is True
        s1 = model.score(X[0])
        s2 = loaded.score(X[0])
        assert abs(s1 - s2) < 1e-4
    finally:
        if os.path.exists(path):
            os.remove(path)
