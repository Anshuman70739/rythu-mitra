# Release Checklist

- [x] Project starts locally and the health/UI smoke test succeeds.
- [x] Existing crop model, yield heuristic, and fertilizer guidance are preserved and wrapped safely.
- [x] New integrated dashboard, planning, health, market, storage comparison, schemes, service-request, voice-helper, and services UI works through tested APIs.
- [x] Weather uses environment configuration and safe demo/error handling; a credential-safe live request returned forecast data.
- [x] Disease artifact loads; its missing verified class map is disclosed.
- [x] SQLite demo database and provenance-bearing demo records work.
- [x] Hardcoded secret removed; `.env` ignored and `.env.example` is safe.
- [x] Upload controls, CSRF, session/role authorization, rate limiting, validation, and headers are implemented.
- [x] Demo data is labelled; official source links are labelled where included.
- [x] English/Telugu dictionaries, persisted preference, navigation switch, and Telugu font fallback are included.
- [x] Weather forecast/cache semantics and offline API safety were hardened; cached weather is explicitly non-current.
- [x] Disease class labels are never guessed; an optional verified mapping file is supported.
- [x] Disease artifact provenance was inspected and documented; no local authoritative class mapping exists (`MODEL_PROVENANCE.md`).
- [x] Private disaster/booking/feedback/question records are protected from anonymous cross-farmer access; moderation routes are server-authorized.
- [x] Important automated tests pass (15 total), including buyer/role, label, language/voice/PWA, storage, forecast, and moderation paths.
- [x] README, audit, architecture, security, and test report are complete.
- [x] Browser/mobile/voice/camera/PWA verification preparation is documented (`BROWSER_QA_CHECKLIST.md`); actual device pass remains manual.
- [ ] Git status / local commit: blocked by the pre-existing read-only, invalid `.git` metadata directory.
- [x] GitHub has not been pushed.

Before publishing: rotate the old exposed OpenWeather credential, set a production secret, replace demo passwords/data, supply verified disease labels, perform browser/mobile review, connect authoritative live sources, and create a usable Git repository after resolving its filesystem ownership/metadata issue.
