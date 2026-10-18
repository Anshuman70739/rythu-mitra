# Rythu Mitra — run and verify the integrated project

This guide matches the code currently stored in `https://github.com/Anshuman70739/rythu-mitra`, on the `main` branch.

**Important:** The frontend, Flask backend, tests, documentation and model weight files are already integrated into this repository. Do not upload the old ZIP, extract a bundle over the repository, or repeat the pull-request merge. The remaining work is to install dependencies in a development environment, run the app, and verify real browser workflows.

## 1. Open the correct repository and Codespace

1. Open [the Rythu Mitra repository](https://github.com/Anshuman70739/rythu-mitra) and sign in to an account that can access it.
2. Click **Code → Codespaces**.
3. Open your existing Codespace for this repository. If you create a new one, choose the `main` branch.
4. In VS Code, choose **Terminal → New Terminal**.
5. Check the current directory and branch:

   ```bash
   pwd
   git branch --show-current
   git status --short
   ```

If `git status --short` shows local changes, preserve or commit them before changing branches. Do not discard work just to get a clean status.

If the working tree is clean, sync the current branch:

```bash
git switch main
git pull origin main
```

Confirm the updated project files exist:

```bash
test -f run.py && test -f backend.py && test -f requirements.txt
test -f templates/rythu_mitra.html
test -f static/js/rythu-mitra-app.js
ls -lh models/crop_model.pkl models/plant_disease_model.h5
```

Run these commands from the repository root. Do not create a second extracted candidate folder for the merged repository.

## 2. Create a Python environment

Check for Python 3.12:

```bash
python3.12 --version
```

Create the virtual environment only if it does not already exist, then activate it:

```bash
if [ ! -d .venv ]; then python3.12 -m venv .venv; fi
source .venv/bin/activate
python --version
```

Install the project dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip check
```

Wait for each command to finish. If dependency installation reports a network/DNS error or a red error message, it has not succeeded. Do not change package versions at random; retain the full error text for troubleshooting.

## 3. Configure local environment settings

Create a local `.env` file only if one does not already exist:

```bash
[ -f .env ] || cp .env.example .env
```

Generate a private development secret:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Open `.env` in VS Code and set `SECRET_KEY=` to the generated string. Save the file. Keep `.env` private and never commit it or paste its contents into a chat, issue, or screenshot.

For local HTTP development, `.env.example` defaults to `APP_ENV=development` and `SESSION_COOKIE_SECURE=false`. Do not use those cookie settings for public production hosting.

Leave `OPENWEATHER_API_KEY` and `DATA_GOV_IN_API_KEY` empty unless you have obtained real provider credentials. No credentials are bundled. A missing key should produce an unavailable/configuration state, not fabricated live data.

## 4. Run checks before starting the website

Run these commands from the repository root with `.venv` activated:

```bash
python -m compileall -q app.py backend.py run.py rythu_mitra_backend scripts tests train_model.py
python scripts/check_frontend_contract.py
python -m pytest -q
```

The GitHub Actions run for the integration pull request reported **28 Python tests passed**, as well as compilation, required-file/JSON and JavaScript-syntax checks. Run them again in your own Codespace and use the actual output from that environment.

Then inspect the local health and model-asset reports:

```bash
python scripts/health_check.py
python scripts/verify_model_assets.py
```

Expected model status:

- `models/crop_model.pkl` and `models/plant_disease_model.h5` are included in this repository.
- Crop recommendations still need to be exercised in the target environment; the existence of a pickle file alone does not validate its origin, input assumptions or agronomic accuracy.
- The disease model has 15 output classes, but the authoritative class-index-to-name mapping is **not** available. `data/disease_labels.template.json` is only a placeholder; do not rename it to `disease_labels.json` or fill it with guessed names. The disease-name prediction path must remain unavailable until the original mapping is recovered and verified. See `data/DISEASE_LABELS_REQUIRED.md`.
- TensorFlow is optional for basic startup and the Python test suite. It is required to load the H5 disease model; install it only when ready to test that model:

  ```bash
  python -m pip install -r requirements-ml.txt
  python scripts/verify_model_assets.py --load-disease
  ```

  The disease-model check remains blocked if the verified label mapping is absent.

## 5. Start Flask

Run:

```bash
python run.py
```

Leave that terminal open while using the site. The server listens on port 5000 by default.

In Codespaces:

1. Open the **Ports** panel in VS Code.
2. Forward port **5000** if it is not listed.
3. Click the browser/globe icon to open the forwarded URL.

The forwarded Codespaces URL is for development and testing, not a permanent public domain.

In a second terminal, verify local endpoints:

```bash
curl -i http://127.0.0.1:5000/health
curl -i http://127.0.0.1:5000/ready
```

Record the real HTTP status and response. A health endpoint does not prove that each optional model or live provider is usable.

## 6. Browser verification checklist

Only mark a check as passed after actually trying it in the browser. A page loading by itself does not prove full integration.

### Basic app and navigation

- [ ] Homepage opens without a blank page or blocking JavaScript error.
- [ ] Primary navigation opens the expected workspaces.
- [ ] Browser refresh and Back/Forward do not break navigation.
- [ ] English and Telugu text are readable and not clipped.
- [ ] Privacy policy and terms pages open at `/privacy-policy` and `/terms-and-conditions`.

### Authentication and data privacy

- [ ] Register a non-sensitive test account, sign in, refresh, and sign out.
- [ ] Invalid inputs and duplicate-account attempts show understandable errors.
- [ ] A protected action after sign-out is denied.
- [ ] Use two test accounts to check that one user cannot read or change the other's private records.
- [ ] Do not use real farmer personal information in tests.

### Crop, disease, weather and markets

- [ ] Submit valid crop-model inputs and confirm the response comes from the backend and is labelled as model output.
- [ ] Try missing/out-of-range crop inputs and confirm the app rejects them.
- [ ] Until the disease labels are verified, confirm that disease-name inference shows unavailable instead of a guessed result.
- [ ] Without API keys, check that weather and official mandi data clearly show unavailable/configuration status.
- [ ] With authorized credentials, verify the actual source and observation date shown by returned provider data. Mandi data is latest reported daily data, not tick-by-tick prices.

### Mobile and accessibility

- [ ] Check narrow mobile widths (including 360px) and ensure there is no unwanted horizontal page scroll.
- [ ] Test 200% browser zoom, keyboard-only navigation, visible focus, form labels and errors.
- [ ] Check long Telugu text and reduced-motion behavior.
- [ ] Check the browser console and failed Network requests without sharing cookies, tokens, API keys or personal data.

## 7. Provider credentials and public hosting are separate tasks

Live weather needs `OPENWEATHER_API_KEY`; official daily mandi data needs a valid server-side `DATA_GOV_IN_API_KEY`. Never add credentials to frontend JavaScript or commit them to GitHub.

Do not treat the project as production-ready merely because the development site opens. Public hosting requires a deliberate configuration of a strong persistent secret, HTTPS, secure cookies, Redis for shared rate limits, persistent SQLite/storage, backups, monitoring, privacy/legal review and tests on the final deployment. Consult `SECURITY.md`, `RELEASE_CHECKLIST.md` and `PRE_LAUNCH_BRAND_CHECKLIST.md` before deployment.

## Final status

**Completed:** repository merge; source integration; automated pull-request checks (28 Python tests passed, plus compile/file/JSON/JavaScript checks).

**Still to verify:** the app running in a real Codespace/browser; authentication and user privacy workflows; mobile/Telugu/accessibility checks; crop model output in the target environment; live provider connections when credentials are available; disease inference after the authoritative 15-label mapping is recovered; production hosting.

This is the current post-merge procedure. Do not repeat ZIP upload/extraction or merge instructions from older notes.
