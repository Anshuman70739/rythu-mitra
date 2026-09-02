# RYTHU MITRA — AUTONOMOUS CODEX BUILD SPECIFICATION

## VERSION
College-project full-build specification

## PROJECT
Rythu Mitra — Smart Farmer Decision Support Platform

## LOCAL PROJECT DIRECTORY
`~/crop-recommendation`

---

# 0. PURPOSE

You are the autonomous lead engineering agent for an EXISTING partially-built college project.

Your job is to take the current repository from its present state to the best practical, polished, secure, demonstrable version possible.

This is NOT a greenfield application.

The correct workflow is:

**INSPECT → UNDERSTAND → TEST → PRESERVE → REPAIR → REFACTOR → EXTEND → INTEGRATE → TEST → HARDEN → DOCUMENT → PREPARE FOR GITHUB**

Never skip the "understand the existing work" stage.

The final product must feel like a serious agriculture-technology startup/enterprise prototype while remaining honest about what is real, demo, curated, or model-generated.

---

# 1. NON-NEGOTIABLE WORKSPACE RULES

## 1.1 Allowed workspace

You may work ONLY inside:

`~/crop-recommendation`

Do not access, inspect, create, modify, delete, rename, move, or read anything outside this project directory.

## 1.2 Never touch

Do not modify:

- Windows system files
- WSL configuration
- shell configuration
- unrelated repositories
- personal files
- browser profiles/data
- SSH configuration
- system Python
- unrelated global packages
- other projects

## 1.3 No sudo

Never use `sudo`.

Prefer the existing project environment:

`~/crop-env`

Use project-local installation/configuration wherever possible.

## 1.4 Destructive operations require approval

Do not perform:

- `rm -rf`
- `git reset --hard`
- `git clean -fd`
- full repository replacement
- destructive database reset
- deleting migrations
- deleting user data
- removing a major existing feature

unless explicit approval has been obtained.

## 1.5 External actions

Never:

- deploy externally
- publish externally
- push to GitHub
- create paid services
- spend money
- access external credentials not already configured

without explicit approval.

---

# 2. AUTONOMOUS WORK MODE

The owner needs to study while the agent works.

Work autonomously through normal engineering tasks.

You may autonomously:

- inspect code
- read project files
- edit files
- create directories
- create files
- refactor code
- repair bugs
- improve UI
- improve security
- install project-local dependencies
- create local databases
- create seed/demo data
- run tests
- run the app
- debug
- lint/format
- create local Git commits
- update documentation

Do NOT repeatedly ask:

- "Should I continue?"
- "Do you want this button green?"
- "Should I run tests?"
- "Which file should I edit?"
- "Should I fix this normal error?"

Use professional judgment.

## 2.1 Critical decision rule

STOP ONLY for genuinely critical decisions:

- destructive or irreversible action
- major database migration with data-loss risk
- deleting major working functionality
- replacing the primary framework
- requiring a personal credential that is not already available/configured
- paid service
- deployment/publication
- GitHub push
- irreversible privacy/security decision
- accessing anything outside the project

When a critical decision is required, ask exactly one concise question:

> CRITICAL DECISION: [what will happen and why]
>
> Approve? [yes/no]

Do not bundle unrelated decisions into one prompt.

---

# 3. TOKEN / CONTEXT EFFICIENCY

Do not waste the user's agent usage by repeatedly asking for the same specification.

This document is the source of truth.

Prefer project files over repeated chat prompts.

Maintain these project control files:

- `BUILD_PLAN.md`
- `BUILD_PROGRESS.md`
- `PROJECT_AUDIT.md`
- `ARCHITECTURE.md`
- `TEST_REPORT.md`
- `RELEASE_CHECKLIST.md`

Update progress and reports as work proceeds.

Do not reread massive unrelated files repeatedly when focused inspection is enough.

Use the project's existing code as context rather than duplicating it into chat.

---

# 4. EXISTING PROJECT — DISCOVER FIRST

The project is already partially built.

Known components may include:

- Flask backend
- crop recommendation
- fertilizer advice
- weather integration
- yield estimation
- TensorFlow/Keras plant disease model
- `plant_disease_model.h5`

These are NOT assumptions that everything is correct.

Inspect and verify.

## 4.1 Inspect repository structure

Identify:

- backend entry points
- frontend entry points
- templates/components
- static assets
- stylesheets
- JavaScript/TypeScript
- data folders
- model folders
- uploads
- database files
- config
- environment files
- package files
- tests
- documentation
- Git configuration

