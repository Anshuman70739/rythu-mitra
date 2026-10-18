# Rythu Mitra

An integrated Flask + HTML/CSS/JavaScript farmer decision-support web application for Telangana. It includes the backend, frontend, market-data adapter, security controls, tests and project documentation.

## Start here

**New to this project? Read `HOW_TO_RUN_RYTHU_MITRA.md` first.** The code and model weight files are already merged into this repository's `main` branch. Open the Codespace for this repository and follow the guide to sync `main`, install dependencies, configure `.env`, run tests and start the server. Do not re-upload or extract the integration ZIP over this repository.

### Quick start in a Linux terminal

From the folder containing `run.py`:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
[ -f .env ] || cp .env.example .env
python -m pytest -q
python run.py
```

Before starting, edit `.env` and set a private development `SECRET_KEY`. In Codespaces open the forwarded port shown in the Ports tab, normally `5000`. The optional TensorFlow dependency is separate in `requirements-ml.txt` and is needed only when testing the disease model.

The repository includes `models/crop_model.pkl` and `models/plant_disease_model.h5`. The crop model must still be verified in the target environment. The authoritative 15-class disease-label mapping is not available, so disease-name predictions must remain unavailable until the original mapping is recovered and verified. Provider API keys are not included; weather and official daily mandi data need your own server-side credentials. Do not claim full integration based only on the page opening.

Never commit `.env`, private API keys, farmer data, uploads or local database files. Use `SECURITY.md` and `RELEASE_CHECKLIST.md` before any public launch.

## Main frontend files

- `templates/rythu_mitra.html` — app shell, accessible dialogs and single-page mount point.
- `static/css/rythu-mitra-tokens.css` — earthy color/type/spacing tokens.
- `static/css/rythu-mitra.css` — layout, cards, forms, data displays, breakpoints.
- `static/css/rythu-mitra-motion.css` — explicit no-scroll-reveal motion policy with reduced-motion support.
- `static/favicon.svg` — project favicon.
- `templates/privacy_policy.html`, `templates/terms_and_conditions.html` — dedicated pre-launch legal pages served at `/privacy-policy` and `/terms-and-conditions`.
- `static/css/legal.css` — restrained styling for standalone legal pages.
- `static/js/rythu-mitra-app.js` — routes, API client, modules, writes, statuses, locale, voice and offline queue.
- `static/locales/en.json`, `static/locales/te.json` — localization dictionaries.
- `static/data/resource-config.json` — field allowlists generated from backend `RESOURCE_SPECS`; it is UI metadata, not a security boundary.
- `scripts/generate_resource_config.py` — regenerate the resource field config after approved backend schema changes.

## Documentation

- `FRONTEND_IMPLEMENTATION_PLAN.md` — audit, design decisions, phase plan and integration gates.
- `FRONTEND_API_MATRIX.md` — page-to-endpoint map, payload/response expectations, auth and limitations.
- `FRONTEND_FEATURE_TRACKER.md` — every major requested module and feature with honest status.
- `FRONTEND_CHANGELOG.md` — changed files and known non-claims.
- `FRONTEND_TEST_REPORT.md` — actual checks run and integration tests still required.
- `BRAND_REFRESH_REPORT.md` — the current brand-rule changes and verification gaps.
- `PRE_LAUNCH_BRAND_CHECKLIST.md` — domain, legal, data-handling and production items that remain before launch.
- Existing `README.md`, `BACKEND_FEATURE_MATRIX.md`, `PROJECT_AUDIT.md`, `ARCHITECTURE.md`, `SECURITY.md` and `RELEASE_CHECKLIST.md` remain in the package.

## Status honesty / dependencies

- Weather needs `OPENWEATHER_API_KEY`.
- Crop recommendation needs trusted `models/crop_model.pkl`.
- Disease scan needs a compatible `models/plant_disease_model.h5`, matching `data/disease_labels.json`, and the optional ML dependencies.
- QR scan needs optional `pyzbar` and OS `zbar`; OCR requires Tesseract and optional `pytesseract`.
- Official daily mandi prices use the data.gov.in / AGMARKNET resource when `DATA_GOV_IN_API_KEY` is configured server-side. Register/sign in at data.gov.in and generate your own API key; never put the key in frontend JavaScript or commit it. Set `MARKET_DEFAULT_STATE=Telangana` (default) or the state relevant to the pilot. The endpoint returns `LATEST_REPORTED` daily observations, not tick-by-tick live prices; every row carries its source and price date. If the key/provider fails, the API returns `UNAVAILABLE` rather than inventing prices. The legacy custom HTTPS adapter remains an optional fallback when the official key is not configured.
- Generic `/api/v1/<resource>` screens are record-management CRUD; they are not proof every specialty workflow, official directory, live provider, or government integration is implemented.
- Seed complaints, crop damage and grievances are only saved to the Rythu Mitra backend. The app does not file official complaints/claims.
- Offline draft sync is supported only for the backend's allowlisted resource types. Uploads are not queued offline; the full application shell is not yet available for cold offline launch.

## Current test status

GitHub Actions passed the integration pull-request checks for Python compilation, required files/JSON, the Python test suite (`28 passed`) and JavaScript syntax. Static frontend contract checks also passed during package review. No end-to-end browser/API test, visual sign-off, live-provider test or full model-inference validation is claimed; see `FRONTEND_TEST_REPORT.md` for limits and remaining checks.
