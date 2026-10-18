# Rythu Mitra frontend v2 — revised implementation plan

## Audit result

This build keeps the existing plain HTML/CSS/JavaScript + JSON locale approach and the backend's Flask/Jinja template route. The supplied patched frontend had a useful shell, English/Telugu dictionaries and a crop photo flow, but most of the requested farm workflows were not present. v2 expands the application into separate, navigable workspaces with reusable UI, a schema-driven record form, same-origin fetch, CSRF headers, server-returned status/source metadata, local offline drafts and explicit unavailable states.

**What was inspected:** `rythu-mitra-frontend-patched(2).zip`; `rythu-mitra-master-backend-v1.zip`; `README.md`; `BACKEND_FEATURE_MATRIX.md`; `rythu_mitra_backend/routes/{core,domains,disease,seeds,misc,admin}.py`; `rythu_mitra_backend/resources.py`; `rythu_mitra_backend/security.py`; `rythu_mitra_backend/services/{weather,markets,models,uploads}.py`; and backend tests.

**Workspace limit:** these files were the latest snapshots in the ChatGPT Library. The live Codespaces working tree and its Git status could not be queried from this environment. This package is a merged, runnable candidate based on the supplied backend snapshot, not a commit applied to your GitHub repository.

## Revised architecture

- Server: existing Flask app factory and API. The root route already selects `rythu_mitra.html` if it exists, so no template-name change or extra competing home route is needed.
- Presentation: single-page, hash-routed HTML view rendered by `static/js/rythu-mitra-app.js`; no React migration, bundler, or external runtime dependency.
- Design system: tokens in `static/css/rythu-mitra-tokens.css`, layout/component rules in `rythu-mitra.css`, and reduced-motion-aware transitions in `rythu-mitra-motion.css`.
- Language: `static/locales/en.json` and `te.json`; preference is held locally and persisted to the profile when signed in.
- Resource forms: `static/data/resource-config.json` is generated from the backend `RESOURCE_SPECS` allowlist. Forms only submit listed business fields; owner, role, moderation, verification, status and source-provenance fields remain server-controlled.
- Auth/security: `GET /api/session` obtains the session and CSRF token; writes use the returned token in `X-CSRF-Token`, use same-origin credentials, and render backend failures visibly.
- Offline: local drafts for the documented sync-allowed resource list only; submission IDs are stable across retries and the UI distinguishes `LOCAL_ONLY` from server-confirmed `SYNCED`. Uploaded images are not queued offline.

## Route / page hierarchy

### Public/primary routes

| Hash route | Purpose |
|---|---|
| `#/home` | “What should I do today?”, tasks, alerts, price/source status and recorded finance totals |
| `#/farms` | Farm and farm-plot records |
| `#/crop-planning` | Model crop recommendation, rule-based risk, irrigation advice, yield reference, crop plan/task/rotation records |
| `#/crop-health` | Image upload/preview, preliminary result, low-confidence treatment, saved scan history and disease information |
| `#/seed-safety` | Multi-photo evidence capture, OCR candidates, farmer confirmation, packet completeness, QR decode/check, informal germination and complaint/escalation |
| `#/weather` | Provider-backed conditions/forecast/advisories or an explicit unavailable response |
| `#/markets` | Market records, price dates/freshness, trend, net value, break-even and sell/store scenarios |
| `#/more` | Grouped secondary module launcher |

### More routes

`#/soil-inputs`, `#/diary`, `#/calendar`, `#/finance`, `#/schemes`, `#/damage`, `#/livestock`, `#/harvest`, `#/equipment`, `#/marketplace`, `#/expert`, `#/notifications`, `#/evidence`, `#/family`, `#/settings`, `#/help`, `#/offline`, and role-gated `#/admin`.

Schema-driven detail workspaces use `#/resource/<resource-slug>` for the backend's allowlisted resources. A specific resource page is record management only unless a dedicated service endpoint is listed below. On mobile, the bottom bar prioritizes Home, Crop Planning, Crop Health and More; Seed Safety remains available from the main sidebar/More section so long Telugu labels have room to wrap.

## Implementation phases

