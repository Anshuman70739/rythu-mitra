# Model Card — Crop Recommendation

## Intended use

Provide a preliminary crop-class suggestion from seven numeric inputs. This is a student-project decision-support aid, not a guarantee of crop suitability, yield, profit, or agronomic success.

## Artifact and inference

- Artifact: `models/crop_model.pkl` (with a legacy project-root fallback).
- Loader: Python pickle in `rythu_mitra_backend/services/models.py`.
- Expected feature order: `N, P, K, temperature, humidity, ph, rainfall`.
- A CI smoke test loaded the trusted artifact and produced the class `rice` for one fixed seven-feature test vector.
- Smoke-tested artifact SHA-256: `b2af5a37c81d19f878d7e7fe5529cc984ce2fdab4ac07d414a1928df5cad3606`.

## Evidence status

| Item | Status |
|---|---|
| Artifact present and loadable in CI | Verified |
| One seven-feature inference succeeds | Verified |
| Output belongs to model-declared classes, when available | Checked by smoke script |
| Original dataset, licence, and version | NOT VERIFIED |
| Training code/config and reproducibility | NOT VERIFIED |
| Held-out evaluation split | NOT VERIFIED |
| Accuracy, precision, recall, F1, confusion matrix | NOT VERIFIED |
| Probability calibration / confidence validity | NOT VERIFIED |
| Validation on Telangana field outcomes | NOT VERIFIED |

## Limitations and safeguards

- A model class label is not proof that the crop is appropriate for a particular farm.
- Soil values, units, local season, water access, pest pressure, market access, and farmer constraints may not be fully represented by the model.
- The smoke test uses a fixed synthetic input and is not an evaluation dataset.
- The model is a pickle artifact. Only load a trusted, reviewed artifact; pickle deserialization can execute code.
- Do not describe a model score as calibrated probability without a calibration evaluation.

## Required next evidence

Find the original training dataset and licence, feature preparation, class mapping, model training script/config, and a genuine held-out test set. Evaluate per-class precision/recall/F1 and confusion matrix. Compare any candidate model on the same held-out split before replacing this artifact.
