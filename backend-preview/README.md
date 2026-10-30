# Rythu Mythra — isolated backend preview

This branch preserves the existing website and adds the new backend package as an isolated preview source archive.

- Backend source archive: `rythumythra-backend-runtime.tar.gz`
- Render extracts the archive during build and runs the Flask API from `RythuMythra-DO-backend/`.
- Health endpoint: `/api/health`
- API root: `/`

## Preview-only warning
This is a temporary review deployment, not production. Render's free filesystem is ephemeral; do not enter real farmer, financial, identity, or other personal data. The weather API key is not included in this repository or archive; configure it separately as a Render secret after rotating the key shared in chat.

The approved landing-page files are not edited by this change.
