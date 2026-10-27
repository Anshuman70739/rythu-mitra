# Rythu Mitra — Repository Audit (2026-10-27)

> Status: initial evidence-based audit. Items marked **NOT VERIFIED** require a separate check; this is not a claim that every feature is complete.

## Recommendation

Use the existing GitHub integration branch as the application base. Do not replace the Flask app with the uploaded prompt/ZIP snapshot. The integration branch has the Flask app factory, backend package, templates/static assets, existing route modules, model services, tests, and CI workflow. The uploaded backend master prompt is the better execution specification because it explicitly requires audit-first work, model acceptance gates, honest provider states, privacy/security checks, and staged channel integrations.

## Branch and pull-request inventory

Observed GitHub branches include:

- main — commit 0a264977090a1ea75c459679b9e45c75dd6b50a0; the working assumption is that this is the simplified branch, but the full comparison of its tree is **NOT VERIFIED** in this audit.
- integration/complete-model-bundle-20261018 — commit a164b4a218e18bd765953d97e5c10231ff02084c; selected base for this backend PR.
- backend/multichannel-foundation-20261027 — feature branch for this work.
- Rythumitra-CD, Rythumitra-CD-test, RythuMitra, Rythumitra-SHX, and several backup/experiment/deploy branches also exist. Their intended ownership, unique commits, and deployment targets have **NOT VERIFIED**.
- PR #8 targets integration/complete-model-bundle-20261018; it has not been merged as of this audit.

No branches were deleted and no default/deployment branch was changed.

## Architecture confirmed from source

- Framework: Flask with application factory rythu_mitra_backend.create_app.
- Main package: rythu_mitra_backend/, with route blueprints for core, domains, seeds, disease, legacy, admin, misc, and channels.
- Entry points include app.py, backend.py, and run.py.
- Frontend uses templates and static assets; this audit did not run a browser-based UI check.
- Database configuration in rythu_mitra_backend/config.py currently resolves SQLite DATABASE_URL/DATABASE_PATH and explicitly rejects non-SQLite database URLs. PostgreSQL support is **NOT IMPLEMENTED/NOT VERIFIED**; do not promise hosted SQLite durability.
- Security controls visible in the app factory include CSRF validation on state-changing /api/ requests, a global API rate-limit hook, security headers, no-store cache policy for API/non-static responses, request-size handling, and a production secret-key check. Full route-by-route authentication and object-ownership coverage remains **NOT VERIFIED**.

## Model assets and readiness

- Model service expects crop_model.pkl and plant_disease_model.h5 in configured model directory or legacy project-root locations.
- Crop model is deserialized with pickle. Only load the trusted repository artifact; pickle loading is unsafe for untrusted files.
- Crop inference checks feature count and reports an artifact hash as a model version. Dataset provenance, class correctness, held-out metrics, and real-world calibration are **NOT VERIFIED**.
- Disease inference requires disease_labels.json as a non-empty JSON list, checks output count against label count, and uses a confidence threshold. The repository currently documents a required label template rather than verified class order; correct class mapping, preprocessing provenance, held-out metrics, and field-photo performance are **NOT VERIFIED**. Keep disease names blocked until these are verified.
- Run python scripts/verify_model_assets.py for artifact/label presence. The --load-disease option additionally requires TensorFlow and valid weights/labels.

## External providers

- Weather configuration reads OPENWEATHER_API_KEY.
- Market configuration reads DATA_GOV_IN_API_KEY, MARKET_DATA_API_KEY, and/or MARKET_DATA_BASE_URL.
- Current credentials and successful live provider requests are **NOT VERIFIED**. Never treat demo fixtures or cached demo weather as live data.
- Scheme links/checklists do not establish official eligibility or submission.
- The added chat/IVR endpoints are local simulations; no WhatsApp message or telephone call is placed.

## CI baseline and known failure

GitHub Actions run 40543551554 on commit 0d07a049f0b74ca85c22e820d772811b549c7e30 showed:

- dependency consistency check: passed;
- Python compile check: passed;
- pytest: **34 passed in 8.12 seconds**;
- health/readiness smoke script: failed because scripts/health_check.py called helpers using Flask current_app outside an application context.

Fix committed on the same feature branch as 053bd4b2aba6faf81003b0ca5ae4a87e156f5527. After the fix, GitHub Actions run 40546560369 completed successfully: dependency check, compile check, **34 pytest tests**, and health/readiness smoke check all passed. A subsequent run 40546770944 also passed after adding the crop-model smoke check. The current verified crop-model smoke result is one prediction (`rice`) from the seven ordered input features; this is a load/inference check only, not an accuracy or field-validity claim.

## Changes in this increment

- docs/MASTER_BUILD_PROMPT_BACKEND_FIRST.md: merged execution guidance for audit-first, Flask compatibility, model verification, test gates, safe data/provider states, and staged channels.
- rythu_mitra_backend/routes/channels.py: bilingual demo chat and simulated IVR routes with explicit DEMO/UNAVAILABLE states and safe responses.
- rythu_mitra_backend/__init__.py: registers the channels blueprint.
- tests/test_channels.py: tests language/menu behavior, no fabricated market prices, unverified disease-label warnings, input validation, CSRF, and missing weather configuration.
- docs/MULTICHANNEL_BACKEND_CONTRACT.md: documents the demo route contract and limitations.
- .github/workflows/backend-channel-tests.yml: backend verification workflow.
- scripts/health_check.py: fixed Flask application-context usage; verified health/readiness returned HTTP 200 in CI.
- scripts/check_crop_model.py: added a smoke test for loading the trusted crop artifact and running one prediction; CI returned `rice` for the fixed seven-feature sample. This does not establish model accuracy.

## Prioritized next work

1. Confirm latest CI after the health-check fix; fix the underlying cause of any remaining failures.
2. Complete route/API inventory against frontend requests and record method, auth, CSRF, validation, response shape, provider/model dependencies, and tests.
3. Verify crop model loading, feature schema, and allowed labels using trusted artifact provenance; report metrics only if a reproducible evaluation dataset exists.
4. Keep disease diagnosis unavailable until the original class order/labels and preprocessing are verified; do not generate labels by guessing.
5. Implement/verify weather and mandi provider adapters with source, reported timestamp, freshness, timeouts, and clear unavailable/demo states.
6. Test record ownership isolation, auth/session flows, upload validation/cleanup, and financial calculations.
7. Decide database persistence/migration strategy only after reviewing existing schema and hosting constraints; make reversible migrations and never delete a database.
8. Only then consider official WhatsApp Cloud API test-number integration, with opt-in, signature verification, idempotency, and secret-safe logs. IVR remains simulated until separately approved.

## Not yet completed

- Full API route and frontend-call inventory.
- Browser/manual responsive checks in English and Telugu.
- End-to-end live weather/mandi tests (credentials are not verified).
- Reproducible model evaluation and dataset/licence audit.
- Database backup/restore and persistent-host deployment verification.
- Production WhatsApp/IVR integrations.
