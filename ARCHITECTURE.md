# Architecture

## Current implementation

Rythu Mitra uses a deliberately small Flask application rather than replacing the existing Flask direction.

```text
Browser / PWA shell
  → Flask routes (`backend.py`)
  → validation + CSRF + session/role checks + rate limits
  → SQLite (`data/rythu_mitra.db`) / model artifacts / OpenWeather
  → JSON responses
  → responsive HTML, CSS, and vanilla JavaScript UI
```

`app.py` is the simple local entry point. `backend.py` owns configuration, routes, narrow service helpers, the SQLite schema/seed data, and ML integration. The compact prototype keeps this together to avoid a premature framework migration; its helpers are deliberately separable into `routes`, `services`, `models`, and `security` packages if it grows.

## Data and access model

SQLite has `users`, generic provenance-bearing `records`, `notifications`, and `audit_logs`. Records support market, schemes, equipment, storage, buyers, questions, disease knowledge, bookings, listings, disaster reports, and feedback. Each record includes status, source, source URL where available, data type, and update timestamps. Farmer-owned submissions are associated with their account.

Roles are farmer, expert, admin, and buyer. Authenticated endpoints use server-side session checks; the admin summary requires the `admin` role. State-changing APIs require a session-bound CSRF token and use parameterized SQLite statements.

## ML and integrations

The supplied `crop_model.pkl` is loaded only on its first recommendation request and receives the existing seven-feature order: N, P, K, temperature, humidity, pH, rainfall. The supplied `plant_disease_model.h5` is loaded on the first scan, accepts 128×128 RGB data, and returns 15 output classes. No verified class mapping accompanied the artifact, so the UI deliberately returns a model class index rather than inventing a disease name.

Weather reads `OPENWEATHER_API_KEY` from the local environment (or `.env`, never source). It uses a timed server-side request. If no key is configured it returns clearly-labelled demo weather; provider failures return safe errors.

## Security decisions

The application sends CSP, frame, MIME-sniffing, referrer, and permissions-policy headers; never lets a client specify a fetch URL; limits API use; validates JSON numerics; rejects unsafe uploads; decodes/re-encodes accepted images under generated names; escapes dynamic UI values; and hides operational errors from clients. HTTPS-only session cookies are enabled by `SESSION_COOKIE_SECURE=1` for deployment.

## Offline behavior

`static/sw.js` caches the app shell only. It never presents weather as current while offline; live API requests remain network requests and can be retried.
