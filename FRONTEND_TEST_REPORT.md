# Rythu Mitra test report

Last updated: 2026-10-18 after integrating the complete frontend, backend, and model-weight files into `main`.

This report distinguishes automated checks from tests that require running the app or inspecting it in a real browser.

## Automated checks

| Check | Latest known result | Evidence / scope |
|---|---|---|
| Python source compilation | PASS | GitHub Actions on the integration pull-request revision compiled app/backend/run.py, backend package, scripts, tests and training script. |
| Required files and JSON | PASS | CI checked the frontend templates, JavaScript, model assets, disease-label instructions, locales, resource config, model manifest and label template. |
| Python pytest suite | PASS — 28 tests | GitHub Actions reported `28 passed in 5.22s` on the pre-merge pull-request revision. Re-run on `main` after any further code changes. |
| JavaScript syntax | PASS | CI ran `node --check static/js/rythu-mitra-app.js`. |
| Frontend contract static check | PASS during package review | `scripts/check_frontend_contract.py` passed for 68 resource schemas, 613 fields, English/Telugu locales, API markers, CSRF markers and seed-status enum. |
| Model asset verification | PARTIAL / BLOCKED | Both weight files are present and have recorded SHA-256 values. The authoritative disease-label mapping is absent, so the model bundle is not usable for showing disease names. |
| Local installed-environment health check | NOT RUN here | This review environment did not have Flask installed and external package downloads were blocked. Use `python scripts/health_check.py` in Codespaces. |

## Runtime and browser checks — still required

| Check | Status | What must be verified |
|---|---|---|
| Flask starts from `python run.py` | NOT VERIFIED in a browser session | Start it in the current main-branch Codespace and inspect any runtime traceback. |
| Homepage and navigation | NOT RUN | No browser end-to-end pass is claimed. |
| Registration, login, logout | NOT RUN | Test using non-sensitive demo accounts. |
| Two-user private-record isolation | NOT RUN | Confirm one test user cannot access another user's records. |
| Crop recommendation inference | NOT RUN | Weights are present; verify output and input handling in the target runtime. |
| Disease scan inference | BLOCKED | Recover and verify the exact 15-class mapping in its original output order first. Do not guess labels. |
| Weather and official daily mandi data | NEED CREDENTIALS | `OPENWEATHER_API_KEY` and `DATA_GOV_IN_API_KEY` are not included. Missing credentials must result in an honest unavailable state. |
| Mobile, keyboard, zoom, Telugu readability | NOT RUN | Requires actual browser/device inspection and human review. |
| Production deployment | NOT STARTED | Requires hosting, HTTPS, persistent secrets/storage, Redis rate limiting, backup/security review and final-domain tests. |

## Required next verification in Codespaces

1. Sync the merged `main` branch and install `requirements.txt` in a virtual environment.
2. Run `python -m compileall -q app.py backend.py run.py rythu_mitra_backend scripts tests train_model.py`.
3. Run `python scripts/check_frontend_contract.py`, `python -m pytest -q`, and `python scripts/health_check.py`.
4. Run `python scripts/verify_model_assets.py`; expect it to report the missing authoritative disease-label file until that mapping is recovered.
5. Start `python run.py`, forward port 5000 in Codespaces, and perform the browser checklist in `HOW_TO_RUN_RYTHU_MITRA.md`.

The website is not production-ready based solely on passing automated tests or opening the homepage.
