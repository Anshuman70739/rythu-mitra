# Rythu Mitra: Complete Setup, Run, Test and Hosting Guide

This guide is written for a beginner using **GitHub Codespaces + VS Code**. Commands are intended for the **Bash terminal inside the Codespace**, unless a step says otherwise.

It covers opening the Codespace, uploading and extracting `RythuMitra.zip`, installing dependencies, configuring the app, locating model assets, running tests, starting Flask, opening the site, testing core workflows, safely preparing GitHub changes, and requirements for public hosting.

> **Important:** This ZIP is a separate copy of the integrated project. Do not extract it over your existing `/workspaces/rythu-mitra` folder. Test it separately first. The ZIP does not include trained model weights or disease labels. No deployment, custom domain or live market API credential is included.

---

## Before you begin: what you need

Required:

1. Access to the GitHub account that can open your Rythu Mitra Codespace.
2. A working internet connection for downloading the ZIP and Python packages.
3. The ZIP downloaded from this conversation, named `RythuMitra.zip`.
4. Python 3.12 available in the Codespace (the earlier Codespace screenshot showed Python 3.12.3).
5. A web browser.

Useful but optional:

- VS Code desktop, although VS Code in the browser also works.
- Node.js for checking JavaScript syntax.
- The trusted trained crop/disease model files from your original repository.
- Data.gov.in and weather-provider credentials, if you want those external services to return live data.

You do **not** need to install Python, Git or VS Code again if they are already available in your Codespace. A Codespace is a remote Linux computer. Its terminal is not the same as Windows Command Prompt.

## The basic plan

1. Download the ZIP to your computer.
2. Open the existing Codespace.
3. Upload the ZIP and move it outside the original repository.
4. Extract the project into a separate folder.
5. Create a Python virtual environment and install packages.
6. Create a private local `.env` file.
7. Check the source, run automated tests and verify model assets.
8. Start Flask and open port 5000 in a browser.
9. Exercise the actual website and record failures honestly.
10. Only after testing, plan how to merge into GitHub and deploy publicly.

---

# Part 1. Download the ZIP and open Codespaces

## Step 1. Download the project

1. Click the `RythuMitra.zip` download link provided in this conversation.
2. If your browser asks where to save it, choose the Downloads folder.
3. Do not rename files inside the ZIP and do not extract it over your original project.
4. Keep this browser tab open so you can return to the download if necessary.

## Step 2. Open the correct GitHub repository

1. Open GitHub in your browser and sign in.
2. Open your Rythu Mitra repository. The previous repository URL used in this project was `https://github.com/Anshumanpadhi74/rythu-mitra`.
3. If the repository page opens normally, you are in the right place. If GitHub says you do not have access, confirm you are logged in to the account that accepted the collaborator invitation.

## Step 3. Open your Codespace

1. On the repository page, click the green **Code** button.
2. Select the **Codespaces** tab.
3. Click the Codespace you already use. If it is stopped, start it and wait for VS Code to finish loading.
4. Check the left Explorer panel. It should show your repository files.
5. From the top menu select **Terminal → New Terminal**.

A terminal panel will open at the bottom of the VS Code window. Commands in this guide go there, not into the browser address bar and not into a Python source file.

## Step 4. Confirm where the terminal is

Type this and press Enter:

```bash
pwd
```

The original repository has previously appeared as:

```text
/workspaces/rythu-mitra
```

Now type:

```bash
ls -la
```

You should see your existing files. If the directory differs, use the real path displayed by `pwd` in the following commands.

## Step 5. Check Git status before doing anything

Run:

```bash
git status --short
```

This shows changes already made in your original repository. If there are changes you care about, do not discard them. The instructions below keep the new candidate separate so they should not alter these files.

---

# Part 2. Upload and extract `RythuMitra.zip` safely

## Step 6. Upload the ZIP to the Codespace

The ZIP is on your computer, but the Codespace is a remote computer, so it must be uploaded first.

In VS Code:

1. Open the Explorer on the left.
2. Right-click the top-level `rythu-mitra` folder, or use the Explorer's **Upload** option if it appears.
3. Choose `RythuMitra.zip` from your computer's Downloads folder.
4. Wait for upload to finish.

