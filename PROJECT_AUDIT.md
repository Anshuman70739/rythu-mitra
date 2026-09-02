# Project Audit — pre-build baseline

Audit date: 2026-08-15

## Structure and stack

The repository initially contained only `backend.py`, an empty `app.py`, `train_model.py`, a scikit-learn crop model (`crop_model.pkl`), a Keras HDF5 disease-model artifact (`plant_disease_model.h5`), and this build plan. The intended stack is Python, Flask, requests, scikit-learn, TensorFlow/Keras, and NumPy. No templates, static assets, package manifest, database, test suite, environment sample, or project documentation existed.

## Existing features and execution flow

| Feature | Files / flow | Status | Findings / action |
|---|---|---|---|
| Crop recommendation | `/predict` → pickle model → fertilizer helper | Partially working | Logic was reasonable but had no validation, error handling, or UI. Preserve model and safely wrap it. |
| Fertilizer advice | `fertilizer_advice()` | Partially working | Preserve conservative nutrient tips; label as general guidance. |
| Yield estimate | `/yield-estimate` rule score | Partially working | Preserve as a transparent, non-trained favorability estimate. |
| Weather | `/weather` → OpenWeather | Insecure/broken | Key was hardcoded; no timeout/validation/provider handling. Move to environment config. |
| Disease detection | intended Keras load | Broken | Syntax error, `tensorflow.kreas` typo, and wrong model path. Retain supplied artifact and load lazily with safe failure handling. |
| Training utility | `train_model.py` | Repaired | The personal absolute cache path was replaced with an explicit local CSV argument and required-column validation. |

## Routes, data, and frontend

Initial routes were `GET /weather`, `POST /predict`, and `POST /yield-estimate`. There was no authentication, authorization, storage, uploads, or frontend/backend integration. The crop model is a 3.5 MB pickle; the disease model is a 20 MB Keras HDF5 artifact. Crop data was not included. No disease label mapping was included, so the app must state when a model result cannot be reliably named.

## Security and dependency findings

- **Critical:** an OpenWeather credential was hardcoded in `backend.py`. It must be rotated outside the repository. The rebuilt code uses only `OPENWEATHER_API_KEY`; no value is recorded here.
- No `.gitignore` or `.env.example`; no security headers, CSRF controls, upload controls, input validation, rate limiting, or safe production errors.
- No database means no privacy/access controls existed.
- `backend.py` fails `py_compile` because of an incomplete assignment.
- The apparent `.git` directory is read-only and not a usable Git repository (`git status` reports not a repository), so local commits cannot currently be created without a writable Git metadata directory.

## Preserve / repair / build

Preserve the two supplied model artifacts, crop prediction feature order (`N,P,K,temperature,humidity,ph,rainfall`), fertilizer heuristics, and the transparent yield heuristic. Repair the backend and weather configuration. Build the database, authenticated roles, safe uploads, dashboard, integrated feature APIs/UI, demo data with provenance, tests, PWA behavior, documentation, and release checklist.

## Risk assessment

Disease-class labels cannot be inferred safely from the supplied artifact alone; results will be class-indexed unless a verified label mapping is later provided. Live weather requires an already configured environment variable. Market, equipment, storage, scheme, and community data will be explicitly labelled as curated demo data rather than represented as live services.
