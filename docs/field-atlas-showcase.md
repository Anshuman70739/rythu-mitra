# Field Atlas project showcase

## Purpose
A collaborator-facing introduction to the Rythu Mitra academic project, with a friendly project story and a separate deeper technical layer. This is not the daily-use farmer workspace.

## Design language
- Field Atlas palette: parchment/cream, forest green, muted sage, terracotta, restrained sky tones.
- Editorial serif headlines paired with readable sans-serif body typography.
- Illustrated Telangana-inspired landscape and purpose-built inline SVG/CSS artwork; the visuals are decorative concepts, not evidence of functioning models or mapping.
- Progressive disclosure: plain-language overview first; expand model details or turn on Technical view to inspect architecture and endpoint contracts.
- Responsive navigation, reduced-motion support, keyboard focus, an explicit motion pause button, and English/Telugu core content toggling.

## Files and responsibilities
- `templates/landing.html`: showcase homepage used by the existing root route on this experiment branch.
- `templates/rythu_mitra_field_atlas.html`: reusable source template for the Field Atlas showcase.
- `templates/landing_blue_horizon_archive.html`: preserved prior landing page from this experiment branch.
- `templates/rythu_mitra_blue_horizon_archive.html`: preserved earlier Blue Horizon workspace page.
- `templates/rythu_mitra.html`: existing app route template for the workspace; not replaced by the showcase template.
- `static/css/rythu-mitra-field-atlas.css`: theme and responsive layout.
- `static/css/rythu-mitra-field-atlas-interactions.css`: reveal and interaction styles.
- `static/js/rythu-mitra-field-atlas.js`: language toggle, navigation, Technical view, expandable details, demo walkthroughs, status dialog, motion control and interaction wiring.

## Honest status policy
- **Built in this branch**: the presentation interface and local interactive walkthrough controls.
- **DEMO / local preview**: user-entered crop-form values are validated in the browser; uploaded images can be previewed through a temporary local object URL.
- **Unavailable / unverified**: model inference and external providers are not called by this showcase.
- **Real output** may be displayed only after the actual model/provider runs successfully and its returned response is validated. Do not invent accuracy, confidence, disease classifications, live weather, market prices, scheme eligibility or impact figures.

## Future extension pattern
Add each new showcase capability as a separate section or reusable feature card. Include (1) a plain-language purpose, (2) implementation state, (3) data/model origin, (4) a demonstration or verified real workflow, (5) limitations, and (6) an integration contract. New modules should not need a complete redesign of the site shell.

## Existing backend paths recorded for future inspection
The current application has paths including `/api/session`, `/api/login`, `/api/logout`, `/api/dashboard`, `/api/weather?city=`, `/api/recommendations`, `/api/disease-scan`, `/api/records/<kind>`, `/api/market-net-income`, `/api/storage-calculation`, and `/api/schemes/matches`. This list is not a response schema and does not prove current availability. Inspect the existing Flask route handlers, CSRF/session requirements, payload limits, validation and response shapes before integration. Authentication, database, model services and routes were not rewritten for this showcase.

## Branch and deployment boundary
- All changes are confined to `experiment/dashboard-visual-masterpiece`.
- The previously approved `preview/landing-animations` and its Render service are not part of this iteration.
- `baseline/monsoon-atlas-approved` and `main` are untouched.
- Do not merge/promote the experiment without explicit approval.
