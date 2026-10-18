"""Lazy-loaded ML adapters with label/version checks and explicit unavailable states."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from typing import Any
import numpy as np
from flask import current_app

_CROP_MODEL = None
_CROP_MODEL_PATH: str | None = None
_DISEASE_MODEL = None
_DISEASE_MODEL_PATH: str | None = None


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()[:16]



def has_model_asset(filename: str) -> bool:
    """Report whether an expected model asset exists in the configured or legacy location."""
    model_dir = Path(current_app.config["MODEL_DIR"])
    return (model_dir / filename).is_file() or (Path(current_app.root_path).parent / filename).is_file()

def has_disease_model_bundle() -> bool:
    """The weights alone are not usable labels; both the model and its label map are required."""
    model_dir = Path(current_app.config["MODEL_DIR"])
    project_root = Path(current_app.root_path).parent
    label_candidates = (model_dir / "disease_labels.json", project_root / "data" / "disease_labels.json")
    if not has_model_asset("plant_disease_model.h5") or not any(p.is_file() for p in label_candidates):
        return False
    try:
        labels = json.loads(next(p for p in label_candidates if p.is_file()).read_text(encoding="utf-8"))
        return isinstance(labels, list) and bool(labels) and all(isinstance(label, str) and label.strip() for label in labels)
    except (OSError, ValueError, TypeError):
        return False

def crop_model():
    global _CROP_MODEL, _CROP_MODEL_PATH
    model_dir = Path(current_app.config["MODEL_DIR"])
    path = model_dir / "crop_model.pkl"
    if not path.is_file():
        legacy_path = Path(current_app.root_path).parent / "crop_model.pkl"
        if legacy_path.is_file(): path = legacy_path
    if not path.is_file():
        raise FileNotFoundError("crop_model.pkl is not installed")
    if _CROP_MODEL is None or _CROP_MODEL_PATH != str(path):
        # Security: pickle can execute code at load time. Only load the trusted model
        # artifact supplied and checked by the project maintainers.
        import pickle
        with path.open("rb") as handle:
            _CROP_MODEL = pickle.load(handle)
        _CROP_MODEL_PATH = str(path)
    return _CROP_MODEL, _hash_file(path)


def predict_crop(features: list[float]) -> dict:
    try:
        model, version = crop_model()
        expected = getattr(model, "n_features_in_", len(features))
        if int(expected) != len(features):
            return {"success": False, "status": "UNAVAILABLE", "data_type": "UNAVAILABLE", "error": "Crop model input feature count does not match the supplied form."}
        crop = str(model.predict(np.asarray([features], dtype=float))[0])
        confidence = None
        if hasattr(model, "predict_proba"):
            try:
                probs = np.asarray(model.predict_proba(np.asarray([features], dtype=float))[0], dtype=float)
                if probs.size and np.all(np.isfinite(probs)) and np.all(probs >= 0) and np.all(probs <= 1) and abs(float(probs.sum()) - 1.0) < 0.02:
                    confidence = round(float(probs.max()) * 100, 1)
            except Exception:
                confidence = None
        return {"success": True, "status": "MODEL_OUTPUT", "data_type": "MODEL_OUTPUT", "crop": crop,
                "model_version": version, "model_confidence": confidence,
                "confidence_note": "Confidence is shown only when the model returns a valid probability distribution; it may not be calibrated for field outcomes." if confidence is not None else "The model does not provide a validated confidence estimate.",
                "feature_order": ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]}
    except FileNotFoundError:
        return {"success": False, "status": "UNAVAILABLE", "data_type": "UNAVAILABLE", "error": "Crop model file is missing. Install and verify the trusted model before using crop recommendations."}
    except Exception:
        current_app.logger.exception("Crop model inference failed")
        return {"success": False, "status": "UNAVAILABLE", "data_type": "UNAVAILABLE", "error": "Crop model could not produce a result."}


def disease_model():
    global _DISEASE_MODEL, _DISEASE_MODEL_PATH
    model_dir = Path(current_app.config["MODEL_DIR"])
    path = model_dir / "plant_disease_model.h5"
    if not path.is_file():
        legacy_path = Path(current_app.root_path).parent / "plant_disease_model.h5"
        if legacy_path.is_file(): path = legacy_path
    labels_path = model_dir / "disease_labels.json"
    if not labels_path.is_file(): labels_path = Path(current_app.root_path).parent / "data" / "disease_labels.json"
    if not path.is_file():
        raise FileNotFoundError("plant_disease_model.h5 is not installed")
    if not labels_path.is_file():
        raise FileNotFoundError("disease_labels.json is required before disease labels may be displayed")
    labels = json.loads(labels_path.read_text(encoding="utf-8"))
    if not isinstance(labels, list) or not labels or any(not isinstance(x, str) or not x.strip() for x in labels):
        raise ValueError("Disease label mapping is invalid")
    if _DISEASE_MODEL is None or _DISEASE_MODEL_PATH != str(path):
        from tensorflow.keras.models import load_model
        _DISEASE_MODEL = load_model(path, compile=False)
        _DISEASE_MODEL_PATH = str(path)
    shape = getattr(_DISEASE_MODEL, "input_shape", None)
    if not shape or len(shape) != 4 or not all(isinstance(x, int) for x in shape[1:]):
        raise ValueError("Disease model input shape must be a fixed NHWC tensor")
    return _DISEASE_MODEL, labels, _hash_file(path), shape


def predict_disease(image) -> dict:
    try:
        model, labels, version, shape = disease_model()
        height, width = int(shape[1]), int(shape[2])
        resized = image.resize((width, height))
        arr = np.asarray(resized, dtype=np.float32) / 255.0
        pred = np.asarray(model.predict(np.expand_dims(arr, 0), verbose=0))[0].astype(float).reshape(-1)
        if len(pred) != len(labels) or not pred.size or not np.all(np.isfinite(pred)):
            raise ValueError("Model output does not match verified labels")
        if np.all(pred >= 0) and np.all(pred <= 1) and abs(float(pred.sum()) - 1.0) < 0.02:
            conf = float(pred.max())
        else:
            # Do not invent a probability from unknown logits/activations.
            conf = None
        idx = int(np.argmax(pred))
        threshold = float(current_app.config.get("DISEASE_CONFIDENCE_THRESHOLD", 0.65))
        confidence_pct = round(conf * 100, 1) if conf is not None else None
        low = conf is None or conf < threshold
        label = labels[idx].strip()
        return {"success": True, "status": "MODEL_OUTPUT", "data_type": "MODEL_OUTPUT",
                "result": label if not low else "Low-confidence model result — expert confirmation needed",
                "candidate_label": label, "class_index": idx, "label_verified": True,
                "confidence": confidence_pct, "low_confidence": low, "model_version": version,
                "guidance": "Preliminary model output only; it is not a confirmed diagnosis. Confirm with a qualified local agriculture professional before treatment.",
                "symptoms": "Compare the visible symptoms with field conditions and a local expert; the model output alone is not enough to select treatment."}
    except FileNotFoundError as exc:
        return {"success": False, "status": "UNAVAILABLE", "data_type": "UNAVAILABLE", "error": str(exc)}
    except Exception:
        current_app.logger.exception("Disease model inference failed")
        return {"success": False, "status": "UNAVAILABLE", "data_type": "UNAVAILABLE", "error": "Disease model, preprocessing, labels, or output dimensions failed verification."}