## 4.2 Understand actual execution flow

Map:

User action
→ frontend
→ API/route
→ validation
→ business logic/service
→ database / ML model / external API
→ response
→ UI

Do not merely list filenames.

Understand what each important feature actually does.

## 4.3 Inspect every existing feature

For each current feature classify:

- WORKING
- PARTIALLY WORKING
- BROKEN
- MISSING
- INSECURE
- POOR UX
- NEEDS DATA
- NEEDS TESTS

Record:

- files
- dependencies
- inputs
- outputs
- current behavior
- problems
- reusable parts
- recommended action

---

# 5. EXISTING PROJECT AUDIT

Create/update:

`PROJECT_AUDIT.md`

Include:

1. Project structure
2. Technology stack
3. Existing features
4. Current routes
5. Current database/storage
6. Existing APIs
7. Existing ML models
8. Existing crop data
9. Existing frontend
10. Existing backend
11. Existing authentication
12. Existing tests
13. Existing documentation
14. Broken/incomplete parts
15. Security findings
16. UI/UX findings
17. Performance findings
18. Dependency findings
19. What should be preserved
20. What should be repaired
21. What should be refactored
22. What must be built
23. Risk assessment

Do not display actual secrets in the audit.

---

# 6. BASELINE THE EXISTING APPLICATION

Before major modifications:

## 6.1 Start the app

Use the existing environment/configuration.

Determine:

- does the backend start?
- does the frontend render?
- which routes work?
- which routes fail?
- what API calls fail?
- any import errors?
- any template errors?
- any JavaScript errors?
- any dependency problems?

## 6.2 Test existing functions

At minimum verify:

- crop recommendation
- fertilizer advice
- weather
- yield estimation
- disease-model loading/inference
- existing pages/forms
- frontend/backend communication

Do not change tests merely to hide failures.

Fix real failures.

---

# 7. OPENWEATHER / BACKEND API SECURITY AND REPAIR

The current project has an OpenWeather integration.

## 7.1 Inspect current secret handling

Find:

- API key source
- variable name
- `.env` usage
- config loader
- backend configuration
- frontend exposure

NEVER print the actual key.

If a secret exists in source:

1. remove hardcoding
2. move to environment configuration
3. create/update `.env.example`
4. ensure `.env` is ignored
5. update backend to read the environment variable
6. verify the value is available without revealing it
7. test the weather endpoint

## 7.2 Expected configuration

Use something conceptually like:

`OPENWEATHER_API_KEY=`

in `.env.example`.

The real secret stays local.

## 7.3 Fix the complete weather path

Verify:

- key loading
- API request construction
- location handling
- response parsing
- missing fields
- timeout
- network failure
- invalid location
- rate-limit response
- provider error
- backend error handling
- frontend/backend integration

A backend configuration failure should produce a safe message such as:

"Weather service is not configured."

Never expose the secret or stack trace.

## 7.4 Secret exposure check

Search the repository for likely secrets.

Report only:

- file
- variable/config name
- secret type
- exposure status

NEVER display the actual secret value.

If a key has been exposed previously, note that it should be rotated/revoked outside the repository.

---

# 8. SECURITY HARDENING — WHOLE APPLICATION

Apply defense-in-depth appropriate to a college prototype.

## 8.1 Secret management

- environment variables
- `.env`
- `.env.example`
- `.gitignore`
- no hardcoded credentials
- no secrets in frontend
- no secrets in logs
- no secrets in tests
- no secrets in docs
- no secrets in demo datasets
- no secrets in commits

## 8.2 Validation

Validate:

- types
- required fields
- string lengths
- numeric ranges
- enums
- dates
- IDs
- file types
- file sizes
- malformed payloads

## 8.3 Authentication

If authentication exists:

- strong password hashing where passwords are used
- secure sessions
- secure cookies
- sensible expiration
- logout
- protected routes

For a college prototype, a secure demo/phone login is acceptable.

Clearly label demo authentication as prototype functionality.

## 8.4 Authorization

Roles:

- farmer
- expert
- admin
- buyer/provider where required

Enforce authorization server-side.

Prevent:

- IDOR
- cross-farmer data access
- unauthorized edits
- unauthorized admin actions

## 8.5 CSRF

Protect state-changing requests where relevant.

## 8.6 XSS

Escape user content.

Never render raw user-supplied HTML.

## 8.7 SQL injection

Use ORM/parameterized queries.

