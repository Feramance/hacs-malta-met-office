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

    assert current["native_condition"] is not None
    assert current["condition"] is not None
    assert current["temperature"] is not None
    assert current["humidity"] is not None
    assert current["pressure"] is not None
    assert current["wind_speed"] is not None


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

    assert data.temperature is not None
    assert data.condition is not None
    assert len(data.forecasts) == 7
    assert data.raw["parser"] == "json_api"
    assert len(data.warnings) >= 1


def test_parse_invalid_current_report() -> None:
    """Invalid current report should raise a parse error."""
    with pytest.raises(MaltaMetOfficeParseError):
        parse_current_report({"current_report": {"data": {}}})


def test_parse_invalid_forecast() -> None:
    """Invalid forecast payload should raise a parse error."""
    with pytest.raises(MaltaMetOfficeParseError):
        parse_forecast({"days": []})
