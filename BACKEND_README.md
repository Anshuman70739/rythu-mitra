# Rythu Mitra — Master Backend v1

A modular Flask + SQLite backend for the Rythu Mitra farmer decision-support prototype. This package is the **backend phase only**; the frontend is intentionally not changed until the backend is reviewed and approved.

## What this version provides

- App factory and compatibility entry points (`python run.py` and `python backend.py`).
- Existing legacy APIs retained where useful, plus feature-specific `/api/v1/<resource>` CRUD endpoints.
- A field allowlist for each resource; client input cannot set record owner, status, role, verification status, or source provenance.
- Account registration/login/logout, password hashing, public-user allowlisting, CSRF protection, role checks, per-owner reads/updates/deletes, audit records, rate limits, session expiry, and account suspension support.
- Dedicated SQLite tables for farm records, seed records, seed complaints and timelines, disease history, market prices, schemes, expenses/income/loans, water and irrigation, inventory and labour, livestock, harvest/storage, equipment and produce listings, experts, damage/insurance reports, FPO/community records, notifications, helpers, uploads, source records, and offline sync operations.
- Private image handling (decode/re-encode, size and pixel limits, random storage identifiers, owner-checked retrieval).
- Honest service status for weather and market data: `LIVE`, `CACHED`, `CURATED`, `DEMO`, or `UNAVAILABLE` as relevant. No weather is invented unless `DEMO_MODE=true`.
- Seed packet evidence/OCR assistance where Tesseract is installed, safe QR destination preview (no automatic fetching), label completeness checks, informal germination arithmetic, private evidence, complaint IDs, local timeline, and official escalation links.
- Disease-model verification gates, private scan history, and an expert-review workflow tied to a scan explicitly shared in a submitted expert question. A working model plus its `disease_labels.json` is required before a class label is returned.
- Crop reference checks, irrigation advice, transparent rule-based risk scoring, market-net calculation, sell/store scenarios, break-even calculations, historical market records, scheme possible-match output, and dashboard summaries.
- Admin source moderation, notifications, audit-log review, data freshness summary, user suspension/roles, and CSV import of market values as `CURATED` or `DEMO` only.

## Important limits

This is a broad **backend v1**, not a claim that all real-world integrations are complete. Generic resources provide a consistent storage/CRUD/authorization workflow; that does not mean each feature already has a specialized algorithm, notification scheduler, external provider, mobile UI, or third-party integration.

- Live weather requires a valid `OPENWEATHER_API_KEY`.
- Official daily mandi prices use the data.gov.in OGD resource generated through AGMARKNET when `DATA_GOV_IN_API_KEY` is configured server-side. These are latest reported daily observations, not instant tick-by-tick market quotes. A documented custom HTTPS adapter remains an optional compatibility path.
- Manual market CSV rows are drafts and must be reviewed. Old dates remain stale; do not change a date merely to make a quote look current.
- Crop and disease inference require trusted model assets. TensorFlow is an optional, large dependency for the disease model. The class-label file is required.
- OCR is optional. Install `requirements-ocr.txt` and a system Tesseract executable to use it. OCR output is not confirmed until the farmer reviews it.
- A seed image, QR value, lot number, or home germination check cannot prove a packet genuine. The service never returns a “genuine” verdict.
- Complaint, crop-damage, insurance, and scheme records are saved **inside Rythu Mitra only**. They are not filed with a government agency or insurer by this app.
- Browser voice, read-aloud, offline local drafts, accessible screens, and the full farmer workflow UI must be implemented and tested in the frontend phase.
- Every API receives coarse IP/account rate limiting; login, registration, scan and submissions also have stricter per-route limits. Local development uses a bounded in-memory limiter. Production requires reachable Redis configured in `REDIS_URL`; it refuses to start if Redis is missing. Set `TRUSTED_PROXY_HOPS` only to the verified reverse-proxy hop count.
- Generic domain records use dedicated tables with a JSON payload plus common owner/status/provenance columns. A later production phase should move high-volume and analytically queried fields to fully typed relational columns and add reviewed migrations.

