"""Official data.gov.in mandi prices plus an optional legacy adapter.

The OGD resource reports daily market observations, not tick-by-tick live prices.
All values are normalized and source/observation dates are preserved.
"""
from __future__ import annotations

from datetime import date, datetime, timezone
import math
from typing import Any

from flask import current_app
import requests

DATA_GOV_IN_RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"
DATA_GOV_IN_RESOURCE_URL = (
    "https://www.data.gov.in/resource/current-daily-price-various-commodities-"
    "various-markets-mandi"
)
DATA_GOV_IN_API_ROOT = "https://api.data.gov.in/resource"


def _text(value: Any, limit: int = 160) -> str:
    if value is None:
        return ""
    return " ".join(str(value).replace("\x00", "").split())[:limit]


def _price(value: Any) -> float | None:
    try:
        cleaned = str(value).replace(",", "").strip()
        if not cleaned or cleaned.lower() in {"na", "n/a", "null", "none", "-"}:
            return None
        result = float(cleaned)
        if not math.isfinite(result) or result < 0:
            return None
        return result
    except (TypeError, ValueError):
        return None


def _parse_price_date(value: Any) -> date | None:
    raw = _text(value, 32)
    if not raw:
        return None
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%y"):
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    return None


def _normalise_ogd_row(row: dict[str, Any], fetched_at: str) -> dict[str, Any] | None:
    # Dataset fields are normally lowercase IDs, but tolerate capitalized names.
    source = {str(k).strip().lower(): v for k, v in row.items()}
    commodity = _text(source.get("commodity"))
    market = _text(source.get("market"))
    district = _text(source.get("district"))
    state = _text(source.get("state"))
    low = _price(source.get("min_price", source.get("minimum_price")))
    modal = _price(source.get("modal_price"))
    high = _price(source.get("max_price", source.get("maximum_price")))
    date_raw = source.get("arrival_date", source.get("price_date"))
    observed = _parse_price_date(date_raw)
    # Never serve a row as a price record if core fields are absent or impossible.
    if not commodity or not market or not observed or None in (low, modal, high):
        return None
    if not low <= modal <= high:
        return None
    age_days = (date.today() - observed).days
    # Future-dated source records are suspicious; keep them visible as stale rather
    # than silently treating them as today's observation.
    stale = age_days < 0 or age_days > 2
    return {
        "state": state,
        "district": district,
        "market": market,
        "commodity": commodity,
        "variety": _text(source.get("variety")),
        "grade": _text(source.get("grade")),
        "minimum_price": low,
        "modal_price": modal,
        "maximum_price": high,
        "price_date": observed.isoformat(),
        "unit": "quintal",
        "status": "LATEST_REPORTED",
        "data_type": "LATEST_REPORTED",
        "source_name": "data.gov.in / AGMARKNET daily mandi prices",
        "source_url": DATA_GOV_IN_RESOURCE_URL,
        "server_fetched_at": fetched_at,
        "age_days": age_days,
        "is_stale": stale,
        "freshness_status": "STALE" if stale else "RECENT_DATE_CHECK_ONLY",
        "note": "Daily wholesale observation from the source; not an instant or guaranteed sale price.",
    }


def fetch_data_gov_in(commodity: str | None = None, district: str | None = None,
                      market: str | None = None, state: str | None = None) -> dict:
    """Fetch the official daily mandi resource. Requires the user's own server-side API key."""
    api_key = str(current_app.config.get("DATA_GOV_IN_API_KEY", "")).strip()
    if not api_key:
        return {"success": False, "status": "UNAVAILABLE", "data_type": "UNAVAILABLE",
                "error": "Official mandi API key is not configured. Add DATA_GOV_IN_API_KEY to the server environment."}

    selected_state = _text(state or current_app.config.get("MARKET_DEFAULT_STATE", "Telangana"), 80)
    params: dict[str, Any] = {
        "api-key": api_key,
        "format": "json",
        "limit": 100,
        "offset": 0,
    }
    for field, value in (("State", selected_state), ("District", district),
                         ("Commodity", commodity), ("Market", market)):
        cleaned = _text(value, 80)
        if cleaned:
            params[f"filters[{field}]"] = cleaned
    url = f"{DATA_GOV_IN_API_ROOT}/{DATA_GOV_IN_RESOURCE_ID}"
    try:
        response = requests.get(url, params=params, timeout=(3.05, 10))
        response.raise_for_status()
        body = response.json()
        if not isinstance(body, dict) or not isinstance(body.get("records"), list):
            raise ValueError("Unexpected data.gov.in response structure")
        fetched_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        records = []
        for row in body["records"][:100]:
            if isinstance(row, dict):
                clean = _normalise_ogd_row(row, fetched_at)
                if clean is not None:
                    records.append(clean)
        if not records:
            return {"success": False, "status": "UNAVAILABLE", "data_type": "UNAVAILABLE",
                    "records": [], "source_name": "data.gov.in / AGMARKNET daily mandi prices",
                    "source_url": DATA_GOV_IN_RESOURCE_URL,
                    "error": "The official provider returned no usable price records for these filters."}
        return {"success": True, "status": "LATEST_REPORTED", "data_type": "LATEST_REPORTED",
                "source_name": "data.gov.in / AGMARKNET daily mandi prices",
                "source_url": DATA_GOV_IN_RESOURCE_URL, "server_fetched_at": fetched_at,
                "observation_frequency": "daily", "total_available": body.get("total"),
                "state_filter": selected_state, "records": records,
                "note": "These are the latest reported daily observations returned by the official dataset, not tick-by-tick live prices. Check each price date before deciding."}
    except (requests.RequestException, ValueError, TypeError) as exc:
        # Do not log the request URL: data.gov.in carries the API key in its query string.
        current_app.logger.warning("Official data.gov.in mandi request failed or had invalid data (%s)", type(exc).__name__)
        return {"success": False, "status": "UNAVAILABLE", "data_type": "UNAVAILABLE",
                "source_name": "data.gov.in / AGMARKNET daily mandi prices",
                "source_url": DATA_GOV_IN_RESOURCE_URL,
                "error": "Official mandi data could not be fetched or verified right now. Please retry later."}


