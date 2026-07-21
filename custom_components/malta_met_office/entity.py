"""Shared entity helpers for Malta Met Office."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo

from .const import DEFAULT_NAME, DOMAIN, MANUFACTURER


def device_info(entry: ConfigEntry) -> DeviceInfo:
    """Return shared device info for all Malta Met Office entities."""
    return DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=DEFAULT_NAME,
        manufacturer=MANUFACTURER,
        entry_type=DeviceEntryType.SERVICE,
    )