If you are using VS Code in a browser and do not see an Upload option, you can try dragging the ZIP from your local file manager into the Explorer. If neither option is available, use the upload feature offered by your Codespaces interface or tell your helper that the ZIP upload step is blocked; do not paste ZIP contents into the terminal.

## Step 7. Move the ZIP outside the Git repository

This avoids accidentally staging the ZIP itself as a project file.

In the terminal, run:

```bash
ls -lh /workspaces/rythu-mitra/RythuMitra.zip
```

If that confirms the ZIP is in the repository root, move it one directory above the repository:

```bash
mv /workspaces/rythu-mitra/RythuMitra.zip /workspaces/RythuMitra.zip
```

If `ls` says the file cannot be found, locate the ZIP in the Explorer. Use its actual path in the `mv` command. Do not run `mv` repeatedly after it has already moved.

Verify it is now outside the repository:

```bash
ls -lh /workspaces/RythuMitra.zip
```

You should see the filename and a file size.

## Step 8. Install extraction and virtual-environment support if needed

First check the tools already available:

```bash
python3.12 --version
unzip -v | head -n 2
```

If `python3.12` is not found, check:

```bash
python3 --version
```

Prefer Python 3.12 for this dependency set. If `unzip` or Python virtual-environment support is missing, run:

```bash
sudo apt-get update
sudo apt-get install -y unzip python3.12-venv
```

Wait for these commands to complete. This installs operating-system support in the Codespace; it does not install the project's Python libraries.

If `apt-get` fails due to a repository, network or DNS error, save the full error and stop here. Do not uninstall Python or try random version changes.

## Step 9. Extract into a separate folder

Create the destination folder:

```bash
mkdir -p /workspaces/rythu-mitra-candidate
```

Extract the ZIP into it:

```bash
unzip -q /workspaces/RythuMitra.zip -d /workspaces/rythu-mitra-candidate
```

Now list the folder:

```bash
ls -la /workspaces/rythu-mitra-candidate
```

You should see a folder named `RythuMitra`.

Enter the candidate project:

```bash
cd /workspaces/rythu-mitra-candidate/RythuMitra
```

Confirm the path:

```bash
pwd
```

It should end with:

```text
/workspaces/rythu-mitra-candidate/RythuMitra
```

List the project files:

```bash
ls -la
```

Important files include `run.py`, `backend.py`, `requirements.txt`, `requirements-ml.txt`, `rythu_mitra_backend/`, `templates/`, `static/`, `scripts/` and `tests/`.

If `run.py` is not listed, do not continue. Find its actual location with:

```bash
find /workspaces/rythu-mitra-candidate -maxdepth 4 -name run.py -print
```

Then change directory to the folder containing `run.py`.

---

# Part 3. Create the Python environment and install packages

## Step 10. Create a virtual environment

Make sure your terminal is in the folder containing `run.py`. Type:

```bash
python3.12 -m venv .venv
```

This creates a private Python environment for the candidate project. It prevents its libraries from being mixed with other projects.

If this command succeeds, activate it:

```bash
source .venv/bin/activate
```

The beginning of the terminal prompt should display `(.venv)`.

Confirm the active interpreter:

```bash
python --version
which python
```

`python --version` should show Python 3.12.x. `which python` should point into `/workspaces/rythu-mitra-candidate/RythuMitra/.venv/`.

### If creating the environment says `ensurepip is not available`

Run the system support installation from Step 8:

```bash
sudo apt-get update
sudo apt-get install -y python3.12-venv
```

Then retry Step 10. Do not remove the original repository's `.venv` or rename it.

## Step 11. Upgrade pip

With `(.venv)` showing in the prompt, run:

```bash
python -m pip install --upgrade pip
```

Wait until the command finishes. If you see DNS resolution or network errors, package download access is blocked. That is an installation blocker; it is not a successful install.

## Step 12. Install the base dependencies

Run:

```bash
python -m pip install -r requirements.txt
```

The base requirements include Flask, requests, Pillow, NumPy, scikit-learn, pytest and Redis client support. TensorFlow is deliberately separate because it is large and is only required when testing the disease model.

Wait for the shell prompt to return. If installation ends in red error text, keep the last 20 lines and resolve the dependency problem before running the app.

Verify dependency consistency:

