"""Data models for Malta Met Office weather data."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class MaltaMetForecast:
    """Single forecast period."""

    datetime: datetime | None = None
    condition: str | None = None
    native_condition: str | None = None
    temperature: float | None = None
    templow: float | None = None
    humidity: int | None = None
    wind_speed: float | None = None
    wind_bearing: float | None = None
    precipitation_probability: int | None = None
    precipitation: float | None = None


@dataclass
class MaltaMetWarning:
    """Weather warning."""

    label: str | None = None
    level: str | None = None
    message: str | None = None
    until: str | None = None


@dataclass
class MaltaMetWeatherData:
    """Current weather and forecast data."""

    condition: str | None = None
    native_condition: str | None = None
    temperature: float | None = None
    apparent_temperature: float | None = None
    humidity: int | None = None
    pressure: float | None = None
    wind_speed: float | None = None
    wind_bearing: float | None = None
    visibility: float | None = None
    dew_point: float | None = None
    last_updated: str | None = None
    forecasts: list[MaltaMetForecast] = field(default_factory=list)
    warnings: list[MaltaMetWarning] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)
