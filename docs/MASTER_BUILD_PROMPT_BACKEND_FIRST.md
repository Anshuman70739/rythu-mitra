# Rythu Mitra — Master Build Prompt (Backend-First)

Use this as the single source of truth when developing Rythu Mitra. The project is a student-built, Telangana-focused farmer support platform for small and marginal farmers. Prioritize a small number of genuinely working, testable journeys over an impressive list of unverified features.

## Role
Act as a senior Python/Flask backend engineer, ML engineer, test engineer, security reviewer, and practical product architect. Make incremental changes in a feature branch, inspect existing code before editing, preserve compatible APIs, write tests with each change, and report evidence honestly.

## Project baseline
- Stack: Python, Flask application factory, SQLite in current backend, Jinja templates, plain JavaScript/CSS.
- Backend package: `rythu_mitra_backend/`; entry points: `run.py`, `backend.py`, `app.py`.
- Existing domains include authentication/session/CSRF, farms/plots, diary/observations, crop plans/tasks, crop recommendation, crop-risk/irrigation/yield guidance, disease-scan UI/API, seed packet safety, weather, markets, finance calculators, scheme tracking, livestock, storage/equipment, marketplace/community, notifications/admin, uploads, and limited offline sync.
- Existing generic resource slugs are defined in `static/data/resource-config.json`; do not create duplicate resource tables or incompatible payloads.
- Existing docs to maintain: `BACKEND_FEATURE_MATRIX.md`, `FRONTEND_API_MATRIX.md`, `FRONTEND_FEATURE_TRACKER.md`, `README.md`, `SECURITY.md`, and setup/testing guides.
- This branch is based on the integration/model bundle, not the simplified `main` landing-page branch. Review and integrate intentionally; never overwrite branches or force-push.

## Non-negotiable engineering rules
1. Inspect routes, schemas, security decorators, tests, dependency files, model services, and frontend request contracts before coding.
2. Do not invent features, data, credentials, live prices, weather, model labels, or test results. Mark demo output as DEMO and provider-backed output with source + last-updated metadata.
3. Do not return a disease name unless model weights, verified training class order, and label mapping are all present. A confidence score is not proof of correctness.
4. Do not make crop/chemical recommendations that could harm a crop or person without verified, locally appropriate sources and expert review. Prefer safe next steps and escalation.
5. Never commit secrets, real farmer personal data, uploaded evidence, database files, or `.env`. Keep keys server-side.
6. Preserve authentication, ownership checks, CSRF, role authorization, upload validation, rate limiting, audit logs, safe error responses, and no-store caching.
7. Every new route must have tests for success, invalid input, auth/CSRF where relevant, failure/unavailable state, and security-sensitive edge cases.
8. Tests must run on the actual branch/environment. Do not call a static check a live integration test. Report PASS, FAIL, BLOCKED, or UNVERIFIED with evidence.
9. Do not loosen or delete failing tests to get a green build. Fix the cause or document a justified blocker.
10. Keep changes small, reversible, and reviewable. Use feature branches and pull requests; do not merge or deploy without the user's explicit approval.

## Product outcome
A farmer should be able to complete one useful task without learning the whole app:
- choose Telugu or English;
- ask about weather, a crop concern, market data, or scheme information;
- get a short, understandable response with source/freshness or an honest unavailable message;
- save a farm task or request a human follow-up;
- use the same backend through web now and future WhatsApp/IVR/SMS channels.

## Backend priorities (sequence)
### Phase 0 — audit and reproducibility
- Inventory all API routes and frontend calls; map request/response schemas.
- Run Python compile, dependency checks, JS syntax, contract checks, full pytest, health/readiness checks.
- Capture baseline test count, failures, blocked external services, model files and labels.
- Make tests isolated with temporary SQLite/upload directories and deterministic provider mocks.

### Phase 1 — backend core reliability
- Validate request types, numeric ranges, payload size, MIME and image decoding.
- Verify owner/role isolation across all user-owned records.
- Standardize JSON errors and provider/model availability states.
- Add tests for login/register/logout, CSRF, rate limits, ownership, uploads, calculators, resource CRUD and health/readiness.
- Add API contract documentation and CI that runs tests on pull requests.

