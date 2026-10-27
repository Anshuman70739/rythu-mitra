# Rythu Mitra

A farmer-focused web experience for Telangana, bringing weather, crop information and market guidance into one clear interface.

## Website

This branch contains the Monsoon landing page and the files it needs to run. It is the current visual version of Rythu Mitra.

## Run locally

Use Python 3.12 or a compatible version. From the repository folder:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python run.py
```

Open the local address printed by the server. Some workspace features need server-side provider credentials; the landing page does not prove those integrations are live.

## Notes

Keep changes to this branch focused on the landing page and its required assets. Keep credentials, farmer data and local databases out of Git.
