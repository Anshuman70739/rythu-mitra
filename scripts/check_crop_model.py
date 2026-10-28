#!/usr/bin/env python3
"""Load the trusted crop model and run a deterministic smoke inference.

Only run this against the project-maintained model artifact. Pickle files can
execute code during deserialization and must never be accepted from untrusted sources.
This check proves basic load/inference compatibility, not agronomic accuracy.
"""
from __future__ import annotations

import hashlib
import pickle
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FEATURES = [90.0, 42.0, 43.0, 20.8, 82.0, 6.5, 202.9]


def main() -> int:
    model_dir = Path(__import__("os").environ.get("MODEL_DIR", str(ROOT / "models"))).expanduser().resolve()
    candidates = (model_dir / "crop_model.pkl", ROOT / "crop_model.pkl")
    path = next((candidate for candidate in candidates if candidate.is_file()), None)
    if path is None:
        print("BLOCKED: crop_model.pkl is missing from the configured model directory and project root.")
        return 1

    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    # Security: this is a trusted project artifact, not an uploaded/user-supplied pickle.
    with path.open("rb") as stream:
        model = pickle.load(stream)

    expected = getattr(model, "n_features_in_", None)
    if expected is not None and int(expected) != len(FEATURES):
        print(f"FAIL: expected 7 crop features but model declares {expected}.")
        return 1

    prediction = model.predict(np.asarray([FEATURES], dtype=float))
    if len(prediction) != 1:
        print(f"FAIL: expected one prediction, got {len(prediction)}.")
        return 1

    label = str(prediction[0]).strip()
    if not label:
        print("FAIL: model returned an empty crop label.")
        return 1

    classes = getattr(model, "classes_", None)
    if classes is not None and label not in {str(value) for value in classes}:
        print("FAIL: prediction is not in the model's declared classes.")
        return 1

    print(f"PASS: crop model loaded and returned one class for 7 ordered features: {label}")
    print(f"Artifact SHA-256: {digest}")
    print("LIMITATION: this smoke check does not establish dataset provenance, accuracy, calibration, or field suitability.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
