# Rythu Mitra — Smart Farmer Decision Support Platform

Rythu Mitra is a local-first college prototype for helping farmers decide what to do today. It joins crop recommendations, conservative soil guidance, weather advisories, crop-health image analysis, market comparisons, schemes, equipment, storage, buyers, crop tasks, and expert/community information in one responsive Flask application.

## What is real, demo, and model-based

- The included crop model is used for the recommendation flow.
- The included Keras disease artifact is used for image inference. It has 15 outputs but no verified disease-label map, so results are intentionally shown as a model class—not a fabricated diagnosis.
- OpenWeather is live only when `OPENWEATHER_API_KEY` is configured; otherwise the UI says **DEMO** and explains why.
- Markets, schemes, equipment, storage, buyers, experts, crop calendar, and alerts are curated demo data. They are visually and structurally marked as such.
- Yield and market-income values are transparent reference estimates, never yield/profit guarantees.

## Features

- Farmer profile, role-aware demo login, personalised dashboard, actions, weather, and crop tasks.
- Crop planning using NPK, pH, rainfall, temperature, and humidity; fertilizer and favourability guidance.
- Plant image validation and Keras model inference with confidence and safety wording.
- Market comparison and net-income calculator; schemes with official-source links; demo buyers, equipment, storage, and expert records.
- API infrastructure for farmer listings, equipment booking, crop-damage reports, expert questions, notifications, feedback, moderation/audit data, and protected admin summary.
- English/Telugu translation dictionaries and a Telugu-capable font fallback; installable app-shell cache for weak connectivity.

## Run locally

This project uses the existing environment at `~/crop-env` where available.

```bash
cd ~/crop-recommendation
cp .env.example .env
# optionally set OPENWEATHER_API_KEY in .env; never commit it
python -m pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`. Use the farmer demo account `9999999999` / `demo-farmer`; other documented demo roles are shown on the sign-in dialog. Demo credentials must never be used outside local demonstration.

## Test

```bash
python -m pytest -q
```

The test suite covers startup/UI headers, login, dashboard authorization, CSRF, crop validation/model wrapping, weather handling, image rejection, records, market calculations, and role protection.

## Architecture and data

See [ARCHITECTURE.md](ARCHITECTURE.md). SQLite is created locally in `data/rythu_mitra.db` and is ignored by Git. Each seeded content record carries source/status/update metadata. Official links are used where included; verify all eligibility and current rules with the official source.

## Safety and limitations

This is decision support, not agronomy, medical, financial, insurance, or legal advice. Confirm crop disease and chemical choices with a qualified agriculture professional. It does not send SMS/WhatsApp, take payments, submit insurance claims, or guarantee availability, eligibility, price, yield, or profit.

## GitHub preparation

`.gitignore`, `.env.example`, dependency constraints, security documentation, audit, architecture, test report, and release checklist are included. Do not publish until secrets are scanned and the release checklist is reviewed.
