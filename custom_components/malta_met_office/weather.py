"""Weather platform for Malta Met Office."""

from __future__ import annotations

from typing import Any

from homeassistant.components.weather import (
    Forecast,
    WeatherEntity,
    WeatherEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfLength,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN, FORECAST_PAGE_URL
from .coordinator import MaltaMetOfficeCoordinator
from .entity import device_info


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Malta Met Office weather entity."""
    coordinator: MaltaMetOfficeCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([MaltaMetOfficeWeatherEntity(coordinator, entry)])


class MaltaMetOfficeWeatherEntity(
    CoordinatorEntity[MaltaMetOfficeCoordinator], WeatherEntity
):
    """Malta Met Office weather entity."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_attribution = ATTRIBUTION
    _attr_supported_features = WeatherEntityFeature.FORECAST_DAILY
    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_native_pressure_unit = UnitOfPressure.HPA
    _attr_native_wind_speed_unit = UnitOfSpeed.KNOTS
    _attr_native_precipitation_unit = UnitOfLength.MILLIMETERS
    _attr_native_visibility_unit = UnitOfLength.KILOMETERS

    def __init__(
        self, coordinator: MaltaMetOfficeCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize weather entity."""
        super().__init__(coordinator)
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_weather"
        self._attr_device_info = device_info(entry)

    @property
    def condition(self) -> str | None:
        """Return current condition."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.condition

    @property
    def native_temperature(self) -> float | None:
        """Return current temperature."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.temperature

    @property
    def native_apparent_temperature(self) -> float | None:
        """Return apparent temperature."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.apparent_temperature

    @property
    def humidity(self) -> float | None:
        """Return humidity."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.humidity

    @property
    def native_pressure(self) -> float | None:
        """Return pressure."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.pressure

    @property
    def native_wind_speed(self) -> float | None:
        """Return wind speed."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.wind_speed

    @property
    def wind_bearing(self) -> float | str | None:
        """Return wind bearing."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.wind_bearing

    @property
    def native_visibility(self) -> float | None:
        """Return visibility."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.visibility

    @property
    def native_dew_point(self) -> float | None:
        """Return dew point."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.dew_point

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        attrs: dict[str, Any] = {"source": FORECAST_PAGE_URL}
        data = self.coordinator.data
        if not data:
            return attrs

        attrs["native_condition"] = data.native_condition
        if data.last_updated:
            attrs["last_updated"] = data.last_updated
        if data.warnings:
            attrs["warnings"] = [
                {
                    "label": warning.label,
                    "level": warning.level,
                    "message": warning.message,
                    "until": warning.until,
                }
                for warning in data.warnings
            ]
        return attrs

    async def async_forecast_daily(self) -> list[Forecast] | None:
        """Return daily forecast."""
        if not self.coordinator.data:
            return None

        forecasts: list[Forecast] = []
        for item in self.coordinator.data.forecasts:
            forecast: Forecast = {}
            if item.datetime is not None:
                forecast["datetime"] = item.datetime.isoformat()
            if item.condition is not None:
                forecast["condition"] = item.condition
            if item.temperature is not None:
                forecast["native_temperature"] = item.temperature
            if item.templow is not None:
                forecast["native_templow"] = item.templow
            if item.wind_bearing is not None:
                forecast["wind_bearing"] = item.wind_bearing
            forecasts.append(forecast)

        return forecasts
