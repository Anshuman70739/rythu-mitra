# Rythu Mitra bug backlog — repaired candidate

Severity: P0 = critical, P1 = high, P2 = medium, P3 = low. Statuses describe the supplied candidate, not an unknown remote checkout.

| ID | Severity | Issue | Status | Evidence / required action |
|---|---|---|---|---|
| RM-001 | P1 | Full pytest/API integration suite cannot be verified in this review environment | BLOCKED | `python -m pytest -q` stopped at `ModuleNotFoundError: flask`; package index DNS was unavailable. Run inside the Codespace with requirements installed. |
| RM-002 | P1 | Model artifacts are not included in the integrated candidate ZIP | BLOCKED / environment-specific | `scripts/verify_model_assets.py` reports crop model, disease model and label bundle missing. The user reports model files exist in GitHub; preserve the active checkout's binaries and run the verifier there. |
| RM-003 | P1 | Disease model weights require a verified class label mapping and training-compatible preprocessing | OPEN | Do not infer label order. Add/verify `data/disease_labels.json` from the actual training provenance; run `python scripts/verify_model_assets.py --load-disease` with ML dependencies. |
| RM-004 | P1 | Real official market API cannot be exercised without the user's own data.gov.in key | IMPLEMENTED, LIVE SMOKE BLOCKED | Direct adapter and mocked regression tests added. Configure `DATA_GOV_IN_API_KEY` in ignored `.env`, then run live smoke test. |
| RM-005 | P2 | Live market action previously showed generic cards without price values | FIXED | `searchLiveMarkets()` now renders commodity, market, state/district, price date, min/modal/max, staleness, source and fetch metadata. |
| RM-006 | P2 | Codespaces entrypoints bound to loopback only | FIXED | `run.py` and compatibility `backend.py` now bind to `HOST` (default `0.0.0.0`) and `PORT` (default `5000`). Verify forwarded port in real Codespace. |
| RM-007 | P2 | Market status could imply instant live prices | FIXED IN CONNECTOR/UI | Official daily records use `LATEST_REPORTED`; the source and observation date are shown. This must not be changed to “real-time”. |
| RM-008 | P2 | Market fallback/provider exception logging could risk exposing a URL containing query parameters | FIXED IN CONNECTOR | Exceptions are logged by type rather than full traceback/URL for market calls. Still review deployment-wide logs. |
| RM-009 | P2 | No persistent cache/fallback for the official market endpoint | OPEN / optional | The connector returns `UNAVAILABLE` on provider failure. Any future cache must preserve timestamps and label old rows `CACHED`/stale. |
| RM-010 | P2 | Official daily endpoint is not a historical trend database | DOCUMENTED LIMITATION | Trend view reads stored app market records. A separate verified history acquisition strategy would require explicit scope and data-retention approval. |
| RM-011 | P2 | Full mobile, keyboard, screen-reader, Telugu overflow and slow-network behavior is unverified | OPEN | Run browser/device checklist and get a native Telugu reader to review core terminology. |
| RM-012 | P2 | In-memory rate limiter and SQLite suitability are limited for multi-worker production | OPEN | Acceptable for controlled prototype only; production requires shared rate limiting, backups, monitoring and operational review. |
| RM-013 | P3 | Large single-file frontend JS couples multiple workflows | OPEN / deferred | Do not rewrite just for style. Consider module split only after integration is stable and with user approval. |

No claim is made that P1 blockers are resolved. Release readiness remains BLOCKED until RM-001 to RM-004 are verified in the actual environment and high-severity checks pass.
