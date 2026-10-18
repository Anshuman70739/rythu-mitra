"""Weather provider adapter with honest LIVE/CACHED/DEMO/UNAVAILABLE states."""
from __future__ import annotations
from datetime import datetime, timezone
import time
from flask import current_app
import requests

_CACHE: dict[str, tuple[float, dict]] = {}
CACHE_TTL_SECONDS = 600


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def get_weather(city: str, *, force_refresh: bool = False) -> dict:
    key = str(current_app.config.get("OPENWEATHER_API_KEY", "")).strip()
    cache_key = city.strip().casefold()
    cached = _CACHE.get(cache_key)
    if not force_refresh and cached:
        age = max(0, int(time.monotonic() - cached[0]))
        if age <= CACHE_TTL_SECONDS:
            result = dict(cached[1])
            result.update(status="CACHED", data_type="CACHED", is_current=False,
                          cache_age_seconds=age, server_fetched_at=cached[1].get("server_fetched_at"),
                          reason="Cached provider result; not a fresh observation.")
            return result
    if not key:
        if current_app.config.get("DEMO_MODE"):
            stamp = _utc_now()
            return {
                "success": True, "status": "DEMO", "data_type": "DEMO", "is_current": False,
                "source_name": "Rythu Mitra demonstration fixture", "source_url": None,
                "provider_observed_at": None, "server_fetched_at": stamp,
                "last_updated": stamp, "cache_age_seconds": None,
                "temperature": 28, "humidity": 72, "rainfall": 12,
                "rain_probability": 55, "wind": 14, "forecast": [],
                "advisories": ["DEMO WEATHER — NOT CURRENT. Do not use this example for a farm decision."],
                "reason": "No weather API key is configured; values are fictional demo fixtures.",
            }
        return {"success": False, "status": "UNAVAILABLE", "data_type": "UNAVAILABLE",
                "source_name": None, "source_url": None, "provider_observed_at": None,
                "server_fetched_at": None, "error": "Live weather is not configured. No current weather is available."}
    fetched = _utc_now()
    try:
        response = requests.get("https://api.openweathermap.org/data/2.5/weather",
            params={"q": city, "appid": key, "units": "metric"}, timeout=8)
        if response.status_code == 404:
            return {"success": False, "status": "UNAVAILABLE", "data_type": "UNAVAILABLE", "error": "Location not found."}
        if response.status_code in (401, 403):
            return {"success": False, "status": "UNAVAILABLE", "data_type": "UNAVAILABLE", "error": "Weather provider credentials are invalid or not enabled."}
        if response.status_code == 429:
            return {"success": False, "status": "UNAVAILABLE", "data_type": "UNAVAILABLE", "error": "Weather provider rate limit reached."}
        response.raise_for_status()
        data = response.json()
        main = data.get("main") if isinstance(data, dict) else None
        if not isinstance(main, dict) or not isinstance(main.get("temp"), (int, float)) or not isinstance(main.get("humidity"), (int, float)):
            raise ValueError("Provider response is missing required fields")
        wind_ms = ((data.get("wind") or {}).get("speed") or 0)
        if not isinstance(wind_ms, (int, float)):
            wind_ms = 0
        rainfall = (data.get("rain") or {}).get("1h", 0)
        if not isinstance(rainfall, (int, float)):
            rainfall = 0
        result = {
            "success": True, "status": "LIVE", "data_type": "LIVE", "is_current": True,
            "source_name": "OpenWeather", "source_url": "https://openweathermap.org/current",
            "provider_observed_at": datetime.fromtimestamp(data["dt"], timezone.utc).isoformat(timespec="seconds") if isinstance(data.get("dt"), (int, float)) else None,
            "server_fetched_at": fetched, "last_updated": fetched, "cache_age_seconds": 0,
            "temperature": round(float(main["temp"]), 1), "humidity": int(main["humidity"]),
            "rainfall": round(float(rainfall), 1), "rain_probability": None,
            "wind": round(float(wind_ms) * 3.6, 1), "forecast": [], "advisories": [],
        }
        forecast = []
        rain_probs = []
        try:
            fr = requests.get("https://api.openweathermap.org/data/2.5/forecast",
                params={"q": city, "appid": key, "units": "metric", "cnt": 8}, timeout=8)
            if fr.status_code == 200:
                for item in (fr.json().get("list") or [])[:8]:
                    details = item.get("main") or {}
                    pop = item.get("pop")
                    if isinstance(details.get("temp"), (int, float)) and isinstance(pop, (float, int)):
                        p = int(round(max(0, min(1, float(pop))) * 100))
                        rain_probs.append(p)
                        forecast.append({"time": item.get("dt_txt"), "temperature": round(float(details["temp"]), 1), "rain_probability": p, "rainfall": (item.get("rain") or {}).get("3h", 0)})
        except (requests.RequestException, ValueError, TypeError, KeyError):
            forecast = []
        result["forecast"] = forecast
        result["rain_probability"] = max(rain_probs) if rain_probs else None
        if result["wind"] > 25:
            result["advisories"].append("Wind is elevated; avoid spraying until local conditions are safe.")
        if result["humidity"] >= 80:
            result["advisories"].append("Humidity is high; inspect crops for disease symptoms and seek local advice if needed.")
        if result["rainfall"] > 5:
            result["advisories"].append("Rain was reported in the last hour; check drainage and local field conditions.")
        if result["rain_probability"] is not None and result["rain_probability"] >= 60:
            result["advisories"].append("The provider forecast indicates a high chance of rain in a forecast interval; check forecast timestamps before acting.")
        if not result["advisories"]:
            result["advisories"] = ["No rule-based alert triggered by the fetched weather fields. This is not a crop diagnosis."]
        _CACHE[cache_key] = (time.monotonic(), dict(result))
        return result
    except requests.Timeout:
        return {"success": False, "status": "UNAVAILABLE", "data_type": "UNAVAILABLE", "error": "Weather provider timed out."}
    except (requests.RequestException, ValueError, TypeError, KeyError):
        return {"success": False, "status": "UNAVAILABLE", "data_type": "UNAVAILABLE", "error": "Weather provider response could not be used."}