Never concatenate untrusted input into SQL.

## 8.8 Upload security

For plant images and damage reports:

- size limits
- MIME validation
- extension validation
- safe generated filenames
- no executable content
- safe directory
- no user-controlled paths
- path traversal prevention
- image decoding validation
- cleanup of temporary files
- re-encoding where practical

## 8.9 Rate limiting

Apply sensible limits to:

- login
- disease scans
- expert questions
- marketplace submissions
- public API endpoints

## 8.10 HTTP security headers

Where appropriate:

- Content-Security-Policy
- X-Content-Type-Options
- Referrer-Policy
- frame protection
- HTTPS-related security when deployed over HTTPS

## 8.11 CORS

No unrestricted wildcard origin in production configuration.

## 8.12 SSRF

Do not let users provide arbitrary URLs that the server then fetches.

## 8.13 Errors

Normal users receive safe, useful error messages.

Do not expose stack traces in production responses.

## 8.14 Logging

Log useful operational events.

NEVER log:

- passwords
- API keys
- access tokens
- session secrets
- private credentials

## 8.15 Privacy

Collect only what the prototype actually needs.

Provide:

- privacy notice
- consent where appropriate
- reasonable data deletion path
- private farmer records
- no public exposure of private phone numbers

## 8.16 Dependencies

- remove unnecessary dependencies
- pin/constrain versions
- check obvious dependency risk
- do not install random packages

---

# 9. ARCHITECTURE REPAIR

Do not migrate the framework just for aesthetics.

Prefer the existing stack.

If Flask works, keep Flask.

Gradually separate concerns into:

- routes/controllers
- services
- models
- validation
- config
- security
- integrations
- ML
- utilities

Avoid:

- giant files
- giant functions
- duplicate logic
- circular dependencies
- dead code
- unused imports
- magic configuration

Create:

`ARCHITECTURE.md`

Document:

- current architecture
- target architecture
- migration decisions
- module responsibilities
- major data flows

---

# 10. DATABASE / DATA LAYER

Reuse existing data structures when good.

If no suitable database exists, SQLite is preferred for the college prototype.

Potential models:

- farmers
- farms
- crops
- crop_calendar
- crop_tasks
- weather_alerts
- market_prices
- market_locations
- government_schemes
- scheme_documents
- disease_cases
- disease_knowledge
- fertilizer_rules
- soil_records
- buyers
- buyer_requests
- equipment
- equipment_bookings
- storage_facilities
- storage_calculations
- expert_questions
- expert_answers
- disaster_reports
- notifications
- feedback
- audit_logs

Use:

- primary keys
- foreign keys
- timestamps
- created_at
- updated_at
- status
- source
- source_url
- last_updated
- data_type

Do not delete existing user/demo data during normal development.

---

# 11. DESIGN SYSTEM — PREMIUM AND CONSISTENT

The whole application must look like ONE product.

Do NOT create a different visual style for each module.

## 11.1 Product personality

- trustworthy
- natural
- agricultural
- premium
- modern
- calm
- practical
- professional
- approachable

## 11.2 Color psychology

Primary family:
- deep natural green = agriculture, growth, trust

Supporting:
- warm earth tones = soil/natural
- blue = information/weather/water
- amber/orange = attention/warning
- red = danger/urgent
- gray = supporting information

Do not make everything green.

## 11.3 Typography

- readable
- strong hierarchy
- short paragraphs
- generous line-height
- Telugu-friendly font fallback
- accessible size

## 11.4 Components

Create or improve reusable:

- Button
- Card
- StatCard
- Alert
- Badge
- StatusChip
- FormField
- Select
- Modal
- Table
- Chart
- EmptyState
- LoadingState
- ErrorState
- Toast
- SourceBadge
- LastUpdated
- ConfidenceBadge

## 11.5 UX psychology

Reduce cognitive load.

Use:

- progressive disclosure
- one primary action per card
- 3–5 important dashboard actions
- clear urgency
- clear statuses
- meaningful confirmations

The central question is:

**"What should I do today?"**

Advisories should preferably show:

- action
- reason
- timing
- source
- last updated
- data status
- confidence if model-generated

---

# 12. RESPONSIVE + ACCESSIBILITY

Mobile-first.

Support:

- phone
- tablet
- laptop

Use:

- large touch targets
- responsive cards
- responsive tables
- charts usable on small screens
- accessible forms
- mobile navigation

Accessibility:

