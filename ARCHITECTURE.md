# Architecture — Rythu Mitra Master Backend v1

## Request flow

`HTTP route → field allowlist/type/range validation → role check → record ownership/reference checks → domain table/service/provider/model → provenance-aware JSON response`

## Structure

- `backend.py`, `run.py`: compatibility entry points.
- `rythu_mitra_backend/__init__.py`: Flask app factory, headers and generic errors.
- `config.py`: `.env` loading, development/production settings, SQLite configuration.
- `db.py`: SQLite connection, additive table setup, schema version and legacy-record migration.
- `security.py`: auth wrappers, CSRF, public user serializer, audit log and capped single-process rate limiter.
- `resources.py`: per-domain field allowlists and role visibility.
- `routes/core.py`: auth/profile, dashboard, model entry points, calculators, weather, markets, schemes, intent suggestion, health.
- `routes/domains.py`: common secure CRUD and moderation for feature-specific tables.
- `routes/seeds.py`: seed label evidence, optional OCR, QR inspection, germination, complaint and escalation flows.
- `routes/disease.py`: preliminary image scan and private scan-history flow.
- `routes/legacy.py`: compatibility endpoints for original `/api/records/<kind>` consumers.
- `routes/admin.py`: admin/account controls, audit, data health, market CSV import.
- `routes/misc.py`: private image uploads, notifications and idempotent offline sync.
- `services/weather.py`, `markets.py`, `models.py`, `uploads.py`: provider adapters and ML/image logic.
- `tests/`: test-client and security workflow tests.
- `scripts/`: first-admin bootstrap, readiness and data-integrity checks.

## Database strategy

Every feature in `RESOURCE_TABLES` has a dedicated table with common columns for owner, parent farm, JSON payload, workflow status, source name/URL, data type, confidence, timestamps, and soft deletion through status. The key high-volume supporting tables are normalized separately: `users`, `uploads`, `notifications`, `audit_logs`, `disease_scan_history`, `offline_sync_operations`, `legacy_records`, `schema_migrations`.

This per-domain-table JSON payload approach is a migration-friendly v1 bridge from the original `records(kind, payload, ...)` design. It avoids putting every feature in one generic table and applies server-side allowlists, but it is not the final normalized data model. Fields that need analytics, unique constraints, complex reporting or external synchronization should later be promoted to typed columns with explicit migrations.

Existing original `records` entries are copied into `legacy_records` with data-type labels mapped conservatively. Original data is not dropped. Old `users` tables with a role CHECK that excludes `provider` are rebuilt only after a same-directory backup is attempted; failure to create that backup stops the migration.

## Providers and model integrity

Weather uses OpenWeather only when a key is configured. The market connector queries the official data.gov.in OGD resource generated through AGMARKNET when `DATA_GOV_IN_API_KEY` is configured; it returns `LATEST_REPORTED` daily prices, not tick-by-tick real-time data. An explicitly configured HTTPS adapter remains an optional compatibility path. The crop model is loaded only from a trusted pickle artifact. The disease model requires a class-label list whose length matches the output; malformed output is `UNAVAILABLE` rather than a guessed diagnosis. Confidence appears only when the model output looks like a probability distribution, and it is still not promised to be calibrated.

## Browser compatibility

All write APIs require a CSRF token and use same-origin cookies. The root route prefers `templates/rythu_mitra.html`, then `templates/index.html`, otherwise displays a backend-only JSON response. Existing frontend work is not replaced in this backend-only package.
