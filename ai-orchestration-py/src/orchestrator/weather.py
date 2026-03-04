"""Weather client — OpenWeatherMap integration, advice engine, DB cache."""

from __future__ import annotations

import logging
import os
from typing import Any

import httpx

from . import db

logger = logging.getLogger(__name__)

OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
CACHE_TTL_MINUTES = 15


# ── Helpers ──────────────────────────────────────────────────────────────────


def _get_api_key() -> str:
    key = os.environ.get("OPENWEATHER_API_KEY")
    if not key:
        raise RuntimeError(
            "OPENWEATHER_API_KEY is not set. Add it to the repo-root .env file."
        )
    return key


def _location_key(lat: float, lon: float) -> str:
    """Round to 2 decimals for a stable cache key (~1 km granularity)."""
    return f"{lat:.2f},{lon:.2f}"


def _estimate_rain_prob(data: dict) -> float:
    """Best-effort rain probability from the current-weather response."""
    if "rain" in data:
        return 0.90

    main = (data.get("weather") or [{}])[0].get("main", "").lower()
    if main in ("rain", "drizzle", "thunderstorm"):
        return 0.80
    if main in ("snow", "sleet"):
        return 0.70

    clouds = (data.get("clouds") or {}).get("all", 0)
    if clouds > 85:
        return 0.30
    if clouds > 60:
        return 0.15
    return 0.0


# ── API client ───────────────────────────────────────────────────────────────


def get_weather(lat: float, lon: float) -> dict[str, Any]:
    """Fetch current weather (imperial units).

    Returns a normalised dict cached for ``CACHE_TTL_MINUTES``.
    Raises ``RuntimeError`` on config or network errors.
    """
    loc_key = _location_key(lat, lon)

    cached = db.weather_cache_get(location_key=loc_key)
    if cached is not None:
        logger.info("Weather cache hit for %s", loc_key)
        return cached

    api_key = _get_api_key()

    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(
                OPENWEATHER_URL,
                params={"lat": lat, "lon": lon, "appid": api_key, "units": "imperial"},
            )
            resp.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise RuntimeError(
            f"OpenWeatherMap returned HTTP {exc.response.status_code}"
        ) from exc
    except httpx.RequestError as exc:
        raise RuntimeError(f"Failed to reach OpenWeatherMap: {exc}") from exc

    data = resp.json()

    result: dict[str, Any] = {
        "temp_f": data["main"]["temp"],
        "feels_like_f": data["main"]["feels_like"],
        "humidity": data["main"]["humidity"],
        "wind_mph": data["wind"]["speed"],
        "rain_prob": _estimate_rain_prob(data),
        "condition": data["weather"][0]["description"],
        "location_name": data.get("name", ""),
    }

    db.weather_cache_set(
        location_key=loc_key, forecast=result, ttl_minutes=CACHE_TTL_MINUTES
    )
    logger.info("Fetched & cached weather for %s", loc_key)
    return result


# ── Advice engine ────────────────────────────────────────────────────────────

_CATEGORIES: list[tuple[float, str, str]] = [
    (50, "Cold", "Heavy coat, layers, and warm accessories"),
    (60, "Cool", "Light jacket or sweater"),
    (75, "Mild", "Comfortable layers, long sleeves optional"),
    (85, "Warm", "Light clothing, breathable fabrics"),
]
_HOT = ("Hot", "Minimal layers, sun protection, stay hydrated")


def weather_advice(
    feels_like_f: float, wind_mph: float, rain_prob: float
) -> dict[str, str]:
    """Deterministic clothing recommendation.

    Temperature bands (°F): Cold ≤50 | Cool 51-60 | Mild 61-75 | Warm 76-85 | Hot >85.
    Overrides: rain_prob > 0.40 → umbrella, wind_mph > 15 → windbreaker.
    """
    category, base = _HOT
    for threshold, cat, rec in _CATEGORIES:
        if feels_like_f <= threshold:
            category, base = cat, rec
            break

    extras: list[str] = []
    if rain_prob > 0.40:
        extras.append("bring an umbrella")
    if wind_mph > 15:
        extras.append("add a windbreaker")

    recommendation = base
    if extras:
        recommendation += " — also " + " and ".join(extras)

    return {"category": category, "recommendation": recommendation}