```bash
python -m pip check
```

Expected outcome: `No broken requirements found.` If it reports conflicts, record and fix them before treating the environment as ready.

---

# Part 4. Configure local settings without leaking secrets

## Step 13. Create the local `.env` file

From the candidate project root, run:

```bash
cp .env.example .env
```

In the VS Code Explorer, open the new `.env` file. If hidden files are not visible, use the Explorer menu to show hidden files, or open it through **File → Open File** and enter the candidate path.

A `.env` file stores local settings. Never paste it into chat or commit it to GitHub.

## Step 14. Generate a private development secret

In the terminal, run:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

The terminal prints a long random string. Copy the output directly into your `.env` file after `SECRET_KEY=`. This secret is private; do not send it to anyone.

For local development, check that these values are set:

```dotenv
APP_ENV=development
DEMO_MODE=false
SECRET_KEY=PASTE_YOUR_GENERATED_VALUE_HERE
REDIS_URL=
SESSION_COOKIE_SECURE=false
```

Replace `PASTE_YOUR_GENERATED_VALUE_HERE` with the generated value. It is a placeholder in this example, not a value to use literally. Keep `SESSION_COOKIE_SECURE=false` only for local HTTP development. Production must use HTTPS and secure cookies.

Save with **Ctrl+S**.

Leave `DATA_GOV_IN_API_KEY` and `OPENWEATHER_API_KEY` blank until you have valid provider credentials. Do not add sample credentials to simulate success.

The local single-process rate limiter is suitable for local tests. Public multi-worker deployment must use a reachable Redis service and `REDIS_URL`.

---

# Part 5. Check the project before starting it

All commands in this part are typed in the candidate project's terminal, with `.venv` activated.

## Step 15. Compile Python files

```bash
python -m compileall -q .
```

No output normally means the Python source files passed compilation. It does not prove runtime imports or routes work.

## Step 16. Check JavaScript syntax

First check Node.js:

```bash
node --version
```

If a Node version appears, run:

```bash
node --check static/js/rythu-mitra-app.js
```

No output and an exit code of zero indicate JavaScript syntax passed. If `node` is not found, mark this check blocked and install a supported Node.js version in the Codespace before claiming it passed.

## Step 17. Check the frontend/backend contract

```bash
python scripts/check_frontend_contract.py
```

The script checks required API markers, resource definitions, language JSON, CSRF markers and the market connector. Read the result. It is a static check; it does not replace live API testing.

## Step 18. Run the complete Python test suite

```bash
python -m pytest -q
```

Wait for a result such as `passed`, `failed`, or `errors`. Save the complete output.

- If all tests pass, record the count and continue.
- If tests fail, keep the failing test name and traceback. Do not delete a failing test or loosen its assertion just to get a green result.
- If an import error says Flask or another dependency is missing, return to Step 12 and fix installation.

## Step 19. Check health, database and integrations

```bash
python scripts/health_check.py
```

This starts a test app, calls health/readiness endpoints and reports the database, upload directory, model files and external-service configuration. It may create local database/storage files according to app configuration. It does not prove that a live provider or ML prediction is accurate.

## Step 20. Check model assets

```bash
python scripts/verify_model_assets.py
```

The ZIP does not include trained model weights. If the script reports models missing, follow Part 6 before claiming model-backed features work.

---

# Part 6. Locate and copy the trusted model files

## Step 21. Search the original repository

Open a second terminal in VS Code using **Terminal → New Terminal**. This second terminal lets you inspect the original project without stopping or changing the candidate.

Run:

```bash
find /workspaces/rythu-mitra -maxdepth 5 -type f \( -name 'crop_model.pkl' -o -name 'plant_disease_model.h5' -o -name 'disease_labels.json' \) -print
```

This command only searches. It does not modify files. Record the exact paths it prints.

## Step 22. Copy only confirmed model files

Return to the candidate terminal and make the expected folders:

```bash
mkdir -p models data
```

If and only if the search output shows that the files are in the original repository root, these commands copy them:

```bash
cp /workspaces/rythu-mitra/crop_model.pkl models/
cp /workspaces/rythu-mitra/plant_disease_model.h5 models/
```

If the paths differ, use the paths actually reported by `find`; do not run these sample commands blindly.

