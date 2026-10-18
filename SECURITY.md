# Security Notes

## Implemented safeguards
- Password hashes use Werkzeug; public-user serialization is allowlisted and excludes phone and password hashes.
- CSRF is checked on state-changing API requests globally and again on protected route decorators, with same-site HttpOnly session cookies.
- Production requires a configured `SECRET_KEY` of at least 32 characters and forcibly disables demo mode.
- All `/api/` routes receive a coarse IP/account rate limit. Sensitive endpoints retain tighter per-route limits. Responses include `429` and `Retry-After` when limited. The global API guard caps query-string size and JSON request-body size, while the app-level upload cap limits multipart bodies.
- Local development uses a bounded, thread-safe in-memory sliding-window limiter. Production requires a reachable Redis service via `REDIS_URL`; the application refuses to start in production without it and rejects requests if the shared limiter becomes unavailable.
- `TRUSTED_PROXY_HOPS` is explicit and defaults to zero. Configure it only to the exact count of trusted reverse proxies so client IP rate-limits are not based on a user-supplied forwarded header.
- Role guards and owner-scoped SQL reads/updates/deletes; user-controlled `owner_id`, `role`, status, credentials and verification fields are rejected.
- Attachment references must belong to the record owner; uploads are decoded/re-encoded with random names, pixel/size checks and private storage.
- Non-sensitive audit metadata is recorded for authentication, resource writes, moderation and uploads. Rate-limit denials do not write one audit row per request, avoiding amplification.
- Security headers include nosniff, frame denial, same-origin policies, CSP `object-src 'none'`, Permissions-Policy and no-store for dynamic/private responses. HSTS is added in production when the request is known secure.

## Release-blocking items for public deployment
1. Provision Redis and set `REDIS_URL`; verify limits work across two application workers and when an instance restarts.
2. Set `APP_ENV=production`, use HTTPS, verify `SESSION_COOKIE_SECURE`, configure a generated persistent secret, use a production WSGI server, a secret manager, and restricted database/upload filesystem permissions.
3. Set `TRUSTED_PROXY_HOPS` according to the hosting provider's official proxy topology. Do not simply trust arbitrary `X-Forwarded-For` values.
4. Perform a migration rehearsal and database backup/restore test on a copy of the real database.
5. Decide the retention/deletion policy for seed packet photos, receipts, soil cards, disease photos, financial records and damage evidence; get explicit informed consent.
6. Add malware/content scanning if documents beyond re-encoded images are later permitted; set upload quotas and cleanup policies.
7. Independently penetration-test family-helper relationships, admin role changes, IDOR, rate limiting, source links and private attachment access.
8. Configure domain/host allowlisting at the deployment edge and confirm there is no unintended cross-origin API access. CORS is not enabled as a cross-origin substitute for CSRF.
9. Do not trust unreviewed `.pkl` model files; pickle loading can execute code. Obtain model artifacts only from trusted maintainers and verify hashes/provenance.

## Agricultural safety constraints
- Disease classifications are preliminary model output, not confirmed diagnosis or pesticide prescription.
- Seed image/OCR/QR and informal germination tests do not prove genuineness or official quality certification.
- Scheme matching is a possible match only, not an eligibility decision.
- Market prices, crop yields, and future storage prices are not guaranteed.
- Complaints and damage reports are local app records until the user follows an official route and independently receives an external reference.
