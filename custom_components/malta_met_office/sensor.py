"""Sensor platform for Malta Met Office."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    DEGREE,
    PERCENTAGE,
    UnitOfLength,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN
from .coordinator import MaltaMetOfficeCoordinator
from .entity import device_info
from .models import MaltaMetWeatherData


@dataclass(frozen=True, kw_only=True)
class MaltaMetSensorEntityDescription(SensorEntityDescription):
    """Describes a Malta Met Office sensor."""

    value_fn: Callable[[MaltaMetWeatherData], StateType]
    extra_fn: Callable[[MaltaMetWeatherData], dict[str, Any]] | None = None


SENSOR_DESCRIPTIONS: tuple[MaltaMetSensorEntityDescription, ...] = (
    MaltaMetSensorEntityDescription(
        key="native_condition",
        name="Condition",
        value_fn=lambda data: data.native_condition,
    ),
    MaltaMetSensorEntityDescription(
        key="temperature",
        name="Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda data: data.temperature,
    ),
    MaltaMetSensorEntityDescription(
        key="apparent_temperature",
        name="Feels like",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda data: data.apparent_temperature,
    ),
    MaltaMetSensorEntityDescription(
        key="dew_point",
        name="Dew point",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda data: data.dew_point,
    ),
    MaltaMetSensorEntityDescription(
        key="humidity",
        name="Humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        value_fn=lambda data: data.humidity,
    ),
    MaltaMetSensorEntityDescription(
        key="pressure",
        name="Pressure",
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPressure.HPA,
        value_fn=lambda data: data.pressure,
    ),
    MaltaMetSensorEntityDescription(
        key="sea_level_pressure",
        name="Sea level pressure",
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPressure.HPA,
        value_fn=lambda data: data.sea_level_pressure,
    ),
    MaltaMetSensorEntityDescription(
        key="wind_speed",
        name="Wind speed",
        device_class=SensorDeviceClass.WIND_SPEED,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfSpeed.KNOTS,
        value_fn=lambda data: data.wind_speed,
    ),
    MaltaMetSensorEntityDescription(
        key="wind_bearing",
        name="Wind bearing",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=DEGREE,
        value_fn=lambda data: data.wind_bearing,
    ),
    MaltaMetSensorEntityDescription(
        key="wind_direction",
        name="Wind direction",
        value_fn=lambda data: data.wind_direction,
    ),
    MaltaMetSensorEntityDescription(
        key="visibility",
        name="Visibility",
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        value_fn=lambda data: data.visibility,
    ),
    MaltaMetSensorEntityDescription(
        key="clouds",
        name="Cloud amount",
        value_fn=lambda data: data.clouds,
    ),
    MaltaMetSensorEntityDescription(
        key="uv_index",
        name="UV index",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.uv_index,
    ),
    MaltaMetSensorEntityDescription(
        key="rainfall",
        name="Rainfall",
        device_class=SensorDeviceClass.PRECIPITATION,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfLength.MILLIMETERS,
        value_fn=lambda data: data.rainfall,
    ),
    MaltaMetSensorEntityDescription(
        key="sea_temperature",
        name="Sea temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda data: data.sea_temperature,
    ),
    MaltaMetSensorEntityDescription(
        key="min_air_temperature",
        name="Min air temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda data: data.min_air_temperature,
    ),
    MaltaMetSensorEntityDescription(
        key="max_shade_temperature",
        name="Max shade temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda data: data.max_shade_temperature,
    ),
    MaltaMetSensorEntityDescription(
        key="hours_of_bright_sunshine",
        name="Bright sunshine",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTime.HOURS,
        value_fn=lambda data: data.hours_of_bright_sunshine,
    ),
    MaltaMetSensorEntityDescription(
        key="sunrise",
        name="Sunrise",
        value_fn=lambda data: data.sunrise,
    ),
    MaltaMetSensorEntityDescription(
        key="sunset",
        name="Sunset",
        value_fn=lambda data: data.sunset,
    ),
    MaltaMetSensorEntityDescription(
        key="moon_phase",
        name="Moon phase",
        value_fn=lambda data: data.moon_phase,
    ),
    MaltaMetSensorEntityDescription(
        key="last_updated",
        name="Last updated",
        value_fn=lambda data: data.last_updated,
    ),
    MaltaMetSensorEntityDescription(
        key="rainfall_24h",
        name="Rainfall 24h",
        device_class=SensorDeviceClass.PRECIPITATION,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfLength.MILLIMETERS,
        value_fn=lambda data: data.rainfall_24h,
    ),
    MaltaMetSensorEntityDescription(
        key="rainfall_season_total",
        name="Rainfall season total",
        device_class=SensorDeviceClass.PRECIPITATION,
        state_class=SensorStateClass.TOTAL,
        native_unit_of_measurement=UnitOfLength.MILLIMETERS,
        value_fn=lambda data: data.rainfall_season_total,
    ),
    MaltaMetSensorEntityDescription(
        key="warning_count",
        name="Warning count",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.warning_count,
    ),
    MaltaMetSensorEntityDescription(
        key="active_warning",
        name="Active warning",
        value_fn=lambda data: data.active_warning,
        extra_fn=lambda data: (
            {
                "warnings": [
                    {
                        "label": warning.label,
                        "level": warning.level,
                        "message": warning.message,
                        "until": warning.until,
                    }
                    for warning in data.warnings
                ]
            }
            if data.warnings
            else {}
        ),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Malta Met Office sensors."""
    coordinator: MaltaMetOfficeCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        MaltaMetOfficeSensorEntity(coordinator, entry, description)
        for description in SENSOR_DESCRIPTIONS
    )


class MaltaMetOfficeSensorEntity(
    CoordinatorEntity[MaltaMetOfficeCoordinator], SensorEntity
):
    """Malta Met Office sensor entity."""

    entity_description: MaltaMetSensorEntityDescription
    _attr_has_entity_name = True
    _attr_attribution = ATTRIBUTION

    def __init__(
        self,
        coordinator: MaltaMetOfficeCoordinator,
        entry: ConfigEntry,
        description: MaltaMetSensorEntityDescription,
    ) -> None:
        """Initialize sensor entity."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = device_info(entry)

    @property
    def native_value(self) -> StateType:
        """Return the sensor value."""
        if not self.coordinator.data:
            return None
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return extra attributes when provided by the description."""
        if not self.coordinator.data or self.entity_description.extra_fn is None:
            return None
        attrs = self.entity_description.extra_fn(self.coordinator.data)
        return attrs or None
