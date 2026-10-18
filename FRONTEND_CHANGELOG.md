# Frontend v2 changelog

## v2.0.0 — Master Backend v1 integration candidate

- Replaced the placeholder-heavy navigation with separate Home, Farms, Crop Planning, Crop Health, Seed Safety, Weather, Markets and More workspaces.
- Kept Flask/Jinja plus HTML, CSS, JavaScript and JSON locales. Root route serves `rythu_mitra.html` through the backend's existing template resolver.
- Added generated `static/data/resource-config.json` from the exact backend `RESOURCE_SPECS` allowlist for 68 record types.
- Added generic resource list/create/edit/soft-delete forms, metadata status/source fields, filters and role-sensitive actions.
- Added API-bound crop recommendation, yield reference, risk and irrigation forms; weather and market/trend forms; finance calculations; scan history; seed evidence/confirmation, QR and packet checks, informal germination, complaint capture, scheme matcher, offline drafts/sync, notifications, private uploads, family screens and admin summary/role/moderation UI.
- Added English/Telugu dictionaries, language persistence, visible source status, unavailable/error/empty states, responsive layout, keyboard focus and reduced-motion rules.
- Corrected Seed Safety complaint option to send backend-supported `dealer_refused_bill` rather than the unsupported `dealer_no_bill` code.
- Added revised implementation plan, endpoint matrix, feature tracker and test report.

## Not claimed in this release

- No end-to-end integration-tested label is assigned yet.
- Weather still needs `OPENWEATHER_API_KEY`; the official daily mandi connector is present but requires server-side `DATA_GOV_IN_API_KEY`. Crop/disease models, matching disease labels, OCR and QR dependencies are not bundled in this ZIP by default.
- Not all modules have specialized lifecycle workflows beyond the backend's available record CRUD.
- No official seed/damage/insurance/government filing, SMS/push/email, payment settlement, live booking availability, or complete offline shell caching.

## Frontend-only quality and interaction pass

- Consolidated frontend route rendering, added a real not-found route and updates document titles on navigation.
- Added stale-request guards/cancellation for route, session, authentication, image quality and disease-analysis requests.
- Centralized dashboard/weather/disease/record response-shape adaptation; safe translated API error messages replace raw server error text.
- Removed the homepage's four-card metric grid in favour of a single action-led hero and an optional open finance summary.
- Removed the guessed default weather city; the user/profile must provide a location.
- Added photo replace/remove/cancel controls, removed fake percentage progress, and bounded client-side preview analysis dimensions.
- Tightened focus restoration, profile-menu keyboard operation, English fallback, Telugu locale parity, mobile touch targets and reduced-motion behavior.
- Added `FRONTEND_MODIFICATION_REPORT.md` and `FRONTEND_MANUAL_TEST_CHECKLIST.md` with evidence and remaining manual checks.
