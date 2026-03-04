"""Tests for the weather advice engine (pure function — no API key or DB needed)."""

from __future__ import annotations

from src.orchestrator.weather import weather_advice


def test_cold_category() -> None:
    result = weather_advice(45.0, 5.0, 0.0)
    assert result["category"] == "Cold"
    assert "coat" in result["recommendation"].lower()


def test_cool_category() -> None:
    result = weather_advice(55.0, 5.0, 0.0)
    assert result["category"] == "Cool"
    assert "jacket" in result["recommendation"].lower() or "sweater" in result["recommendation"].lower()


def test_mild_category() -> None:
    result = weather_advice(70.0, 5.0, 0.0)
    assert result["category"] == "Mild"


def test_warm_category() -> None:
    result = weather_advice(80.0, 5.0, 0.0)
    assert result["category"] == "Warm"


def test_hot_category() -> None:
    result = weather_advice(95.0, 5.0, 0.0)
    assert result["category"] == "Hot"
    assert "sun protection" in result["recommendation"].lower()


def test_boundary_cold_cool() -> None:
    assert weather_advice(50.0, 5.0, 0.0)["category"] == "Cold"
    assert weather_advice(51.0, 5.0, 0.0)["category"] == "Cool"


def test_rain_override() -> None:
    result = weather_advice(70.0, 5.0, 0.50)
    assert "umbrella" in result["recommendation"].lower()


def test_no_umbrella_below_threshold() -> None:
    result = weather_advice(70.0, 5.0, 0.35)
    assert "umbrella" not in result["recommendation"].lower()


def test_wind_override() -> None:
    result = weather_advice(70.0, 20.0, 0.0)
    assert "windbreaker" in result["recommendation"].lower()


def test_rain_and_wind_combined() -> None:
    result = weather_advice(60.0, 18.0, 0.60)
    rec = result["recommendation"].lower()
    assert "umbrella" in rec
    assert "windbreaker" in rec
