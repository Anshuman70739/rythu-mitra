# Replace the Codespaces project with this complete bundle safely

This package is a complete project tree. Do not delete the current repository before making a backup and testing this candidate.

## Recommended sequence

1. Download this ZIP to your computer and upload it to your Codespace, or move it into `/workspaces`.
2. In the current Codespace terminal, check pending edits:

   ```bash
   cd /workspaces/rythu-mitra
   git status --short
   ```

3. Back up the whole working folder outside the repository (including the current model files and uncommitted edits):

   ```bash
   cd /workspaces
   cp -a rythu-mitra "rythu-mitra-backup-$(date +%Y%m%d-%H%M%S)"
   ```

   Confirm the backup directory exists before continuing. Do not skip this if `git status` reports modified files.

4. Extract this ZIP into a separate candidate folder, not on top of the current repository:

   ```bash
   mkdir -p /workspaces/rythu-mitra-full-candidate
   unzip -q /workspaces/RythuMitra_Complete_Integrated.zip -d /workspaces/rythu-mitra-full-candidate
   cd /workspaces/rythu-mitra-full-candidate/RythuMitra_Complete_Integrated
   ```

   Adjust the ZIP path only if you uploaded it somewhere else. Verify that `run.py`, `backend.py`, `rythu_mitra_backend/`, `templates/`, `static/`, `models/` and `tests/` exist.

5. Test the candidate in that folder first:

   ```bash
   python -m compileall -q .
   python scripts/verify_model_assets.py
   python -m pytest -q
   ```

   The model-asset check will report that the *verified disease-label mapping* is missing. That warning is expected and intentional; the weights are included, but the class names are not known. Do not claim disease-name prediction is ready until `data/disease_labels.json` is supplied from the original model source and `python scripts/verify_model_assets.py --load-disease` passes.

6. Only after reviewing/testing the candidate, replace the working tree while keeping `.git`, your local `.env`, and private uploads/database files. If you choose to replace the existing repo tree, run these commands carefully from the existing repo root, after confirming the candidate and backup paths are correct:

   ```bash
   cd /workspaces/rythu-mitra
   rsync -av --delete \
     --exclude='.git/' \
     --exclude='.env' \
     --exclude='uploads/' \
     --exclude='data/*.db' \
     --exclude='data/*.db-*' \
     /workspaces/rythu-mitra-full-candidate/RythuMitra_Complete_Integrated/ ./
   ```

   The source path above must point to the extracted candidate. This synchronizes the project files as a group; files not present in the package are removed except the excluded repository metadata, local environment file, private uploads and SQLite database files. Review `git status --short` before any commit. Do not force-push or delete `.git`.

7. Recheck `.env` settings privately, then run the project tests again. Install base requirements with `python -m pip install -r requirements.txt`; install `requirements-ml.txt` only when the environment supports TensorFlow and you are testing disease-model loading.

## Do not upload secrets

Never commit `.env`, access tokens, private farmer uploads or private database records. The bundle does not contain your secrets or the original Git metadata.
