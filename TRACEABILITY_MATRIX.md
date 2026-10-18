# Rythu Mitra traceability matrix — repaired candidate

Statuses are based on source checks in the candidate ZIP, not on a successful live deployment. `PASS (static)` means only that a structural source check passed. Runtime work is not `PASS` unless the associated tests execute.

| Requirement / workflow | Frontend | Backend | Data/model/provider | Test evidence | Status |
|---|---|---|---|---|---|
| App startup / home | `templates/rythu_mitra.html`, `static/js/rythu-mitra-app.js` | `run.py`, `backend.py`, app factory, `/` | Flask and base requirements | Python compile passed; runtime blocked (Flask unavailable in review environment) | BLOCKED |
| Session / CSRF / login | centralized `api()` and auth views | security helpers, `/api/session`, `/api/register`, `/api/login`, `/api/logout` | SQLite user/session data | Existing tests cover CSRF, serialization and owner isolation; test suite did not execute here | UNVERIFIED |
| Dashboard / private records | dashboard and resource pages | `/api/dashboard`, `/api/v1/<resource>` | SQLite records | Static API contract check passed; browser persistence not tested | UNVERIFIED |
| Crop recommendation | crop-planning form | `/api/recommendations`, `services/models.py` | trusted `crop_model.pkl` | Missing in candidate ZIP; active checkout asset must be checked | BLOCKED |
| Disease scan | crop-health upload and result view | `/api/disease-scan`, `services/models.py` | `plant_disease_model.h5`, `disease_labels.json`, TensorFlow | Candidate ZIP lacks weights and labels; bundle verifier detects this | BLOCKED |
| Weather | weather form/status | `/api/weather`, `services/weather.py` | server-side `OPENWEATHER_API_KEY` | Missing-key test exists; suite did not execute; live provider not tested | BLOCKED |
| Official daily mandi prices | Markets page, corrected live-result cards | `/api/markets?provider=live`, `services/markets.py` | data.gov.in / AGMARKNET API; `DATA_GOV_IN_API_KEY` | New mocked adapter tests added; no real key/network in review environment | PARTIAL — configuration needed |
| Curated market listing | Markets page | `/api/markets` without provider | admin-imported CURATED/DEMO records | Existing route and static checks only | UNVERIFIED |
| Market historical trend | trend form | `/api/markets/trend` | stored Rythu Mitra records | Does not imply official provider history is stored | PARTIAL |
| Income / storage scenarios | calculators | dedicated calculation endpoints | user-entered assumptions | Existing unit test covers one net-income calculation; suite blocked | UNVERIFIED |
| Seed checks / complaints | seed-safety workflow | `/api/seed/*` | optional OCR/QR libraries; local records | Existing tests cover germination arithmetic, QR preview and non-filing disclaimer; suite blocked | UNVERIFIED |
| Offline drafts | local draft queue and sync view | `/api/offline/sync` | browser local storage + server database | Existing idempotency test; browser/offline cycle not run | UNVERIFIED |
| Family helper / expert / admin | related workspace pages | role-protected routes | SQLite roles and audit events | Static only; no full role matrix run | UNVERIFIED |
| English / Telugu | locale dictionaries | profile language settings | `en.json`, `te.json` | JSON parse and key coverage check | PASS (static only) |
| Mobile/accessibility | CSS breakpoints, labels and status text | N/A | browser/device APIs | No physical-device, screen-reader or mobile E2E test | UNVERIFIED |
| Security / privacy | escaped display helpers, same-origin API client | CSRF, auth, role/ownership checks, upload helpers | cookies, private uploads and SQLite | Code review + selected existing tests; no complete security scan | PARTIAL |