- semantic HTML
- labels
- visible focus
- contrast
- keyboard support
- alt text
- ARIA where appropriate
- non-color status cues

---

# 13. FEATURE 1 — PERSONALIZED FARMER PROFILE + DASHBOARD

Profile should support:

- name
- language
- district
- mandal
- village
- land area
- soil type
- irrigation
- current crop
- crop stage
- previous crop
- season
- experience
- approximate budget

Dashboard should show:

- greeting
- location
- crop/stage
- weather
- today's actions
- crop-health status
- market snapshot
- schemes
- crop calendar
- alerts
- quick actions

Example:

GOOD MORNING

Location: Warangal
Crop: Cotton
Stage: Flowering

TODAY'S ACTIONS

Rain expected tomorrow
→ Delay spraying

Humidity is high
→ Inspect leaves

Nearby modal market price
→ ₹... / quintal

Today's crop task
→ Pest inspection

Possible schemes
→ 2 matches

Use "Why am I seeing this?" where useful.

---

# 14. FEATURE 2 — ENGLISH / TELUGU / VOICE

Support:

- English
- Telugu

Use centralized:

`en.json`
`te.json`

Persist the preference.

Voice where supported:

- speech-to-text
- text-to-speech
- voice search
- simple intent routing

Example intents:

- today's weather
- today's price
- what should I do today
- schemes for me

Show:

"What I heard: ..."

before important actions.

Gracefully handle unsupported browsers.

Voice is optional.

---

# 15. FEATURE 3 — CROP PLANNING

Inputs:

- location
- land size
- soil
- N/P/K if available
- pH if available
- water availability
- season
- rainfall
- previous crop
- budget
- priorities

Outputs:

- crop
- suitability score
- estimated cost
- water requirement
- duration
- risk
- reasoning
- approximate return where supported

Initial priority crops:

- Paddy
- Cotton
- Maize
- Chilli
- Tomato

Never guarantee profit.

Reuse existing crop recommendation logic/data.

---

# 16. FEATURE 4 — CROP CALENDAR

Create crop-stage tasks:

- seed treatment
- sowing
- fertilizer
- irrigation
- weed control
- pest monitoring
- disease monitoring
- flowering
- harvesting
- storage

Support:

- today's task
- upcoming task
- due
- overdue
- completed

Connect calendar to dashboard.

---

# 17. FEATURE 5 — WEATHER INTELLIGENCE

Keep the existing weather integration if it works after repair.

Display:

- temperature
- humidity
- rainfall
- rain probability
- wind
- forecast

Translate into actions:

Heavy rain:
"Consider delaying spraying."

Strong wind:
"Avoid spraying during strong winds."

High humidity:
"Inspect your crop for fungal symptoms."

Dry period:
"Check irrigation requirements."

Every advisory should expose:

- source
- last updated
- reason
- severity
- LIVE/DEMO status

Never fake live weather.

---

# 18. FEATURE 6 — PLANT DISEASE DETECTION

Use existing:

`plant_disease_model.h5`

Do not retrain/replace unless necessary.

Build:

image selection/camera
→ validation
→ preprocessing
→ model inference
→ class mapping
→ confidence
→ result
→ symptoms
→ safe preliminary guidance
→ expert verification option

Display:

"AI/model-based preliminary result. Confirm with an agriculture professional before applying treatments."

If confidence is low:

"Low confidence — expert verification recommended."

Do not fabricate confidence.

---

# 19. FEATURE 7 — SOIL + FERTILIZER

Support:

- soil profile
- NPK
- pH
- soil history
- fertilizer calculations
- nutrient history
- Soil Health Card upload/reference
- safe guidance

Clearly label demo/reference calculations.

Use assumptions transparently.

Do not invent dangerous chemical quantities.

Preserve/improve existing fertilizer functionality.

---

# 20. FEATURE 8 — MARKET INTELLIGENCE

Support:

- commodity
- market
- min price
- modal price
- max price
- date
- arrival quantity where available
- distance
- estimated transport

Calculate:

Estimated Net Income
=
Expected Selling Value
- Transport Cost
- Market Charges
- Other Expenses

Show:

- comparison
- trend
- simple chart
- nearest market
- best estimated net result

Do not guarantee profit.

Prefer live/official data if practical.
Otherwise use clearly labelled demo/curated data.

---

# 21. FEATURE 9 — BUYERS / FPO MARKETPLACE

Farmer listing:

- crop
- quantity
- quality
- expected price
- harvest date
- location
- contact/request method

