# Official daily mandi price setup

## What this integration does

The backend queries the Government of India's Open Government Data API for the daily mandi price resource generated through AGMARKNET:

- Resource: `9ef84268-d588-465a-a308-a864a43d0070`
- Official resource page: https://www.data.gov.in/resource/current-daily-price-various-commodities-various-markets-mandi
- Dataset cadence: daily
- Key price fields: state, district, market, commodity, variety, grade, arrival date, minimum price, modal price, maximum price

This is the latest reported daily observation, **not** an instant tick-by-tick market feed, a guaranteed farm-gate price, or a prediction of what a buyer will pay.

## Configure in the Codespace

1. Sign in to data.gov.in and generate your own API key using the portal's API feature: https://www.data.gov.in/help
2. In the Codespace project terminal, from the project root, create the local environment file if it does not exist:

   ```bash
   cp .env.example .env
   ```

3. Open `.env` in VS Code and set:

   ```dotenv
   DATA_GOV_IN_API_KEY=put_your_own_key_here
   MARKET_DEFAULT_STATE=Telangana
   ```

4. Save `.env`. Never paste the API key in the chat, frontend JavaScript, a screenshot, a commit, a public issue, or a report. `.env` is ignored by Git; verify with `git status --short` before committing.
5. Restart Flask so its environment config is reloaded:

   ```bash
   # stop the existing server with Ctrl+C, then:
   python run.py
   ```

6. Open the forwarded port 5000. Go to Markets and choose the live/latest provider action.

## Expected result

The UI should show `LATEST REPORTED (DAILY)`, source `data.gov.in / AGMARKNET daily mandi prices`, the source observation date, and minimum/modal/maximum price in rupees per quintal. Records older than two days or with an unknown/future date are marked stale. This is a freshness warning only; the source date remains visible.

If a key is missing, rejected, rate-limited, the provider times out, the response changes, or no valid records match the filters, the endpoint returns `UNAVAILABLE`. It does not make up numbers or relabel stale observations as current.

## Useful endpoint

After configuring the key, the frontend's Live button calls:

`GET /api/markets?provider=live&commodity=Paddy&district=Warangal`

State defaults to `MARKET_DEFAULT_STATE` (Telangana unless changed in `.env`). The key is only sent by the server. Do not call this API directly from browser JavaScript.

## Limits still to verify

- A real provider smoke test must be run in the user's Codespace after the key is configured.
- Provider field/filter availability and quotas can change; inspect the actual response, not only HTTP 200.
- The current connector retrieves latest daily records. Historical trend view still relies on records stored in Rythu Mitra; it does not claim the official current-daily API is a long-term historical database.
- Do not use the modal wholesale price as a promise of the amount a farmer will receive. Transport, quality, quantity, fees, distance, and buyer terms can differ.
