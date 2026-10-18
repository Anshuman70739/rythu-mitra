# Test Report — Rythu Mitra integrated v2 repair candidate

Date: 2026-10-15. Scope: extracted integrated v2 archive, modified in an isolated copy. Original archives were not changed. This is not a test of the user's active remote Codespace.

## Checks executed in this environment

| Check | Result | Details |
|---|---|---|
| Python source compile (`python -m compileall -q .`) | PASS | All candidate Python files compiled. This does not import dependencies or start Flask. |
| Frontend JS parse (`node --check static/js/rythu-mitra-app.js`) | PASS | No JavaScript syntax error. |
| Frontend contract script (`python scripts/check_frontend_contract.py`) | PASS | 68 resource schemas, 613 field definitions, locale/resource config parse, core API markers, CSRF and market provider markers. |
| Locale/resource JSON parsing | PASS | `en.json`, `te.json`, and `resource-config.json` parse successfully. |
| Disease/crop asset verifier | BLOCKED / EXPECTED IN ZIP | `scripts/verify_model_assets.py` reported the crop `.pkl`, disease `.h5`, and `disease_labels.json` missing from the candidate ZIP. The user says model files are in GitHub; run the verifier inside the active checkout and preserve the model assets while applying repairs. |
| Backend pytest suite | BLOCKED | `python -m pytest -q` stops while importing `tests/conftest.py`: `ModuleNotFoundError: No module named 'flask'`. Installing dependencies was attempted but package-index DNS/network access failed in this review environment. No pytest pass is claimed. |
| Official market adapter live smoke | BLOCKED | Requires the user's own `DATA_GOV_IN_API_KEY`, and this review environment could not reach package/provider hosts. Mocked regression tests were added, but could not execute through Flask here. |
| Live weather provider | NOT RUN | No user OpenWeather key supplied. |
| Browser end-to-end / mobile / screen reader | NOT RUN | A full browser test environment was not available here. |
| Bandit / pip-audit / coverage | NOT RUN | Tool installation unavailable in this environment. |

## Test coverage added

Six regression tests in `tests/test_backend.py` cover: valid official-provider row and field normalization, invalid minimum/modal/maximum ordering, missing official API key, stale observation dates, provider timeouts, and malformed rows. They are **added but not executed through Flask** here due to the missing Flask dependency. A separate dependency-light mocked harness against the market service passed the valid-row normalization/filter case, impossible-price rejection, and missing-key status case.

## Recommended checks in the Codespace

From project root, using a Python 3.12 environment compatible with `requirements.txt`:

```bash
python -m pip install -r requirements.txt
python -m pytest -q
python -m compileall -q .
node --check static/js/rythu-mitra-app.js
python scripts/check_frontend_contract.py
python scripts/verify_model_assets.py
python scripts/verify_model_assets.py --load-disease
python scripts/health_check.py
```

The last model-loading check requires the optional ML dependencies installed and actual trusted model files + a verified `disease_labels.json`. Do not invent the class list or infer its order from alphabetic sorting; verify the training-time class mapping.

After setting `DATA_GOV_IN_API_KEY` in the ignored local `.env` and restarting Flask, use the Markets page's live/latest action. Confirm HTTP 200, a non-empty `records` list, `status=LATEST_REPORTED`, correct Telangana filters, source URL, observation date, rupee-per-quintal unit, ordered non-negative prices and stale warning. If the provider responds with 403/429/no data, document it as BLOCKED/UNAVAILABLE rather than using sample prices.