Buyer request:

- crop
- quantity
- quality
- target price
- location

Support:

- search
- filters
- status
- verification
- report
- suspend/block

No payments.

Do not publicly expose sensitive phone numbers.

Clearly mark demo listings.

---

# 22. FEATURE 10 — EQUIPMENT RENTAL

Types:

- tractor
- rotavator
- harvester
- sprayer
- drone
- irrigation equipment

Show:

- provider
- location
- price
- availability
- verification

Actions:

- request booking
- booking status
- cancellation
- report

Demo records are acceptable and must be labelled.

---

# 23. FEATURE 11 — GOVERNMENT SCHEMES

Build searchable/filterable scheme records.

Potential content:

- PM-KISAN
- Crop Insurance
- Kisan Credit Card
- Soil Health Card
- Farm mechanization
- Irrigation
- Agriculture Infrastructure Fund
- Telangana schemes

For each:

- description
- eligibility
- benefits
- documents
- application steps
- official URL/source
- last updated

Use:

- Likely eligible
- Needs more information
- Check official eligibility

Never guarantee eligibility.

Never fabricate scheme rules/amounts.

---

# 24. FEATURE 12 — CROP DAMAGE / DISASTER REPORTING

Support:

- flood
- drought
- hail
- pest
- disease
- livestock
- other

Fields:

- crop
- location
- date
- affected area
- description
- image
- severity
- status

Statuses:

- Draft
- Submitted
- Under Review
- Closed

Do not claim insurance approval.

---

# 25. FEATURE 13 — STORAGE / POST-HARVEST

Support:

- storage facilities
- warehouses
- cold storage
- capacity
- location
- cost
- availability
- crop compatibility

Calculators:

- storage cost
- transport
- sell now vs store

Guidance:

- drying
- grading
- storage practices
- shelf-life where supported

Never guarantee future price increases.

Clearly mark demo facilities.

---

# 26. FEATURE 14 — EXPERT / COMMUNITY

Create:

Farmer question
→ category/crop
→ optional image
→ expert answer
→ status

Features:

- expert profiles
- verification indicator
- answer
- source
- timestamp
- helpful vote
- report
- moderation

Clearly label demo experts/responses.

Do not allow dangerous/unsupported advice to be presented as verified.

---

# 27. ADMIN DASHBOARD

Create protected admin functionality.

Show:

- farmers
- disease scans
- market searches
- scheme searches
- weather alerts
- expert questions
- disaster reports
- marketplace reports
- equipment requests
- feedback
- system status

Support:

- moderation
- data/source updates
- content management
- audit logs

Admin routes must be server-authorized.

---

# 28. NOTIFICATIONS

Create in-app notification infrastructure for:

- weather alerts
- crop tasks
- market changes
- scheme reminders
- disease warnings

If SMS/WhatsApp is not actually connected:

DO NOT claim it was sent.

Clearly identify such integrations as future work.

---

# 29. OFFLINE / WEAK INTERNET

Implement practical lightweight behavior:

- service worker/PWA if compatible
- cached app shell/static assets
- cached crop/calendar data
- cached last successful weather where safe
- offline indicator
- retry handling
- lightweight assets
- compressed images

Never present cached weather as current.

---

# 30. DEMO DATA

Where live APIs would consume too much development time, use structured demo data.

Prioritize:

- 5 Telangana-relevant crops
- multiple markets
- government schemes
- equipment
- storage
- buyers
- expert questions
- calendar tasks
- disease knowledge

Every demo record should be explicitly identifiable as demo.

The UI should show:

**Demo data — replace with live source**

when appropriate.

Never fabricate a live API response.

---

# 31. DATA SOURCE PROVENANCE

For important records, store:

- source name
- source URL
- last updated
- data type
- confidence/status

Use authoritative sources where practical, such as:

- Telangana Agriculture
- Government Farmer Portal
- eNAM
- AGMARKNET
- IMD
- ICAR
- agricultural universities
- official government scheme portals

Do not scrape random sites unnecessarily.

---

# 32. INTEGRATION — MAKE IT ONE PRODUCT

Do not leave the 14 features as disconnected pages.

Connect them.

Example:

Farmer profile
+
Cotton
+
Flowering stage
+
Weather
→ Today's Action:
"Delay spraying; inspect crop."

Crop
+
soil
+
water
+
season
→ Crop Planning

Crop
+
market prices
+
transport
→ Estimated Net Income

Farmer profile
+
land
+
crop
→ Scheme matching

