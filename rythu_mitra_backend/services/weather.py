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


def _open_meteo_weather(city: str, *, fallback_reason: str | None = None) -> dict:
    """No-key weather fallback using Open-Meteo model forecasts, with explicit provenance."""
    fetched = _utc_now()
    cache_key = city.strip().casefold()
    try:
        geo_response = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 10, "language": "en", "format": "json", "countryCode": "IN"},
            timeout=(3.05, 8),
        )
        geo_response.raise_for_status()
        geo_body = geo_response.json()
        places = geo_body.get("results") if isinstance(geo_body, dict) else None
        if not isinstance(places, list) or not places:
            return {"success": False, "status": "UNAVAILABLE", "data_type": "UNAVAILABLE",
                    "source_name": "Open-Meteo", "source_url": "https://open-meteo.com/",
                    "error": "No matching Indian location was found. Check the spelling of the district or city."}
        place = next((p for p in places if str(p.get("admin1", "")).casefold() == "telangana"), places[0])
        latitude, longitude = place.get("latitude"), place.get("longitude")
        if not isinstance(latitude, (int, float)) or not isinstance(longitude, (int, float)):
            raise ValueError("Geocoding response is missing coordinates")
        response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m",
                "hourly": "temperature_2m,precipitation_probability,precipitation",
                "forecast_days": 2,
                "timezone": "auto",
                "wind_speed_unit": "kmh",
            },
            timeout=(3.05, 10),
        )
        response.raise_for_status()
        body = response.json()
        current = body.get("current") if isinstance(body, dict) else None
        hourly = body.get("hourly") if isinstance(body, dict) else None
        if not isinstance(current, dict) or not isinstance(hourly, dict):
            raise ValueError("Open-Meteo response is missing current or hourly data")
        temperature = current.get("temperature_2m")
        humidity = current.get("relative_humidity_2m")
        if not isinstance(temperature, (int, float)) or not isinstance(humidity, (int, float)):
            raise ValueError("Open-Meteo response is missing temperature or humidity")
        times = hourly.get("time") if isinstance(hourly.get("time"), list) else []
        temps = hourly.get("temperature_2m") if isinstance(hourly.get("temperature_2m"), list) else []
        pops = hourly.get("precipitation_probability") if isinstance(hourly.get("precipitation_probability"), list) else []
        rains = hourly.get("precipitation") if isinstance(hourly.get("precipitation"), list) else []
        current_time = str(current.get("time") or "")
        start_index = next((i for i, value in enumerate(times) if str(value) >= current_time), 0)
        forecast = []
        rain_probs = []
        for i in range(start_index, min(len(times), start_index + 8)):
            temp = temps[i] if i < len(temps) else None
            pop = pops[i] if i < len(pops) else None
            rain = rains[i] if i < len(rains) else None
            if isinstance(pop, (int, float)):
                pop = int(round(max(0, min(100, float(pop)))))
                rain_probs.append(pop)
            forecast.append({
                "time": times[i],
                "temperature": round(float(temp), 1) if isinstance(temp, (int, float)) else None,
                "rain_probability": pop if isinstance(pop, (int, float)) else None,
                "rainfall": round(float(rain), 1) if isinstance(rain, (int, float)) else None,
            })
        wind = current.get("wind_speed_10m", 0)
        rainfall = current.get("precipitation", 0)
        result = {
            "success": True, "status": "MODEL_OUTPUT", "data_type": "MODEL_OUTPUT", "is_current": True,
            "source_name": "Open-Meteo (model-based weather)", "source_url": "https://open-meteo.com/",
            "provider_observed_at": current_time or None, "server_fetched_at": fetched,
            "last_updated": fetched, "cache_age_seconds": 0,
            "temperature": round(float(temperature), 1), "humidity": int(round(float(humidity)),
            "rainfall": round(float(rainfall), 1) if isinstance(rainfall, (int, float)) else None,
            "rain_probability": max(rain_probs) if rain_probs else None,
            "wind": round(float(wind), 1) if isinstance(wind, (int, float)) else None,
            "forecast": forecast,
            "advisories": ["Model-based weather guidance only; confirm conditions locally before spraying or other time-sensitive farm work."],
            "note": "Current conditions are model-based estimates, not a direct local weather-station observation. Open-Meteo data attribution: CC BY 4.0.",
        }
        if fallback_reason:
            result["fallback_note"] = fallback_reason
        _CACHE[cache_key] = (time.monotonic(), dict(result))
        return result
    except (requests.RequestException, ValueError, TypeError, KeyError):
        return {
            "success": False, "status": "UNAVAILABLE", "data_type": "UNAVAILABLE",
            "source_name": "Open-Meteo", "source_url": "https://open-meteo.com/",
            "error": "Weather data could not be fetched for this location right now. Check the city name and retry.",
        }


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
        return _open_meteo_weather(city)
    fetched = _utc_now()
    try:
        response = requests.get("https://api.openweathermap.org/data/2.5/weather",
            params={"q": city, "appid": key, "units": "metric"}, timeout=8)
        if response.status_code == 404:
            return _open_meteo_weather(city, fallback_reason="OpenWeather did not resolve the location.")
        if response.status_code in (401, 403):
            return _open_meteo_weather(city, fallback_reason="OpenWeather credentials are unavailable; used no-key Open-Meteo fallback.")
        if response.status_code == 429:
            return _open_meteo_weather(city, fallback_reason="OpenWeather rate limit reached; used no-key Open-Meteo fallback.")
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
        return _open_meteo_weather(city, fallback_reason="OpenWeather timed out; used no-key Open-Meteo fallback.")
    except (requests.RequestException, ValueError, TypeError, KeyError):
        return _open_meteo_weather(city, fallback_reason="OpenWeather data was unavailable; used no-key Open-Meteo fallback.")