If the search found `disease_labels.json`, copy it to the candidate `data/` folder using its exact path, for example:

```bash
cp /actual/path/from/find/disease_labels.json data/
```

Replace `/actual/path/from/find/disease_labels.json` with the path actually returned by the search. Do not paste that example path literally.

**Critical:** A disease-label file must match the model's training class order. Do not invent labels, sort them alphabetically, or assume a mapping. If no verified label file exists, disease detection must remain unavailable until the correct mapping is recovered from training materials.

Only load a pickle model if it comes from the trusted project repository and its origin has been verified. Python pickle files can execute code when loaded.

## Step 23. Install TensorFlow only for disease-model testing

With the candidate `.venv` active, run:

```bash
python -m pip install -r requirements-ml.txt
```

TensorFlow can be large, so allow time for download and installation. If package resolution fails for the current Python/platform combination, save the full error; do not change the training model or claim the model works.

Then run:

```bash
python scripts/verify_model_assets.py --load-disease
```

This tries to load the disease model and compare output dimensions with the label list. A pass does not alone validate the class meanings, training preprocessing, or accuracy on real farms.

---

# Part 7. Start Flask and open the website

## Step 24. Start the app

Return to the candidate terminal. Confirm it is in the `RythuMitra` project directory and shows `(.venv)`.

Run:

```bash
python run.py
```

If startup succeeds, the terminal displays a Flask server message, typically showing port 5000. Keep this terminal open. The server stops if you close this terminal or press **Ctrl+C**.

If startup fails, copy the complete traceback and fix the actual error before proceeding.

## Step 25. Forward port 5000 in Codespaces

1. In VS Code's bottom panel, click **Ports**.
2. If Ports is hidden, open `Ctrl+Shift+P` and search for **Ports: Focus on Ports View**.
3. In the Ports panel, choose **Forward a Port** if port 5000 is not already listed.
4. Enter `5000` and confirm.
5. Click the globe/open-in-browser icon beside port 5000.
6. A Codespaces-forwarded HTTPS URL should open in the browser.

Use the URL Codespaces gives you. `http://127.0.0.1:5000` inside the Codespace terminal points to the app in that Codespace, but when typed in your personal laptop's browser it points to the laptop itself, not the remote Codespace.

## Step 26. Test health endpoints

Keep Flask running in the first terminal. Open a **second** terminal, then enter the candidate project folder and activate the environment:

```bash
cd /workspaces/rythu-mitra-candidate/RythuMitra
source .venv/bin/activate
```

Call the local endpoints:

```bash
curl -i http://127.0.0.1:5000/health
curl -i http://127.0.0.1:5000/ready
```

Review the HTTP status and JSON body. A healthy service does not mean each optional integration has been configured. Missing model/provider states must remain visible.

---

# Part 8. Real website test checklist

Open the forwarded site URL. Use the browser's developer tools if available: press **F12**, choose **Console** to inspect JavaScript errors and **Network** to inspect failed HTTP requests. Do not share cookies, authorization headers, API keys or private farmer data in screenshots.

For every test, record PASS only when you actually performed it. Otherwise use FAIL, BLOCKED or UNVERIFIED.

## A. Homepage and navigation

1. Load the homepage in a new tab.
2. Confirm the CSS and JavaScript load; the page must not be blank.
3. Open Console and look for red errors.
4. Resize the browser to 320, 360, 375, 390, 560, 600, 768, 1024 and 1440 pixels.
5. Confirm there is no horizontal page scroll and no fixed navigation covering a button.
6. Test both English and Telugu. Verify text wraps instead of being clipped.
7. Click every primary navigation item. Confirm it opens the expected workspace.
8. Refresh the browser and use Back/Forward. Confirm navigation does not break.

## B. Authentication and roles

1. Register a test farmer using non-sensitive test information.
2. Check a valid registration and a duplicate phone/account response.
3. Sign in, refresh the page, and confirm the session behaves consistently.
4. Sign out and try a protected action. It must require authentication.
5. If role-specific accounts are supported, verify a farmer cannot open admin controls.
6. Create two test farmers and create private records for both. Check that changing a record identifier cannot expose the other farmer's information.
7. Do not use real farmer information while testing.

