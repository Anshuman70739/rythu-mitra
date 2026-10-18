# Frontend test report — integrated v2 repair candidate

Date: 2026-10-15. Source-level and static brand checks only; no end-to-end browser pass is claimed.

| Check | Result | Evidence / limitation |
|---|---|---|
| JavaScript syntax | PASS | `node --check static/js/rythu-mitra-app.js` exited successfully after the market renderer change. |
| Locale/resource JSON | PASS | All three JSON files parse. The new `LATEST_REPORTED` string was added to English and Telugu. |
| Frontend API/contract static check | PASS | `scripts/check_frontend_contract.py` passes for 68 resource schemas, 613 fields and expected routes/CSRF markers. |
| Live market card rendering | CODE CHANGED, BROWSER TEST NOT RUN | Live action now includes commodity, market, location, observation date, min/modal/max values, stale warning and source metadata. Verify visually in Codespace. |
| Backend API integration | BLOCKED | Flask dependency could not be installed in the review environment; test suite did not run. |
| Live market provider | BLOCKED | Requires `DATA_GOV_IN_API_KEY` in the user's server environment; no credential was supplied or copied into this package. |
| Crop/disease model result rendering | BLOCKED | Candidate ZIP lacks model assets. Use the model files in the actual repository and verify label mapping before testing. |
| Phone sizing, keyboard, screen reader, Telugu native review | NOT RUN | Requires real browser/device and human review. |

## Required browser workflows

1. Start with `python run.py`; ensure port 5000 is forwarded in Codespaces.
2. Confirm `/`, `/api/session`, `/health`, `/ready` and browser console have no critical errors.
3. In Markets, search commodity and district, choose the official latest-data action, verify source and price date, and test the missing/wrong-key error state.
4. Verify the live card never shows a generic title, never labels daily data as instant real-time, and displays min/modal/max only when source values passed validation.
5. Check 360px-wide mobile viewport, 200% zoom, long Telugu text, keyboard focus, loading/error announcements and slow-network behavior.
6. When model files are verified, test one valid image, one corrupted image, an oversized image, a low-confidence result and unavailable model state.


## Brand and trust checks added on 2026-10-15

- App favicon, application footer legal links, and dedicated privacy/terms templates added.
- `tests/test_legal_pages.py` now checks the legal routes, favicon route, and retained brand constraints when run with Flask installed.
- Inline SVG references checked against defined symbols; no missing symbols found.
- Static source scan passed for no em/en dashes, no smooth scroll, no reveal/shimmer animation names, no builder branding, rectangular language/profile controls, and legal routes/links.
- Python compilation, JavaScript syntax, locale/resource JSON parse, HTMLParser checks and `scripts/check_frontend_contract.py` passed.
- Full `pytest` attempted but blocked during `tests/conftest.py` import because Flask is not installed in the audit environment (`ModuleNotFoundError: No module named 'flask'`).
- Headless Chromium screenshot attempt timed out in this environment; no visual browser sign-off is claimed.
- Custom domain, live API keys, model asset/label verification, legal contact details and external legal/Telugu review remain launch blockers.
