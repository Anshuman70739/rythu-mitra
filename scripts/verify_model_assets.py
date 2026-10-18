#!/usr/bin/env python3
"""Verify server-side model files and labels without copying weights into the frontend.

By default this script only checks files and label structure. If TensorFlow is installed,
pass --load-disease to load the H5 model and compare its output dimension with labels.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def find_asset(filename: str, model_dir: Path) -> Path | None:
    candidates = (model_dir / filename, ROOT / filename)
    return next((p for p in candidates if p.is_file()), None)


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--load-disease", action="store_true", help="Load H5 using TensorFlow and verify output count")
    args = parser.parse_args()
    model_dir = Path(os.getenv("MODEL_DIR", str(ROOT / "models"))).expanduser().resolve()
    labels_candidates = (model_dir / "disease_labels.json", ROOT / "data" / "disease_labels.json")
    print(f"Model directory: {model_dir}")
    failures = 0
    for filename in ("crop_model.pkl", "plant_disease_model.h5"):
        path = find_asset(filename, model_dir)
        if path is None:
            print(f"MISSING: {filename}")
            failures += 1
        else:
            print(f"FOUND: {filename} ({path.stat().st_size:,} bytes; sha256={digest(path)})")
    label_path = next((p for p in labels_candidates if p.is_file()), None)
    labels = None
    if label_path is None:
        print("MISSING: data/disease_labels.json or models/disease_labels.json")
        failures += 1
    else:
        try:
            labels = json.loads(label_path.read_text(encoding="utf-8"))
            if not isinstance(labels, list) or not labels or any(not isinstance(x, str) or not x.strip() for x in labels):
                raise ValueError("expected a non-empty JSON list of class-name strings")
            try:
                display_label_path = label_path.relative_to(ROOT)
            except ValueError:
                display_label_path = label_path
            print(f"FOUND: {display_label_path} ({len(labels)} labels; JSON structure valid)")
        except (OSError, ValueError, TypeError) as exc:
            print(f"INVALID: disease labels file ({type(exc).__name__}: {exc})")
            failures += 1
    if args.load_disease:
        model_path = find_asset("plant_disease_model.h5", model_dir)
        if not model_path or labels is None:
            print("BLOCKED: cannot load model until weights and valid labels are present")
            failures += 1
        else:
            try:
                from tensorflow.keras.models import load_model
                model = load_model(model_path, compile=False)
                output_shape = model.output_shape
                if isinstance(output_shape, list) or not output_shape or not isinstance(output_shape[-1], int):
                    raise ValueError(f"unexpected output shape: {output_shape}")
                print(f"Disease model input_shape={model.input_shape}; output_shape={output_shape}")
                if output_shape[-1] != len(labels):
                    raise ValueError(f"model outputs {output_shape[-1]} classes but labels has {len(labels)}")
                print("PASS: model output dimension matches label count. Label order/preprocessing still requires provenance verification.")
            except Exception as exc:
                print(f"FAIL: disease model load/shape check ({type(exc).__name__}: {exc})")
                failures += 1
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
