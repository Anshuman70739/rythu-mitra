# Multichannel Backend Contract — Demo Foundation

This document describes the backend prototype in branch `backend/multichannel-foundation-20261027`.

## Demo chat

**POST** `/api/channels/demo-chat`

Requires a valid session CSRF token in `X-CSRF-Token`. Request:

```json
{"message":"hello","language":"en"}
```

- `message`: required string, 1–500 characters.
- `language`: `en` or `te`; defaults to `en`.
- The response includes `success`, `channel`, `language`, `status`, `answer`, `source`, `updated_at`, `requires_human`, and `demo`.
- `status` is one of `DEMO` or `UNAVAILABLE` for the demo routes. Weather with a city uses the existing weather service and may return its real provider status.
- Market prices are intentionally unavailable unless the official provider is configured. The bot does not invent prices.
- Crop help is preliminary and escalates to human help; it does not name a plant disease without verified class labels.

## IVR menu simulation

**POST** `/api/channels/ivr/demo`

Requires a valid session CSRF token. Request:

```json
{"digits":"2","language":"en"}
```

This simulates keypad (DTMF) input and returns the same shared reply flow. The response explicitly says no phone call was placed. It does not connect to a telephone provider.

## Demo flow

1. `hello` / `menu`: show the English or Telugu menu.
2. `1`: ask for a city; send `weather Hyderabad` to test provider configuration.
3. `2`: collect crop details and show safe preliminary guidance; human follow-up is requested but no agent is notified.
4. `3`: explain that mandi data is unavailable until official credentials are configured.
5. `4`: link to the official MyScheme portal and clarify that this demo does not submit applications or determine eligibility.
6. `5`: demonstrate an escalation request without claiming a real agent was contacted.

## Important distinction

These endpoints provide a working, local, testable conversation prototype for presentations. They are **not a live WhatsApp bot or live IVR service**. Actual WhatsApp/voice integration still needs a chosen provider, verified webhook signature handling, opt-in/consent, provider account configuration, approved templates where applicable, production URLs, provider-specific tests, and a privacy review.

Do not remove the application's global CSRF protection to make provider webhooks work. A future webhook must use a narrowly scoped exemption only after authenticating the provider's signature and validating timestamps/request shape.

## Tests

The automated tests in `tests/test_channels.py` cover bilingual menu behavior, safe crop guidance, no fabricated market prices, simulated IVR, invalid inputs, CSRF, and missing weather credentials. They must be run in the repository environment before claiming PASS.
