"""Tests for Malta Met Office JSON parsers."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from custom_components.malta_met_office.api import (
    parse_current_report,
    parse_forecast,
    parse_weather_payloads,
)
from custom_components.malta_met_office.exceptions import MaltaMetOfficeParseError

FIXTURES = Path(__file__).parent / "fixtures"


def _load(name: str) -> dict | list:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_parse_current_report_fixture() -> None:
    """Parse the captured current-report fixture."""
    payload = _load("weather-current-report.json")
    assert isinstance(payload, dict)
    current = parse_current_report(payload)

    assert current["native_condition"] == "FINE"
    assert current["condition"] == "sunny"
    assert current["temperature"] == 36.0
    assert current["humidity"] == 29
    assert current["pressure"] == 1014.0
    assert current["sea_level_pressure"] == 1020.0
    assert current["wind_speed"] == 8.0
    assert current["wind_direction"] == "SW"
    assert current["wind_bearing"] == 220.0
    assert current["uv_index"] == 7.0
    assert current["sea_temperature"] == 29.0
    assert current["clouds"] == "CAVOK"
    assert current["sunrise"] == "06:01"
    assert current["sunset"] == "20:15"
    assert current["moon_phase"] == "Waxing Crescent"
    assert current["rainfall"] == 0.0


def test_parse_forecast_fixture() -> None:
    """Parse the captured 7-day forecast fixture."""
    payload = _load("weather-7day-forecast.json")
    assert isinstance(payload, dict)
    forecasts = parse_forecast(payload)

    assert len(forecasts) == 7
    assert forecasts[0].datetime is not None
    assert forecasts[0].temperature is not None
    assert forecasts[0].templow is not None
    assert forecasts[0].native_condition is not None


def test_parse_weather_payloads_combined() -> None:
    """Combine current, forecast, and warnings fixtures."""
    current = _load("weather-current-report.json")
    forecast = _load("weather-7day-forecast.json")
    warnings = _load("weather-warnings.json")
    assert isinstance(current, dict)
    assert isinstance(forecast, dict)

    data = parse_weather_payloads(current, forecast, warnings)

    assert data.temperature == 36.0
    assert data.condition == "sunny"
    assert data.uv_index == 7.0
    assert data.sea_temperature == 29.0
    assert data.rainfall_24h == 0.0
    assert data.rainfall_season_total == 397.4
    assert data.warning_count >= 1
    assert data.active_warning is not None
    assert len(data.forecasts) == 7
    assert data.raw["parser"] == "json_api"
    assert len(data.warnings) >= 1


def test_model_exposes_sensor_fields() -> None:
    """Model should include attributes used by the sensor platform."""
    from custom_components.malta_met_office.models import MaltaMetWeatherData

    expected = {
        "native_condition",
        "temperature",
        "apparent_temperature",
        "dew_point",
        "humidity",
        "pressure",
        "sea_level_pressure",
        "wind_speed",
        "wind_bearing",
        "wind_direction",
        "visibility",
        "clouds",
        "uv_index",
        "rainfall",
        "sea_temperature",
        "min_air_temperature",
        "max_shade_temperature",
        "hours_of_bright_sunshine",
        "sunrise",
        "sunset",
        "moon_phase",
        "last_updated",
        "rainfall_24h",
        "rainfall_season_total",
        "warning_count",
        "active_warning",
    }
    assert expected.issubset(MaltaMetWeatherData.__dataclass_fields__)


def test_parse_invalid_current_report() -> None:
    """Invalid current report should raise a parse error."""
    with pytest.raises(MaltaMetOfficeParseError):
        parse_current_report({"current_report": {"data": {}}})


def test_parse_invalid_forecast() -> None:
    """Invalid forecast payload should raise a parse error."""
    with pytest.raises(MaltaMetOfficeParseError):
        parse_forecast({"days": []})