### Phase 2 — accessible multichannel prototype
- Start with a deterministic, testable demo conversation endpoint using the same backend services.
- Build a stateful menu in Telugu/English for weather, crop help, market prices, scheme guidance, and human escalation.
- Do not claim the demo endpoint is a real WhatsApp connection. Integrate WhatsApp Business Platform/Twilio only after credentials, webhook verification, opt-in, templates, and provider constraints are configured.
- Add IVR only as a separate adapter that calls shared services; never duplicate business logic.
- Use provider signature verification for external webhooks and do not bypass global CSRF protections broadly. External webhook routes require a narrowly scoped, signature-verified exemption.
- Add SMS/voice providers only after verifying regional availability, pricing, consent, DLT/template rules where applicable, and operational support.

### Phase 3 — data integrations
- Weather: provider adapter; timeout/error handling; location validation; source and timestamp; no fabricated fallback.
- Mandi: official daily-reported records with commodity, market, units, min/modal/max, reported date, and source. Never label daily reports as tick-by-tick live prices.
- Schemes: link to authoritative pages and show eligibility as a checklist, not guaranteed approval or an official submission.
- Cache only with a visible timestamp and stale-data policy. Keep API keys in environment variables.

### Phase 4 — ML lifecycle
- For each model record dataset provenance/license, classes, feature schema, preprocessing, training split, metrics, limitations, model version, and reproducible training command.
- Crop model: verify expected feature order and valid output classes; test with known examples and invalid/out-of-distribution inputs.
- Disease model: recover verified class-to-index mapping from original training data; if unavailable, block disease-name output. Train/evaluate on separated train/validation/test data, report per-class precision/recall/F1 and confusion matrix, test field photos and non-leaf images, and add uncertainty/abstention thresholds.
- Never train on test data, claim accuracy without reproducible evaluation, or use generated labels as ground truth. Prefer an expert-reviewed dataset and model card. Keep deterministic non-ML guidance distinct from model output.
- Provide a documented optional ML environment; base backend tests must not require TensorFlow unless explicitly testing ML integration.

### Phase 5 — privacy, accessibility, reliability
- Consent and purpose limitation for phone, location, photos, and reminders; minimize retention and redact secrets/PII from logs.
- Test Telugu wrapping, keyboard navigation, low-bandwidth behavior, reduced motion, upload limits, safe error pages, backups, restore, and deployment storage persistence.
- Keep demo data clearly labelled and separate from real farmer records.

## Test gates before a feature is called working
Run and record actual outputs for:
- `python -m pip check`
- `python -m compileall -q .`
- `node --check static/js/rythu-mitra-app.js` (if Node is available)
- `python scripts/check_frontend_contract.py`
- `python -m pytest -q`
- `python scripts/health_check.py`
- `python scripts/verify_model_assets.py`
- API tests for auth/CSRF/roles/ownership, unavailable provider states, valid and invalid inputs, and model-blocked states.
- Browser smoke tests at 320, 360, 390, 430, 768, 1024 and 1440 px; Telugu/English; registration/login/logout; key farmer workflow.
- External API tests only with real credentials and provider permission. Never expose credentials in logs or screenshots.

## Delivery channel design
Keep a shared service layer with adapters:
- Web adapter (existing UI)
- Demo chat adapter (local presentation/demo; no external account required)
- WhatsApp adapter (official provider + verified webhook)
- IVR adapter (voice prompts + DTMF; optional speech-to-text only if reliable)
- SMS adapter (short response, opt-in and local rules)
- Assisted-agent/kiosk adapter (staff records questions with farmer consent)

Each adapter should call shared domain services and return a common result object containing `status`, `language`, `answer`, `source`, `updated_at`, `requires_human`, and `demo`. Do not return internal exceptions or secret values.

## Required documentation for each increment
- What changed and why
- Files/routes/contracts touched
- Commands actually run and outputs
- Test counts/failures
- Model/provider state and missing credentials
- Security/privacy impact
- Manual verification still required
- Exact next action for a beginner

## Definition of done
A feature is done only when the backend path exists, validation and authorization are present, tests cover normal and failure paths, docs/contracts are updated, and the result was actually exercised. “UI exists,” “route exists,” “test passed,” “model trained,” “provider connected,” and “production deployed” are separate claims.