def fetch_custom_adapter(commodity: str | None = None, district: str | None = None) -> dict:
    """Backward-compatible explicitly configured HTTPS adapter; never implies official source."""
    base = str(current_app.config.get("MARKET_DATA_BASE_URL", "")).strip()
    if not base:
        return {"success": False, "status": "UNAVAILABLE", "data_type": "UNAVAILABLE",
                "error": "No custom market-data adapter is configured."}
    if not base.startswith("https://"):
        return {"success": False, "status": "UNAVAILABLE", "data_type": "UNAVAILABLE",
                "error": "Market adapter must use HTTPS."}
    params = {k: v for k, v in {"commodity": commodity, "district": district}.items() if v}
    headers = {}
    api_key = str(current_app.config.get("MARKET_DATA_API_KEY", "")).strip()
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    try:
        response = requests.get(base.rstrip("/") + "/prices", params=params, headers=headers, timeout=(3.05, 8))
        response.raise_for_status()
        body = response.json()
        if not isinstance(body, dict) or body.get("success") is not True or not isinstance(body.get("records"), list):
            raise ValueError("Provider did not match the configured adapter contract")
        records = []
        for row in body["records"][:100]:
            if not isinstance(row, dict):
                continue
            required = ("commodity", "market", "minimum_price", "modal_price", "maximum_price", "price_date")
            if not all(row.get(k) is not None for k in required):
                continue
            low, modal, high = (_price(row[k]) for k in ("minimum_price", "modal_price", "maximum_price"))
            if None in (low, modal, high) or not low <= modal <= high:
                continue
            records.append({**row, "minimum_price": low, "modal_price": modal, "maximum_price": high,
                            "status": "LIVE", "data_type": "LIVE",
                            "source_name": _text(body.get("source_name") or "Configured custom market provider"),
                            "source_url": _text(body.get("source_url") or base),
                            "server_fetched_at": body.get("fetched_at") or datetime.now(timezone.utc).isoformat(timespec="seconds")})
        if not records:
            return {"success": False, "status": "UNAVAILABLE", "data_type": "UNAVAILABLE",
                    "error": "Custom market provider returned no usable price records."}
        return {"success": True, "status": "LIVE", "data_type": "LIVE",
                "source_name": body.get("source_name") or "Configured custom market provider",
                "source_url": body.get("source_url") or base,
                "server_fetched_at": body.get("fetched_at"), "records": records}
    except (requests.RequestException, ValueError, TypeError) as exc:
        current_app.logger.warning("Custom market adapter request failed or had invalid data (%s)", type(exc).__name__)
        return {"success": False, "status": "UNAVAILABLE", "data_type": "UNAVAILABLE",
                "error": "Configured market adapter is unavailable or returned invalid data."}


def fetch_configured_provider(commodity: str | None = None, district: str | None = None,
                              market: str | None = None, state: str | None = None) -> dict:
    """Prefer direct official OGD when configured; otherwise keep the legacy adapter option."""
    if str(current_app.config.get("DATA_GOV_IN_API_KEY", "")).strip():
        return fetch_data_gov_in(commodity, district, market, state)
    if str(current_app.config.get("MARKET_DATA_BASE_URL", "")).strip():
        return fetch_custom_adapter(commodity, district)
    return fetch_data_gov_in(commodity, district, market, state)
