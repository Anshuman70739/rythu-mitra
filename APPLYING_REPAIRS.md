# Applying this repair candidate safely

## Important version warning

This candidate is based on `Rythu_Mitra_Master_v1_Integrated_Frontend_v2.zip` (the modular Flask package plus the integrated v2 frontend). It is **not a drop-in patch for the older single-file backend currently seen in some Codespaces**. The uploaded archives did not contain `.git` metadata, so this process could not create a branch or alter/push your GitHub repository. No source was pushed or deployed.

Do not extract this full archive over your active repository blindly. The candidate ZIP does not include `crop_model.pkl`, `plant_disease_model.h5`, or `disease_labels.json`; replacing folders wholesale could remove or hide files that exist in your active repository. The original uploaded archives remain unchanged.

## Choose the correct base

- If you are already working from the integrated v2 structure (`rythu_mitra_backend/`, `static/js/rythu-mitra-app.js`, `templates/rythu_mitra.html`), apply `Rythu_Mitra_Repair_Overlay_for_Integrated_v2.zip` on a new Git branch after making sure `git status --short` is clean.
- If your active checkout only has the older `app.py`, a large `backend.py`, `crop_model.pkl`, and `plant_disease_model.h5`, it is a different architecture. Keep it untouched until you deliberately choose whether integrated v2 will replace that implementation. Do not paste the new tiny `backend.py` wrapper into the old code without also switching the rest of the backend package as a coherent candidate.

## If choosing the integrated v2 candidate

1. Save/backup the current repository state and create a branch in your own Codespace:

   ```bash
   git status --short
   git switch -c qa/rythu-mitra-audit-repair
   ```

   If the working tree has changes, save them first. Do not reset them.

2. Make sure your repository contains the integrated v2 project structure. Apply the overlay only to that structure, or extract the full candidate to a separate folder and compare before copying changes.
3. Preserve the trusted model binaries from your existing repo. They can remain at the project root (where this candidate has a legacy fallback) or be placed under `models/`. Do not add them to the frontend's `static/` folder.
4. Locate the matching disease class labels from the actual model-training pipeline and place the verified list at `data/disease_labels.json` or `models/disease_labels.json`. **Do not guess the class order.**
5. Use compatible Python (3.12 recommended for this requirements set), activate a virtual environment, then run:

   ```bash
   python -m pip install -r requirements.txt
   python -m pip install -r requirements-ml.txt  # needed for H5 disease inference
   python -m pytest -q
   python -m compileall -q .
   node --check static/js/rythu-mitra-app.js
   python scripts/check_frontend_contract.py
   python scripts/verify_model_assets.py
   python scripts/verify_model_assets.py --load-disease
   ```

   Run model verification only after placing the files. The `--load-disease` check loads the H5 model; it still cannot prove the labels' semantic order or model accuracy on Telangana field images.
6. Follow `MARKET_DATA_SETUP.md` to set your own `DATA_GOV_IN_API_KEY` in the ignored `.env`; never paste the key into chat or commit it.
7. Start with `python run.py`, use Codespaces port 5000, and follow `TEST_REPORT.md`, `FRONTEND_TEST_REPORT.md`, `TRACEABILITY_MATRIX.md` and `RELEASE_CHECKLIST.md`.
8. Review the diff, run your full test suite and browser scenarios, then make your own commit only if the checks support it. This package does not auto-commit or push anything.

## What is intentionally not claimed

- No full pytest suite passed in this review environment; Flask could not be installed here due network/DNS failure.
- No live market smoke request was made. The provider key must be configured in your own server environment.
- No model inference is verified from these ZIPs because the model weights and disease labels are not included in them.
- No browser E2E, native-Telugu, screen-reader, production-security or farmer field test is claimed.
