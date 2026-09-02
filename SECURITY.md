# Security policy and local configuration

## Configuration

Copy `.env.example` to `.env` locally and set values there. `.env` is ignored by Git. Use `OPENWEATHER_API_KEY` only on the server; it is never returned to the browser or logged. The pre-build backend contained an exposed weather key. It has been removed from source; its owner should revoke/rotate it through OpenWeather.

Use a new, strong `SECRET_KEY` for every non-demo deployment and set `SESSION_COOKIE_SECURE=1` when HTTPS is in use.

## Prototype protections

- Parameterized SQLite queries, server-side role checks, session-bound CSRF tokens, and rate limits.
- Safe input ranges and lengths, safe error responses, and no client-provided fetch URLs.
- JPEG/PNG/WebP-only crop uploads, 5 MB cap, image decoding, generated filenames, and re-encoding.
- CSP, clickjacking, MIME, referrer, and permissions-policy headers.
- Local demo passwords are intentionally documented for a college demo only; replace the demo accounts before any non-demo use.

## Reporting

Do not include secrets in an issue, screenshot, test result, or commit. For a real deployment, report vulnerabilities privately to the project owner and rotate affected credentials.
