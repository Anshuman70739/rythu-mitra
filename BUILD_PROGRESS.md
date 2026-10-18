# Build Progress — Backend first

## v1 pass completed in source
- Created Flask package/app factory while preserving `backend.py` import compatibility.
- Added dedicated per-feature tables and resource allowlists for all requested backend domains.
- Added auth/CSRF/public-user serialization, rate-limit/audit helpers, role checks, owner checks, private upload handling and admin moderation.
- Added seed packet evidence/OCR-assisted text, QR comparison without network fetch, informal germination calculator, complaint records and official escalation links.
- Added disease inference validation/history and model-asset fallback to original root directory.
- Added honest weather states and a direct data.gov.in/AGMARKNET daily market adapter with `LATEST_REPORTED` status; real requests still require a user-issued server-side API key.
- Added finance, irrigation/risk, task status, market trend, dashboard totals/alerts, notifications, offline sync and expert Q&A relationships.
- Added documentation, admin bootstrap, health/data validation scripts and pytest test suite.

## Must happen in the user's Codespace before integration is accepted
1. Create/use a Python 3.12 virtual environment and install `requirements.txt`.
2. Run `python -m compileall -q .`.
3. Run `pytest -q`.
4. Run `python scripts/validate_data.py` and `python scripts/health_check.py`.
5. Resolve failures; compare the app behavior against the original database copy before migration.
6. Add trusted model files and `data/disease_labels.json`, then validate inference and preprocessing.
7. Configure weather and/or an approved market adapter as needed.
8. Review backend and explicitly approve it before beginning the frontend work.

## Do not mark complete yet
- Integration tests were not executed in the builder because Flask/Pillow were missing and package downloads could not be reached.
- The frontend has not been changed or connected in this phase.
- No official seed, scheme, insurance, notification, or government complaint submission is performed. Official daily market lookup code is implemented but requires a server-side data.gov.in API key and a successful live smoke test.