Read `BACKEND_FEATURE_MATRIX.md`, `PROJECT_AUDIT.md`, `ARCHITECTURE.md`, `SECURITY.md`, `BUILD_PROGRESS.md`, `TEST_REPORT.md`, and `RELEASE_CHECKLIST.md` before integration.

## Requirements

Use Python 3.12 for the initial setup, especially if using older ML model artifacts.

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Ubuntu / Codespaces: source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env   # Linux/macOS/Codespaces; on Windows, copy .env.example .env
```

Edit `.env`. For local development, keep `APP_ENV=development`, `SESSION_COOKIE_SECURE=false`, `DEMO_MODE=false`, and choose a private stable `SECRET_KEY` of at least 32 characters. The development limiter stays in memory. For production, configure `APP_ENV=production`, HTTPS, a persistent `SECRET_KEY`, and a reachable Redis instance in `REDIS_URL`; production startup intentionally fails without those security prerequisites. `DEMO_MODE=true` seeds explicitly labelled demo accounts and fixtures; never enable it on a public deployment.

If the project uses its TensorFlow disease model:

```bash
pip install -r requirements-ml.txt
```

If optional packet OCR is wanted, install `requirements-ocr.txt` and the operating system's Tesseract executable separately.

## Run

```bash
python run.py
```

Open `http://127.0.0.1:5000`. The root route returns JSON until a compatible template exists in `templates/`; the full frontend will be connected only after backend review/approval.

Create the first administrator interactively (password is not echoed):

```bash
python scripts/create_admin.py
```

The script refuses to create a second bootstrap admin if an active admin already exists. Do not commit credentials or `.env`.

## Checks

```bash
python -m compileall -q .
pytest -q
python scripts/validate_data.py
python scripts/health_check.py
```

Optional security tools can be added later (`ruff`, `bandit`, `pip-audit`) after dependency/network availability. A check only counts as passing when it actually ran. See `TEST_REPORT.md` for checks performed while generating this bundle.

## API patterns

- Session/CSRF: `GET /api/session`; pass the returned token as `X-CSRF-Token` on writes.
- Auth: `POST /api/register`, `/api/login`, `/api/logout`, `POST /api/profile`.
- Dashboard: `GET /api/dashboard`.
- Weather: `GET /api/weather?city=Warangal`.
- Crop recommendation: `POST /api/recommendations` with `N`, `P`, `K`, `temperature`, `humidity`, `ph`, `rainfall`.
- Disease scan: `POST /api/disease-scan` with multipart `image` field; scan history at `GET /api/scan-history`; experts can submit preliminary reviews using `POST /api/disease-scans/<scan_id>/expert-review` only after that scan image is explicitly shared in an expert question.
- Seed workflow: `/api/seed/scans`, `/api/seed/qr-check`, `/api/seed/packet-check`, `/api/seed/germination`, `/api/seed/complaints`, `/api/seed/escalation`.
- Market prices/trend: `GET /api/markets`, `/api/markets/trend?commodity=Cotton&market=Warangal`; `GET /api/markets?provider=live` uses the official data.gov.in connector when `DATA_GOV_IN_API_KEY` is present, otherwise the optional configured custom adapter.
- Schemes: `GET /api/schemes/matches` (requires login).
- Domain resources: e.g. `POST /api/v1/farms`, `GET /api/v1/crop-tasks`, `POST /api/v1/expenses`, `POST /api/v1/seed-lots`, `POST /api/v1/seed-complaints`, `POST /api/v1/crop-damage-reports`.
- User-saved uploads: `POST /api/v1/uploads` multipart `image` and `category`; retrieve with `GET /api/v1/uploads/<id>` only when authorized.
- Offline synchronization: `POST /api/offline/sync`; supports idempotency keys and keeps client drafts until a confirmed `SYNCED` result.
- Admin: `/api/admin/*`, plus `/api/admin/resources/<resource>/<id>/moderate` for source/listing review.
- Operational status: `GET /health`, `GET /ready`.

Generic resource list/detail/write routes are described in `BACKEND_FEATURE_MATRIX.md`. The frontend should display `status`, `data_type`, `source_name`, `source_url`, `last_updated`, `last_verified`, `expires_at`, and `confidence` wherever returned; absence of a provider is shown as `UNAVAILABLE`, not filled with fake current data.
