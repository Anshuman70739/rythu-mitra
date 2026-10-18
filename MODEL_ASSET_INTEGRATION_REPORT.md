# Model asset integration report

This file documents what is actually included in this release package.

## Included

- Updated HTML/CSS/JavaScript frontend and its locale/resource configuration.
- Updated Flask/Python backend, route modules, services, DB/security modules, and tests.
- Crop model at `models/crop_model.pkl` (3,540,062 bytes; SHA-256 `b2af5a37c81d19f878d7e7fe5529cc984ce2fdab4ac07d414a1928df5cad3606`).
- Plant-disease model at `models/plant_disease_model.h5` (20,015,648 bytes; SHA-256 `9f29ee27d3c0298576cdd18ded8c1a72b6d8b8c1c5d79cbe9eea93be45c8dfe9`).
- Original source `train_model.py`, `app.py` compatibility entry point, `.gitattributes`, and `MODEL_PROVENANCE.md`.
- `models/MODEL_ASSET_MANIFEST.json`, a 15-slot label template, and explicit disease-label setup instructions.

## Important limitation: disease labels

The source bundle records a model output shape of `(None, 15)` but includes no verified names/order for the 15 output classes. `data/disease_labels.template.json` is only a placeholder; it is not the runtime label file. The actual `data/disease_labels.json` is deliberately not created, because guessed names could cause false crop-disease results. Until an authoritative 15-entry mapping is recovered, the model weights are present but named disease predictions remain unavailable.

## Where model files live

The updated backend defaults `MODEL_DIR` to `models/`, so the weights are placed there. The app's configured loader checks the expected files at this location. TensorFlow is in optional `requirements-ml.txt`; the base app dependencies do not install it automatically.

## Verification scope

Archive contents, model file sizes, SHA-256 checksums, JSON validity, Python compilation and JavaScript syntax are checked when assembling the bundle. Runtime tests may still depend on installing the project's requirements, the selected Python/TensorFlow version, a trusted disease label map and environment configuration. A hash confirms file identity, not model accuracy or prediction quality.