| Phase | Scope | Current build status |
|---|---|---|
| 0 — Audit and API map | Inspect source; document endpoints, allowlists, auth/CSRF and limitations | **Implemented in docs**; runtime tests of this combined package remain pending |
| 1 — Design system and shell | Responsive nav, tokens, reusable UI, account/session, locale, global errors | **Implemented in source**; browser/accessibility testing pending |
| 2 — Core farmer workflow | Profile, farms/plots, dashboard, diary/tasks/calendar, crop planning | **Implemented in source** via dedicated tools + actual CRUD; task calendar reminders are not scheduled by backend |
| 3 — Crop and field tools | Scan/history, weather, soil/input/irrigation/risk, provenance displays | **Implemented in source**; models/providers are conditional; expert scan review is incomplete |
| 4 — Seed Safety | Packet photos, OCR candidates, farmer confirmation, QR checks, germination, complaint evidence/escalation | **Implemented in source**; OCR/QR packages are conditional; no official complaint filing |
| 5 — Markets and economics | Market/trend, price freshness, income and expense records, scenarios, loans/storage | **Implemented in source**; live market adapter is conditional and finance is arithmetic only |
| 6 — Schemes, damage and services | Scheme matching/tracking, damage/insurance/grievances, livestock, harvest/storage, equipment, produce | **Record management implemented**; deeper lifecycle/provider workflows need follow-up |
| 7 — Expert, community and inclusion | Expert and community records, notices, voice/read-aloud, local drafts, family helper | **Partially implemented**; community moderation breadth and consent/revocation need review; offline shell caching is not implemented |
| 8 — Admin and verification | Role-restricted user/moderation/source screens, health and audit, security/accessibility | **Partial UI implemented**; add end-to-end role tests, field testing and production security review |

## Shared component plan

- **Inputs:** schema-driven fields with label/help/required states; number/date/boolean/array/object support; validation before requests.
- **Cards/lists:** semantic record cards, metadata line, source links, status badges and actionable empty states.
- **State:** loading skeleton/announcement, empty state, inline API error with retry, success toast after server acknowledgement, offline warning, local-only/synced labels.
- **Evidence:** image file validation, preview, multipart upload and private upload reference; evidence IDs should be kept private.
- **Safety:** confidence and model output labels, stale/cached/data type labels, not-filed notices, confirmation before role/data state changes.
- **Accessibility:** skip link, semantic headings/forms/dialogs, visible focus, keyboard controls, aria live regions, 48px touch targets for key controls, reduced motion and Telugu wrap handling.

## Endpoint mapping

The file `FRONTEND_API_MATRIX.md` lists page, method, request shape, response fields, auth and limitations. The resource form schema comes directly from `rythu_mitra_backend/resources.py`, not a hand-invented property set.

## Dependencies and external integration gates

1. **Weather:** set `OPENWEATHER_API_KEY` to use the configured provider. Without it, expect `UNAVAILABLE`; do not use a live label.
2. **Crop recommender:** add the maintainer-verified `models/crop_model.pkl`; without it, `/api/recommendations` should return `UNAVAILABLE`.
3. **Disease scan:** compatible `plant_disease_model.h5`, valid `data/disease_labels.json` and optional TensorFlow stack are required. Keep no label/low-confidence results non-diagnostic.
4. **QR/barcode:** optional `pyzbar` plus system `zbar`; manual printed text entry remains the fallback. QR destination is not fetched.
5. **OCR:** optional `pytesseract` plus Tesseract executable. Extracted text remains unconfirmed until the farmer explicitly confirms values.
6. **Live market:** direct data.gov.in / AGMARKNET daily adapter now exists; configure `DATA_GOV_IN_API_KEY` server-side and run a live smoke test. Current curated records never become live by import time; official output is `LATEST_REPORTED`, not tick-by-tick real-time.
7. **Official sources:** maintainers need source-owner approval, source URLs, freshness rules and verification dates for schemes, local offices, helplines and market feeds.
8. **Notifications/payment/official filings:** SMS/push/email, payments, government filing, insurance systems, buyer settlement and live provider booking are outside the current backend contract.
9. **PWA offline shell:** drafts are local, but caching the app shell for offline cold start needs a root-scoped service-worker route; do not claim full offline-first operation yet.
10. **Family helper:** the backend demands an existing registered helper ID. A friend invite-by-phone/email workflow is not included in v1.

## Release gate

Do not mark the frontend “complete” based on screens. Run the backend pytest suite, perform account-role integration tests, verify each listed workflow in a real browser against the running Flask app, inspect network failures and freshness states, test mobile and keyboard-only behavior, and review upload/privacy boundaries. The attached test report separates source-level checks from blocked runtime verification.


## Frontend polish pass — October 2026

The current updated source keeps the established HTML/CSS/vanilla-JavaScript stack. The home page now uses an action-led hero without the four-card metric row; weather does not assume Hyderabad when a user has not supplied a location; data-response adaptation remains isolated; Crop Health offers replace/remove/cancel controls and shows only supported confidence; English/Telugu locale key sets match. Static verification details and limitations are recorded in `FRONTEND_MODIFICATION_REPORT.md`, with device/browser checks in `FRONTEND_MANUAL_TEST_CHECKLIST.md`.
