# Browser and Device QA Checklist

This is a release verification script, not a claim that an automated browser was available in the local environment.

## Desktop, tablet, phone

1. Run `python app.py` and open `http://127.0.0.1:5000` in a current Chromium/Firefox/Safari browser.
2. Test widths around 390px, 768px, and 1440px. Confirm no horizontal scroll, usable touch targets, readable Telugu, visible focus rings, and one-column cards on phone widths.
3. Sign in as farmer, buyer, expert, and admin. Confirm unauthorized record creation/moderation is rejected server-side.

## Language and voice

1. Switch `EN`/`తె`; confirm navigation changes, `document.documentElement.lang` changes, and a signed-in preference survives reload.
2. On a browser supporting `SpeechRecognition`, select Voice help, confirm a visible “What I heard” transcript, and test weather, price, today, and schemes intents.
3. On unsupported browsers, confirm the visible fallback says voice is unavailable and navigation remains usable.

## Camera, disease, and safety

1. On a phone, open Crop health and confirm the image input can offer the rear camera (`capture=environment`).
2. Test valid JPEG/PNG/WebP, wrong extension/MIME, corrupt file, and >5 MB file. Confirm safe errors.
3. Confirm results show `Model class N` unless an owner-provided verified mapping exists, plus confidence and professional-confirmation wording.

## PWA/offline

1. Install/add the app if the browser supports the manifest. Confirm the shell loads after an app-shell cache warm-up.
2. Disconnect the network. Confirm the offline banner appears, shell navigation remains available, and weather/API responses say they cannot be presented as current.
3. Reconnect and use Refresh; confirm live weather can be fetched again and cached weather is marked `CACHED`/non-current.

## Data honesty and security

Confirm DEMO labels on curated markets, schemes, equipment, storage, buyer, expert, and fallback-weather records; verify no API key appears in page source, network response, logs, or screenshots. Use the release checklist after completing this manual pass.
