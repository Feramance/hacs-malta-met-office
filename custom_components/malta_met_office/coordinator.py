"""DataUpdateCoordinator for Malta Met Office."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import async_get_weather_data
from .const import DEFAULT_UPDATE_INTERVAL, DOMAIN
from .exceptions import MaltaMetOfficeError
from .models import MaltaMetWeatherData

_LOGGER = logging.getLogger(__name__)


class MaltaMetOfficeCoordinator(DataUpdateCoordinator[MaltaMetWeatherData]):
    """Coordinator for Malta Met Office data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize coordinator."""
        self.entry = entry
        self.session = async_get_clientsession(hass)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=DEFAULT_UPDATE_INTERVAL,
        )

    async def _async_update_data(self) -> MaltaMetWeatherData:
        """Fetch data from Malta Met Office."""
        try:
            data = await async_get_weather_data(self.session)
        except MaltaMetOfficeError as err:
            raise UpdateFailed(str(err)) from err

        _LOGGER.debug(
            "Parsed Malta Met Office data: condition=%s forecasts=%s",
            data.native_condition,
            len(data.forecasts),
        )
        return data
