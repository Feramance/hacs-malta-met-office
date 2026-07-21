"""Diagnostics support for Malta Met Office."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, FORECAST_PAGE_URL


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for Malta Met Office."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    data = coordinator.data

    return {
        "entry": {
            "title": entry.title,
            "data": dict(entry.data),
        },
        "last_update_success": coordinator.last_update_success,
        "current_condition": data.condition if data else None,
        "native_condition": data.native_condition if data else None,
        "forecast_count": len(data.forecasts) if data and data.forecasts else 0,
        "warning_count": len(data.warnings) if data and data.warnings else 0,
        "source": FORECAST_PAGE_URL,
        "parser": data.raw.get("parser") if data and data.raw else None,
    }
