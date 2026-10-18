# Rythu Mitra brand refinement report

Date: 15 October 2026

## Applied changes

- Replaced generic guest and dashboard headings with feature-specific farmer language.
- Replaced feature-card Unicode symbols with the existing inline SVG system and added matching simple icons for farm, soil, market, records, money, help, equipment, livestock, alerts, and settings.
- Added a project favicon at `static/favicon.svg` and referenced it from the app and legal pages.
- Changed rounded language/profile/icon controls to restrained rectangular controls. Status labels use a compact rectangular treatment; the progress meter remains rounded because it is a bar rather than a button.
- Removed smooth auto-scroll, scroll reveal effects, panel lifting, shimmer sweep and backdrop blur effects. Normal focus indicators and restrained color feedback remain.
- Removed em dash and en dash characters from user-facing template, CSS, JavaScript, and locale source. Placeholder text uses plain language.
- Added dedicated `/privacy-policy` and `/terms-and-conditions` routes with standalone responsive templates and footer navigation.
- Added bilingual high-level Telugu summaries to both legal pages. They are drafts and need fluent Telugu and legal review.
- Added `tests/test_legal_pages.py` for route and brand-regression checks.
- Added this report and `PRE_LAUNCH_BRAND_CHECKLIST.md`.

## Static checks run

- `python -m compileall -q .`: passed.
- `node --check static/js/rythu-mitra-app.js`: passed.
- JSON parsing for `en.json`, `te.json` and `resource-config.json`: passed.
- HTMLParser pass for the app, privacy page and terms page: passed.
- Inline SVG reference check: passed; no missing symbols found.
- `scripts/check_frontend_contract.py`: passed with 68 resource schemas and 613 field definitions.
- Source checks for em dash, en dash, smooth scroll, scroll-reveal animation, builder branding, favicon, legal routes and footer links: passed.

## Not verified in this environment

- Flask is not installed in the current execution environment, so `pytest` route/client tests and live Flask rendering were not run here. Run `python -m pytest -q` in the project's installed virtual environment.
- A headless Chromium preview did not complete in this environment, so no claim is made that a full visual browser test passed.
- Actual keyboard/screen-reader use, mobile device rendering and Telugu copy review still need human testing.

## Launch blockers that cannot be solved by a source ZIP alone

- No custom domain was supplied or configured. Deployment, DNS and HTTPS must be completed on the chosen host.
- The privacy/terms pages deliberately identify the operator contact as outstanding because a real legal identity and monitored contact address were not provided. Supply these before launch.
- The retention/deletion/export process needs a verified operator decision. The current code documents that complete account-deletion and full-export workflows are not available in this version.
- The Telugu legal summaries require language and legal review.
- Actual model files and a training-matched disease label mapping must be verified in the target checkout.
- Full Flask tests and live browser workflow tests must pass before release.

## Design constraints checked

No purple gradients, review/testimonial sections, customer counters, custom cursor animation, builder-branded footer, animated scroll reveals, or decorative photo assets were introduced by this change. The main app continues to use Flask/Jinja, HTML, CSS and vanilla JavaScript.
