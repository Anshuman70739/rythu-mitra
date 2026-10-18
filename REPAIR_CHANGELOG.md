# Targeted repair changelog

Base: `Rythu_Mitra_Master_v1_Integrated_Frontend_v2.zip` plus the separate backend v1 archive, compared before editing. Original ZIPs were left unchanged. The candidate uses the integrated v2 package because it already contains the matching frontend and modular backend; the standalone frontend remains a legacy integration foundation and is not merged into this candidate.

## Changes made

1. Implemented a direct server-side connector for the official data.gov.in / AGMARKNET daily mandi dataset (`9ef84268-d588-465a-a308-a864a43d0070`). It uses `DATA_GOV_IN_API_KEY`, filters state/district/commodity/market, validates numeric ranges and dates, and returns `LATEST_REPORTED` daily records with source metadata.
2. Kept the explicitly configured HTTPS adapter as a backwards-compatible optional provider if the official key is not configured. No synthetic price fallback was added.
3. Avoided logging provider exception tracebacks/URLs for market calls because official API keys are passed in query parameters by the provider API.
4. Updated readiness checks to consider the new official API-key configuration.
5. Fixed the frontend live-market action that previously displayed generic data cards and omitted actual price values.
6. Added English/Telugu status labels and a dedicated neutral/info badge style for `LATEST_REPORTED`.
7. Changed Flask entrypoints to bind to `0.0.0.0` by default for Codespaces port forwarding, configurable via `HOST` and `PORT`.
8. Added mocked regression tests for official provider normalization, invalid price order and missing API key behavior.
9. Added a model asset verifier that can optionally load TensorFlow model weights and compare output count with disease label count. It does not invent labels or load/unpickle the crop model.
10. Added market setup instructions, traceability, bug backlog and updated status reports.

## Not changed

- No framework migration, broad architecture rewrite, or major design refresh.
- No guessed disease labels or model retraining.
- No secret/API key or model binary was added to the archive.
- No real provider call could be made without the user's API key and due to network/package access limits in this execution environment.
- No commit, push, deployment, paid service, or official submission was performed.


## Brand refinement pass (15 October 2026)

- Rewrote generic opening copy to name crop tasks, crop-health checks, and reported mandi prices.
- Standardized feature-card icons on inline SVG symbols rather than Unicode pictographs.
- Added SVG favicon and dedicated privacy and terms pages with clear draft status and Telugu summaries.
- Added footer legal navigation and route regression tests.
- Removed smooth scrolling, scroll reveal, shimmer sweep, hover lift, and blurred glass treatment.
- Changed pill-shaped language/profile/icon controls to rectangular controls and removed em/en dashes from user-facing sources.
- Source checks passed. Flask route tests and browser/device checks remain unverified because Flask is not installed in this audit environment; see `BRAND_REFRESH_REPORT.md`.