## C. Crop recommendation

1. Enter valid N, P, K, temperature, humidity, pH and rainfall values.
2. Submit and confirm the UI waits for the backend response.
3. Check that the response is marked as model output and that any limitations are visible.
4. Try missing values, text instead of numbers, negative nutrient values and impossible pH input.
5. If the model is missing, the app must say unavailable. It must not display a fabricated successful recommendation.

## D. Disease detection

1. Confirm model weights and verified label mapping exist first.
2. Upload a valid JPEG/PNG/WebP leaf image.
3. Confirm the request finishes and shows a preliminary result, status and confidence only when the model produces a valid probability distribution.
4. Try an empty file, an unsupported file, a corrupted image and an image above the configured size limit.
5. Confirm unsafe/invalid uploads are rejected with a human-readable message.
6. Confirm results do not claim a confirmed diagnosis or guarantee a treatment.
7. If weights/labels are missing or inference fails, the screen must show unavailable. Record it as BLOCKED, not PASS.

## E. Weather and mandi prices

1. Without an API key, check that weather/market show an honest unavailable/configuration state.
2. With a valid provider key configured, check a valid location or commodity/market.
3. Confirm market results have the commodity, market name, reported price date, source and min/modal/max values when available.
4. Remember this is a daily reported mandi dataset, not tick-by-tick pricing and not necessarily the farm-gate price.
5. Test invalid location, no matching market, missing key and provider timeout where practical.
6. Never represent cached or demo data as currently live.

## F. Market calculations and storage

1. Enter quantity and price with the visible units.
2. Enter transportation and other charges.
3. Verify the result with a hand calculation.
4. Change one input and confirm the result changes.
5. Try zero, negative and very large values.
6. Confirm the page says estimate/reference, not guaranteed profit.

## G. Security smoke checks on your own local instance

1. Test write requests with and without a valid CSRF token using the provided automated tests or browser workflow. Missing/invalid CSRF should be rejected.
2. Check that requests over the configured limit receive HTTP 429 and a `Retry-After` header. Use the automated suite instead of flooding the app.
3. Test unauthenticated access to private records and wrong-role access to admin functions.
4. Test file-size limits, invalid content types and corrupt image files.
5. Confirm secrets are not returned by API responses or printed into client-side JavaScript.
6. Confirm normal error pages do not reveal stack traces, secret values or private filesystem paths.

Only test your own local/Codespaces deployment. Do not run exploit tests against other websites or external services.

## H. Accessibility and design

1. Navigate using Tab and Shift+Tab only.
2. Confirm the keyboard focus is visible and moves in a logical order.
3. Confirm form fields have labels and validation errors are understandable.
4. Use browser zoom at 200% and inspect content overflow.
5. Check mobile viewport widths and Telugu text wrapping.
6. Check the homepage for vague copy, decorative symbols used as icons, fake metrics, fake testimonials, unwanted gradients and distracting motion.
7. Test `/privacy-policy` and `/terms-and-conditions` directly.

---

# Part 9. Configure real provider data

## Daily mandi prices (data.gov.in / AGMARKNET)

1. Visit https://www.data.gov.in/ and sign in or create an account following the portal's current process.
2. Find the official resource for current daily prices for commodities and markets/mandis.
3. Follow the portal's instructions to obtain an API key.
4. In the candidate `.env` file, set `DATA_GOV_IN_API_KEY` to the key. Never place it in JavaScript, HTML or GitHub.
5. Restart Flask after changing `.env`.
6. Test the market page and confirm the reported date and source. The UI should label data as latest reported daily data.
7. If the provider returns an error or no matching data, the site must show unavailable rather than making up a price.

## Weather

1. Choose and register with the weather provider used by your backend.
2. Add the private key to `OPENWEATHER_API_KEY` in `.env`.
3. Restart Flask.
4. Test both a valid location and provider failure. A missing key or timeout must not create a fabricated live result.

---

# Part 10. Keep your original GitHub project safe

The extracted candidate folder is a separate folder, not your original Git repository. **Do not run `git push` from the extracted candidate folder.** Do not copy the entire candidate over the original project before review because the backend architecture differs and important model assets, labels or datasets may need to be preserved.

After candidate tests pass:

1. Open the original repository and make sure any existing work is committed or backed up.
2. Create a separate branch in the original repository for integration. For example, from the original repo terminal:

   ```bash
   cd /workspaces/rythu-mitra
   git status --short
   git switch -c integration/rythu-mitra-candidate
   ```

3. Review the current branch and candidate side-by-side. Reconcile routes, models, labels, data, migrations, settings and templates intentionally. Do not overwrite files merely because they have matching names.
4. Copy only the agreed files into the original Git repository.
5. Review changes:

   ```bash
   git status --short
   git diff --stat
   git diff
   ```

6. Verify `.env`, credentials, database files, private uploads and farmer evidence are not staged. If they appear, stop and remove them from staging before committing.
7. Run tests again inside the branch. Only stage the intended source and documentation files.
8. Commit and push the branch after review. Merge into `main` only when tests and integration checks pass.

Never force push or reset the original branch to make the candidate fit.

---

# Part 11. Prepare for actual public hosting

A Codespaces-forwarded link is a development/testing URL, not a permanent public hosting arrangement. Public hosting is a separate task and should not begin until local tests and essential workflows pass.

## Required before deploying

- Choose a hosting provider that supports Python/Flask and the required Python version.
- Confirm the host supports the CPU/RAM needed for TensorFlow disease inference if that runs on the server.
- Configure a strong persistent `SECRET_KEY` using the host's secret manager.
- Set `APP_ENV=production` and keep Flask debug mode off.
- Provision reachable Redis and set `REDIS_URL`; production startup deliberately refuses to run without the shared rate limiter.
- Set `TRUSTED_PROXY_HOPS` only to the exact value in the host's documented proxy topology.
- Configure HTTPS and secure cookies.
- Set API keys only in the host's private environment/secrets manager.
- Decide on persistent database and upload storage. This candidate uses SQLite; its current backend rejects non-SQLite database URLs. Do not deploy to ephemeral storage if farmer records/uploads must persist. If your host requires PostgreSQL, a deliberate database migration is a separate engineering change.
- Configure backup, restore, log access and data-retention procedures.
- Verify privacy policy wording, terms, owner/contact details and the actual collection/retention behavior.
- Purchase or use your chosen custom domain, configure DNS and wait for TLS certificate provisioning.
- Test the final domain over HTTPS, authentication, uploads, rate limits, backups and all core workflows.
- Complete security, privacy and accessibility review. Do not launch while critical/high issues or untested core workflows remain.

## Do not do these things

- Do not commit `.env`.
- Do not use a guessed or example API key.
- Do not claim disease detection works without the verified model and class labels.
- Do not claim mandi prices are instant when the source is daily reports.
- Do not mark tests as passed because the page merely opens.
- Do not use the Codespaces URL as your permanent public domain.
- Do not put actual farmer records or private crop images into test fixtures or public issue reports.

---

# Final test record

After completing the steps, record the actual result for each item:

| Check | Status | Evidence / notes |
|---|---|---|
| Python dependencies installed | PASS / FAIL / BLOCKED | |
| `pip check` | PASS / FAIL | |
| Python compile | PASS / FAIL | |
| JavaScript syntax | PASS / FAIL / BLOCKED | |
| Frontend contract script | PASS / FAIL | |
| `pytest` | PASS / FAIL / BLOCKED | |
| Health/readiness script | PASS / FAIL | |
| Homepage opens | PASS / FAIL | |
| Registration and login | PASS / FAIL | |
| Two-user privacy check | PASS / FAIL | |
| Crop model | PASS / BLOCKED / FAIL | |
| Disease model and labels | PASS / BLOCKED / FAIL | |
| Weather provider | PASS / UNAVAILABLE / BLOCKED | |
| Official mandi provider | PASS / UNAVAILABLE / BLOCKED | |
| CSRF and rate limit | PASS / FAIL | |
| Mobile widths and Telugu | PASS / FAIL | |
| Privacy and terms pages | PASS / FAIL | |
| Production configuration | NOT STARTED / PASS / FAIL | |
| Custom domain and HTTPS | NOT STARTED / PASS / FAIL | |

The app may be suitable for continued development when local startup works, but it is not production-ready until the tests, models, live providers, storage, security configuration and hosting checks have actual evidence.