Disease result
→ crop health
→ alert
→ expert verification

Calendar task
→ dashboard

---

# 33. TESTING / QA

Create and run tests.

## Backend

- startup
- routes
- validation
- authentication
- authorization
- database
- APIs
- error handling

## Disease

- valid image
- invalid image
- oversized file
- corrupted file
- low confidence
- model failure

## Weather

- valid API
- missing key
- invalid location
- timeout
- API limit
- malformed response

## Market

- filters
- sorting
- calculations
- invalid quantities
- missing values

## Schemes

- matching
- incomplete profile
- no matches
- source link

## Marketplace

- create
- update
- search
- report
- authorization

## Equipment

- booking
- cancellation
- authorization

## Disaster

- report
- image
- validation
- authorization

## Frontend

- navigation
- forms
- loading
- errors
- mobile
- tablet
- desktop
- Telugu
- English

## Security

- secret scan
- authorization
- upload security
- path traversal
- XSS-sensitive surfaces
- SQL-injection-sensitive surfaces
- CORS
- security headers
- rate limiting

Fix failures rather than merely listing them.

Create/update:

`TEST_REPORT.md`

---

# 34. PERFORMANCE

Keep the college prototype fast.

Review:

- page load
- JavaScript size
- image size
- API calls
- duplicate requests
- database queries
- model loading
- upload handling

Use caching where appropriate.

Do not add unnecessary animation.

Use lazy loading where useful.

---

# 35. FINAL UI / "PREMIUM PRODUCT" PASS

After functionality is stable, review every screen.

Fix:

- inconsistent colors
- inconsistent spacing
- poor typography
- weak hierarchy
- clutter
- poor mobile layouts
- confusing forms
- missing loading state
- missing empty state
- missing error state
- inconsistent buttons
- duplicate CSS
- placeholder text
- broken links
- console errors
- poor Telugu layout

The finished interface should feel:

**"professional agricultural technology product"**

not:

**"student project made from unrelated templates."**

---

# 36. GITHUB PREPARATION

Do NOT push.

Prepare:

- `.gitignore`
- `.env.example`
- `requirements.txt`
- `README.md`
- `SECURITY.md`
- architecture documentation
- test report
- screenshots/demo instructions

README should explain:

- problem
- solution
- features
- architecture
- stack
- setup
- environment variables
- model
- database
- demo data
- live vs demo vs curated
- testing
- security
- data sources
- limitations
- safety disclaimer
- future improvements

Scan for secrets before any GitHub push.

Local Git commits are allowed.

GitHub push requires explicit approval.

---

# 37. FINAL RELEASE CHECKLIST

Create/update:

`RELEASE_CHECKLIST.md`

Verify:

[ ] project starts
[ ] existing features still work
[ ] new features work
[ ] weather configuration works
[ ] disease model loads
[ ] database works
[ ] no secrets in tracked files
[ ] `.env` is ignored
[ ] `.env.example` is safe
[ ] uploads are safe
[ ] authentication/authorization works
[ ] demo data is labelled
[ ] live data has source/update metadata
[ ] Telugu works
[ ] English works
[ ] mobile layout works
[ ] important tests pass
[ ] README complete
[ ] Git status reviewed
[ ] GitHub not pushed yet

---

# 38. FINAL REPORT

At the end, provide:

1. What existed before the build
2. What was preserved
3. What was fixed
4. What was refactored
5. What was added
6. Complete feature list
7. Backend architecture
8. Frontend architecture
9. Database architecture
10. APIs connected
11. Model information
12. Demo data used
13. Security improvements
14. Tests performed
15. Tests passed
16. Known limitations
17. Remaining manual tasks
18. Exact run command
19. Exact test command
20. Git status
21. Whether the project is ready for GitHub push
22. Any critical approval still required

Never claim something is done unless it was actually verified.

---

# 39. MASTER EXECUTION RULE

This is the single most important instruction.

DO NOT rebuild blindly.

First understand my real existing codebase.

Then:

**PRESERVE what works.**

**REPAIR what is broken.**

**IMPROVE what is weak.**

**REFACTOR what is necessary.**

**BUILD what is missing.**

**INTEGRATE all modules.**

**TEST everything.**

**SECURE everything.**

**DOCUMENT everything.**

**PREPARE for GitHub.**

Work continuously through the roadmap.

Do not wait for me after ordinary phases.

Only stop for genuinely critical decisions.

Always work only inside:

`~/crop-recommendation`
