"""Tests for Malta Met Office condition and wind mapping."""

from custom_components.malta_met_office.api import (
    map_condition,
    parse_wind_bearing_from_direction,
)


def test_map_condition() -> None:
    """Test mapping of native condition labels."""
    assert map_condition("Sunny") == "sunny"
    assert map_condition("FINE") == "sunny"
    assert map_condition("HOT & SUNNY") == "sunny"
    assert map_condition("Partly cloudy") == "partlycloudy"
    assert map_condition("Cloudy") == "cloudy"
    assert map_condition("Rain showers") == "rainy"
    assert map_condition("Thunder with rain") == "lightning-rainy"
    assert map_condition("Fog") == "fog"
    assert map_condition(None) is None
    assert map_condition("Mysterious weather") is None


def test_wind_bearing_mapping() -> None:
    """Test compass direction mapping."""
    assert parse_wind_bearing_from_direction("N") == 0
    assert parse_wind_bearing_from_direction("NE") == 45
    assert parse_wind_bearing_from_direction("E") == 90
    assert parse_wind_bearing_from_direction("S") == 180
    assert parse_wind_bearing_from_direction("W") == 270
    assert parse_wind_bearing_from_direction("SSW") == 202.5
    assert parse_wind_bearing_from_direction("VAR") is None
    assert parse_wind_bearing_from_direction(None) is None
