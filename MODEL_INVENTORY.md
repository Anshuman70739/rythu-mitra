# Rythu Mitra Model Inventory

Last checked: 2026-10-27 via GitHub Actions on the backend feature branch.

| Artifact | Presence | Load/inference status | Data provenance and metrics | Product status |
|---|---|---|---|---|
| `models/crop_model.pkl` (legacy project-root fallback is supported) | Present according to the CI health check | **PASS — smoke tested.** Trusted artifact loaded and predicted `rice` for one fixed seven-feature input. Artifact SHA-256: `b2af5a37c81d19f878d7e7fe5529cc984ce2fdab4ac07d414a1928df5cad3606`. | Dataset origin/licence, training script/config, held-out split, per-class metrics, calibration, and field performance: **NOT VERIFIED**. | Basic inference is operational in CI; do not claim model accuracy or field suitability. |
| `models/plant_disease_model.h5` (legacy project-root fallback is supported) | Present according to the CI health check | **BLOCKED.** Disease inference requires verified `disease_labels.json`; CI confirms no usable label bundle is installed. TensorFlow loading and preprocessing are not verified by the base CI job. | Original training class order, dataset origin/licence, preprocessing, held-out metrics, field-photo performance, and uncertainty calibration: **NOT VERIFIED**. | Do not present a disease name or treatment based on this model until the original label map and preprocessing are verified. |

## How to re-check

From the repository root:

```bash
python scripts/check_crop_model.py
python scripts/verify_model_assets.py
python scripts/verify_model_assets.py --load-disease
```

The disease command needs TensorFlow and a valid disease label file. A missing label file is a genuine blocker, not a reason to guess labels.

## Acceptance rules

- A successful load/inference smoke check is not an accuracy evaluation.
- Do not deserialize model files from untrusted sources.
- Do not retrain until the dataset, licence, class names, feature schema, preprocessing, and evaluation split are known.
- Never manufacture disease class labels. Recover them from the original training code/data or model author.
