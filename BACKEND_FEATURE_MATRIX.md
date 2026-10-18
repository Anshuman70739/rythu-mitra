# Backend Feature Matrix — v1

Legend: **Implemented v1** means a backend endpoint/storage path exists with basic validation and access control. It does not imply full UI, official integration, or production certification. **Conditional** means a provider, model, OCR engine, data, or setup is required. **Follow-up** means specialized behavior is not yet finished.

| Area requested | Backend coverage in v1 | Status / limitations |
|---|---|---|
| Farmer account, profile, language preference | `/api/register`, `/api/login`, `/api/logout`, `/api/profile`; users table | Implemented v1; SMS/phone OTP not included |
| Multiple farms and plots | `farms`, `farm-plots` | Implemented v1 storage/CRUD |
| Digital farm diary and observation history | `farm-diary`, `farm-observations` | Implemented v1 storage/CRUD; no scheduled reminders |
| Crop plans/calendar/tasks and status | `crop-plans`, `crop-tasks`, `harvest-plans` | Implemented v1 storage/CRUD; task status is inferred from due date unless completed/skipped |
| Crop recommendations | `/api/recommendations` | Conditional on trusted `crop_model.pkl`; no fabricated fallback |
| Yield reference | `/api/yield-estimate` | Transparent rule score only; not trained yield estimate |
| Crop risk and irrigation guidance | `/api/crop-risk`, `/api/irrigation-advice`; risk, irrigation, water-source, rainwater, rotation/intercropping tables | Implemented v1 reference logic/storage; not a validated agronomic model |
| Soil tests and Soil Health Card evidence | `soil-records`, uploads, input purchases | Implemented v1 records; OCR extraction/review UI is frontend follow-up |
| Disease/pest image scan and history | `/api/disease-scan`, `/api/scan-history`, disease tables | Conditional on the model, label file and compatible preprocessing; preliminary MODEL_OUTPUT only |
| Seed packet front/back/QR/tag/receipt images | `/api/seed/scans`, private upload API | Implemented v1 evidence capture; OCR optional and requires Tesseract |
| Seed label completeness | `/api/seed/packet-check`, scan response | Implemented v1; never proves genuineness |
| Safe QR/lot comparison | `/api/seed/qr-check` | Implemented v1 text comparison and allowlisted trust indicator; URLs are not fetched and authenticity is not certified |
| Informal germination check | `/api/seed/germination`, `seed-test-results` | Implemented v1 calculator; not official lab test |
| Seed complaints and status timeline | `/api/seed/complaints`, `seed-complaint-events`, `/api/seed/escalation` | Local app record only; no government filing or authority case sync |
| Weather current/forecast | `/api/weather`, weather service | Conditional on OpenWeather key. Without it: UNAVAILABLE (or explicitly fictional DEMO when enabled). Forecast fields depend on provider response |
| Official daily mandi prices | `/api/markets?provider=live`, `services/markets.py`; stored data at `/api/markets` and `/api/markets/trend` | Direct data.gov.in / AGMARKNET connector uses server-side `DATA_GOV_IN_API_KEY`; outputs `LATEST_REPORTED` daily observations with price date/source; live smoke requires key. CSV imports remain CURATED/DEMO drafts, never silently LIVE. Historical trend still depends on stored app records. |
| Net income, sell/store, break-even | `/api/market-net-income`, `/api/storage-calculation`, `/api/finance/break-even` | Implemented v1 arithmetic only; all scenario assumptions are user-provided |
| Expenses/income/loan tracker, inventory, labour planner | `expenses`, `income`, `loans`, `inventory-items`, `input-purchases`, `labour-plans`; dashboard totals | Implemented v1 storage/summaries; no automated lender/bank integration |
| Scheme directory, possible matcher, documents/status tracking | `/api/schemes/matches`, `schemes`, `scheme-documents`, `scheme-tracking`, `benefit-tracking` | Implemented v1 possible-match records; official eligibility and applications must be verified externally |
| Crop damage/disaster/insurance records | `crop-damage-reports`, `insurance-records`, `insurance-claims`, grievance `complaints` | Implemented v1 evidence records/IDs; not an official insurance/grievance submission |
| Livestock, vaccination/health, dairy, fisheries | `livestock`, `livestock-health`, `dairy-records`, `fish-ponds`, `livestock-fish-records` | Implemented v1 records; no veterinary diagnosis/official vaccination integration |
| Harvest quality, drying, storage and booking requests | `harvest-records`, `produce-quality`, `drying-records`, `storage-facilities`, `storage-bookings` | Implemented v1 records and request storage; availability/provider validation remains manual/moderated |
| Equipment and service directory | `equipment-listings`, `equipment-bookings`, `service-directory` | Implemented v1 moderated listings/request records; no payments or live availability sync |
| Produce buyer requests, listings, group selling | `farmer-listings`, `buyer-requests`, `fpo-directory`, `fpo-groups` | Implemented v1 moderated user submissions; payment and settlement not included |
| Expert Q&A and helpful vote | `expert-questions`, `expert-answers`, `expert-votes`, content reports | Implemented v1 submit/answer/read relationship; expert accounts must be assigned by admin; no SLA guarantee |
| FPO/community and local pest/market reports | `community-posts`, `market-feedback`, `pest-reports`, `notices`, `local-alerts` | Implemented v1 moderated records; no precise public farm locations by default |
| Notifications and audit trail | notifications APIs, admin creation, audit logs | Implemented v1 in-app only; no SMS, push, or email provider |
| Trusted family-helper access | `family-helpers`, accept/revoke and scoped access to approved resources | Implemented v1 consent/scope checks; requires further security review before production |
| Offline drafts and sync | `offline-drafts`, `/api/offline/sync` idempotency | Backend sync implemented v1; actual offline storage/queue is frontend work |
| Telugu voice/read aloud | `/api/assistant/intent` recognizes basic English/Telugu intents and requires confirmation | Partial: browser voice I/O/read-aloud are frontend responsibilities, not done here |
| Admin/moderation/data freshness | `/api/admin/*`, source metadata, moderation, users, CSV drafts, health | Implemented v1 core admin APIs; full admin UI is frontend follow-up |
| Security and operational status | CSRF, hashed passwords, safe serializer, cookies/config, upload guards, rate limiting, `/health`, `/ready` | Implemented v1; rate limiting is in-memory; runtime checks still required |

## Resource CRUD pattern

For most resources, use:

- `GET /api/v1/<resource>?limit=50&offset=0&q=...`
- `POST /api/v1/<resource>`
- `GET /api/v1/<resource>/<id>`
- `PATCH /api/v1/<resource>/<id>`
- `DELETE /api/v1/<resource>/<id>` (soft delete)
- Admin moderation: `POST /api/admin/resources/<resource>/<id>/moderate`

Known resource slugs match the entries in `rythu_mitra_backend/resources.py`. Use the allowlisted fields in that file; never send `owner_id`, status, verification flags, or source metadata as ordinary user-controlled payload fields. Admin-curated source records use separate server-owned metadata fields.
