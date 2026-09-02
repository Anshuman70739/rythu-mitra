# Test Report

Date: 2026-08-15

## Executed

`python -m py_compile app.py backend.py train_model.py` passed.

`python -m pytest -q` passed: **15 passed in 13.43 seconds**. This includes the earlier regression coverage plus forecast/cache semantics, the no-guessed-disease-label guarantee, private farmer-record visibility, storage calculation, scheme matching, moderation, normal 404 handling, buyer-role workflow authorization, and language/voice/PWA asset checks.

The suite verifies page startup/security headers, login/dashboard authorization, CSRF, crop-input validation and model response, demo and provider-error weather paths, invalid image/type rejection, market arithmetic/records, and role authorization.

Local runtime smoke test passed: `python app.py`, `GET /health`, and `GET /` returned successfully. The health response indicated a configured weather environment variable without disclosing it. A one-time live OpenWeather verification using the configured server environment returned `LIVE` status and 8 forecast points; no credential was printed. The supplied crop model loaded with 7 input features. The supplied disease artifact loaded successfully with input `(None, 128, 128, 3)` and output `(None, 15)`; TensorFlow used CPU because no GPU driver is installed.

The service-worker implementation was reviewed to confirm that it caches only the shell and returns an explicit offline error for API calls, so cached weather is never represented as current.

Release-preparation checks also passed for the camera capture hint, equal English/Telugu translation keys, voice feature detection/fallback hooks, responsive CSS breakpoint, PWA shell/offline guard, model provenance documentation, and absence of the previously exposed weather-key value.

## Not automatically verified

Browser-device camera/speech support, actual responsive devices, external scheme links, and production HTTPS deployment require manual verification. The supplied disease model lacks a verified class mapping, so semantic disease labels cannot be tested honestly.
