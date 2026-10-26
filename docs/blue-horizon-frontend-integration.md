# Blue Horizon dashboard prototype — frontend integration notes

## Scope and safety boundary
- Prototype branch: `experiment/dashboard-visual-masterpiece`.
- The existing Flask backend, route handlers, database, authentication, CSRF protection, model loading, and provider configuration are unchanged by this dashboard work.
- This branch replaces the workspace template and its front-end entry point only. The approved landing page is not edited by this prototype.
- All dashboard fixture values are explicitly illustrative. They are not live market/weather data, real farm records, real model outputs, eligibility results, or agricultural advice.
- Browser-only tasks, preferences, and notes use localStorage. They do not sync to the server and can be reset.

## Frontend architecture
- View rendering: `static/js/rythu-mitra-visual-prototype.js` page render functions (`home`, `cropPage`, `healthPage`, `weatherPage`, `marketsPage`, `calendarPage`, `financePage`, `schemesPage`, `recordsPage`, `settingsPage`).
- UI state: the `state` object; local demo persistence functions are kept separate from render functions.
- API boundary: `apiClient` and `ENDPOINTS` document future calls. Requests deliberately return `unavailable` without sending network requests in this phase.
- Styles and responsive behavior: `static/css/rythu-mitra-visual-prototype.css`.
- Accessibility: keyboard focus states, skip link, labelled controls, ARIA state for task toggles, reduced-motion media query, visible pause/resume control, touch-sized controls, and responsive bottom navigation.

## Existing backend contract to preserve for later integration
The current app has these established API paths (do not infer response schemas from this list; inspect the actual route handlers before wiring):
| Frontend concern | Existing endpoint |
| --- | --- |
| Session state | `GET /api/session` |
| Sign in | `POST /api/login` |
| Sign out | `POST /api/logout` |
| Dashboard | `GET /api/dashboard` |
| Weather | `GET /api/weather?city=` |
| Crop recommendations | `POST /api/recommendations` |
| Crop health scan | `POST /api/disease-scan` |
| Farm records | `/api/records/<kind>` |
| Market net income | `POST /api/market-net-income` |
| Storage calculation | `POST /api/storage-calculation` |
| Scheme matches | `POST /api/schemes/matches` |

Authentication and security behavior remain owned by the current Flask backend. Existing route handlers should be read before wiring the API client; preserve required session cookies, CSRF headers/tokens, validation, and error response formats. Never place credentials or secrets in client-side JavaScript.

## Integration state model
When wiring actual APIs, keep these states distinct:
- `loading`: request in progress; render a skeleton or progress state.
- `unavailable`: no provider/model is configured or endpoint integration is intentionally disabled.
- `error`: request failed; show a recoverable error without inventing data.
- `demo`: explicit fixture or UI-only result; must carry a visible DEMO label.
- `real`: only after a successful, validated response from the real endpoint/model; show source, timestamp, unit and confidence/limitations where applicable.

Never silently fall back from an API error to a fixture while labelling it real. Do not label an output as real model inference unless a model was actually called and the returned result was validated.

## Known prototype limitations
- Sign-in is a preview dialog only. It does not authenticate, create accounts, or submit credentials.
- Crop recommendation form validates browser inputs but does not call a crop model.
- Crop image upload uses a temporary local object URL only; it does not upload or diagnose the image.
- Weather and market charts are sample fixtures.
- The yield/income calculator performs local arithmetic from user-entered assumptions; it is not a yield prediction model.
- Scheme cards are placeholders and do not determine eligibility.
- No backend, model, market, weather, or scheme API is called from this prototype.

## Preview
A separate Render service is configured for this branch so the approved landing-page preview remains separate. Do not merge or change the approved preview/main branch until the user explicitly approves.
