# Feature Gap Report

Comparison date: 2026-08-15. This report compares executable routes, UI behavior, storage, and tests with the master build plan; it does not restate the plan.

## COMPLETE

- Flask startup path, SQLite bootstrap, crop-recommendation model wrapper, conservative fertilizer guidance, and transparent yield-favourability estimate.
- Secure environment-based weather-key handling, request timeouts, safe provider errors, and no secret exposed to client responses.
- Basic farmer/expert/admin demo sign-in; server-side session/role checks; CSRF on state changes; parameterized storage; validation; rate limits; security headers; image type/size/decode/re-encode protections.
- Responsive product shell, semantic form labels, keyboard focus treatment, safe escaped client rendering, demo/source notices, English/Telugu preference persistence, app-shell service worker, documentation, and baseline automated tests.

## PARTIAL

- Farmer profile stores all planned data columns but has no full profile editor; the dashboard omits crop-health status, alerts, and editable quick actions.
- Crop planning uses the real crop model but did not yet expose all planning context or practical output metadata.
- Crop calendar is a static dashboard response rather than persisted/completable crop-stage tasks.
- Current weather, short forecast, rain probability, advisories, explicit cached/non-current semantics, and a credential-safe live provider check work.
- Telugu uses central JSON files and persists a preference, but only the navigation is translated; most page content remains English.
- Markets show curated records, sorting support, and net-income arithmetic, but trend/best-net detail is limited.
- Schemes have curated records, official links, and profile-based status guidance, but filtering is limited.
- Marketplace, buyer requests, equipment, storage, expert questions, and disaster reports now have role-checked basic submission workflows; lifecycle details and dedicated screens remain incomplete.
- Offline app shell is cached with an offline/retry indicator and explicit non-current API semantics, but browser-device verification remains outstanding.
- Admin summary is protected but lacks moderation/content-management screens.

## MISSING

- Verified disease-model class mapping. No mapping asset or authoritative source was supplied, so a disease name cannot be safely displayed.
- Verified/live market, scheme, equipment, storage, buyer, expert, crop-calendar, and disease-knowledge sources. Existing records are correctly labelled demo/curated.
- Production deployment, real SMS/WhatsApp, payments, insurance submission, and external marketplace communication.
- Comprehensive browser/device accessibility and mobile visual test coverage.

## BROKEN

- No currently reproducible broken core route was found in the existing automated suite.
- The pre-existing `.git` metadata remains read-only and invalid, so `git status` and local commits are unavailable.

## DEMO ONLY

- Demo accounts, dashboard crop tasks, market records, schemes, equipment, storage, buyers/FPO, expert response, disease knowledge, and fallback weather.
- The yield score and market-income calculator are reference estimates, not trained yield/profit predictions.

## NEEDS MANUAL VERIFICATION

- Camera, speech recognition/synthesis, service-worker offline behavior, and phone/tablet/laptop rendering in supported browsers.
- Official scheme links and current eligibility rules; all live/data-source integrations.
- Disease predictions after an authoritative class-label mapping is supplied.
- Production HTTPS cookies, rate-limit durability across workers, credential rotation, backup/retention policy, and a usable Git repository.
