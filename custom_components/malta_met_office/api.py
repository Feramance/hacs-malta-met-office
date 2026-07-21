"""API client and parsers for Malta Met Office."""

from __future__ import annotations

from datetime import datetime
from http.cookies import SimpleCookie
from typing import Any
from urllib.parse import unquote

import aiohttp
from aiohttp import ClientSession

from .const import (
    API_BASE_URL,
    CSRF_COOKIE_PATH,
    CURRENT_REPORT_PATH,
    FORECAST_PAGE_URL,
    FORECAST_PATH,
    SITE_ORIGIN,
    SITE_REFERER,
    USER_AGENT,
    WARNINGS_PATH,
)
from .exceptions import (
    MaltaMetOfficeConnectionError,
    MaltaMetOfficeEndpointError,
    MaltaMetOfficeError,
    MaltaMetOfficeParseError,
)
from .models import MaltaMetForecast, MaltaMetWarning, MaltaMetWeatherData

WIND_BEARINGS: dict[str, float] = {
    "N": 0,
    "NNE": 22.5,
    "NE": 45,
    "ENE": 67.5,
    "E": 90,
    "ESE": 112.5,
    "SE": 135,
    "SSE": 157.5,
    "S": 180,
    "SSW": 202.5,
    "SW": 225,
    "WSW": 247.5,
    "W": 270,
    "WNW": 292.5,
    "NW": 315,
    "NNW": 337.5,
}


def map_condition(native: str | None) -> str | None:
    """Map Malta Met Office condition text to Home Assistant condition."""
    if not native:
        return None

    value = native.lower().strip()

    if "thunder" in value and ("rain" in value or "shower" in value):
        return "lightning-rainy"
    if "thunder" in value or "lightning" in value:
        return "lightning"
    if "hail" in value:
        return "hail"
    if "snow" in value:
        return "snowy"
    if "pouring" in value or "heavy rain" in value:
        return "pouring"
    if "rain" in value or "shower" in value:
        return "rainy"
    if "fog" in value or "mist" in value or "haze" in value:
        return "fog"
    if "partly" in value:
        return "partlycloudy"
    if "cloudy" in value or "overcast" in value:
        return "cloudy"
    if "wind" in value:
        return "windy"
    if "sunny" in value or "fine" in value or "clear" in value or "hot" in value:
        return "sunny"

    return None


def parse_wind_bearing_from_direction(direction: str | None) -> float | None:
    """Convert compass direction to bearing degrees."""
    if not direction:
        return None

    cleaned = direction.strip().upper()
    if cleaned in {"VAR", "VRB", "VARIABLE"}:
        return None

    return WIND_BEARINGS.get(cleaned)


def _to_float(value: Any) -> float | None:
    """Convert a value to float if possible."""
    if value is None or value == "":
        return None
    try:
        return float(str(value).replace("+", "").strip())
    except (TypeError, ValueError):
        return None


def _to_int(value: Any) -> int | None:
    """Convert a value to int if possible."""
    number = _to_float(value)
    if number is None:
        return None
    return int(round(number))


def _request_headers(xsrf_token: str | None = None) -> dict[str, str]:
    """Build request headers expected by the Malta Met Office API."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json, text/plain, */*",
        "Origin": SITE_ORIGIN,
        "Referer": SITE_REFERER,
        "X-Requested-With": "XMLHttpRequest",
    }
    if xsrf_token:
        headers["X-XSRF-TOKEN"] = xsrf_token
    return headers


def _extract_xsrf_token(session: ClientSession) -> str | None:
    """Extract and decode the XSRF token from the cookie jar."""
    for cookie in session.cookie_jar:
        if cookie.key == "XSRF-TOKEN":
            return unquote(cookie.value)
    return None


def _xsrf_from_set_cookie(response: aiohttp.ClientResponse) -> str | None:
    """Fallback: parse XSRF token from Set-Cookie headers."""
    raw_cookies = response.headers.getall("Set-Cookie", [])
    for raw in raw_cookies:
        parsed = SimpleCookie()
        parsed.load(raw)
        if "XSRF-TOKEN" in parsed:
            return unquote(parsed["XSRF-TOKEN"].value)
    return None


async def async_ensure_csrf(session: ClientSession) -> str:
    """Ensure a CSRF session cookie and return the XSRF token."""
    url = f"{API_BASE_URL}{CSRF_COOKIE_PATH}"
    try:
        async with session.get(
            url,
            headers=_request_headers(),
            timeout=aiohttp.ClientTimeout(total=20),
            allow_redirects=True,
        ) as response:
            if response.status not in (200, 204):
                raise MaltaMetOfficeConnectionError(
                    f"CSRF cookie request failed with status {response.status}"
                )
            token = _extract_xsrf_token(session) or _xsrf_from_set_cookie(response)
            if not token:
                raise MaltaMetOfficeConnectionError(
                    "CSRF cookie request did not return an XSRF token"
                )
            return token
    except MaltaMetOfficeError:
        raise
    except Exception as err:
        raise MaltaMetOfficeConnectionError(str(err)) from err


async def async_fetch_json(
    session: ClientSession,
    path: str,
    *,
    xsrf_token: str,
) -> Any:
    """Fetch JSON from a Malta Met Office API path."""
    url = f"{API_BASE_URL}{path}"
    try:
        async with session.get(
            url,
            headers=_request_headers(xsrf_token),
            timeout=aiohttp.ClientTimeout(total=20),
            allow_redirects=True,
        ) as response:
            if response.status >= 400:
                text = await response.text()
                raise MaltaMetOfficeEndpointError(
                    f"Endpoint {path} returned {response.status}: {text[:200]}"
                )
            return await response.json(content_type=None)
    except MaltaMetOfficeError:
        raise
    except Exception as err:
        raise MaltaMetOfficeConnectionError(str(err)) from err


def parse_current_report(payload: dict[str, Any]) -> dict[str, Any]:
    """Parse current weather fields from the current-report payload."""
    report = payload.get("current_report") or {}
    data = report.get("data") or {}
    if not isinstance(data, dict) or not data:
        raise MaltaMetOfficeParseError("Current report payload missing data")

    native_condition = None
    condition_obj = data.get("condition")
    if isinstance(condition_obj, dict):
        native_condition = condition_obj.get("label")
    elif isinstance(condition_obj, str):
        native_condition = condition_obj

    wind_bearing = _to_float(data.get("wind_direction_deg"))
    if wind_bearing is None:
        wind_bearing = parse_wind_bearing_from_direction(data.get("wind_direction"))

    return {
        "condition": map_condition(native_condition),
        "native_condition": native_condition,
        "temperature": _to_float(data.get("current_temperature")),
        "apparent_temperature": _to_float(data.get("feels_like")),
        "humidity": _to_int(data.get("relative_humidity")),
        "pressure": _to_float(data.get("atmospheric_pressure")),
        "wind_speed": _to_float(data.get("wind_speed")),
        "wind_bearing": wind_bearing,
        "visibility": _to_float(data.get("visibility")),
        "dew_point": _to_float(data.get("dew_point")),
        "last_updated": report.get("last_updated"),
    }


def parse_forecast(payload: dict[str, Any]) -> list[MaltaMetForecast]:
    """Parse daily forecast entries from the 7-day forecast payload."""
    days = payload.get("days")
    if not isinstance(days, list) or not days:
        raise MaltaMetOfficeParseError("Forecast payload missing days")

    forecasts: list[MaltaMetForecast] = []
    for day in days:
        if not isinstance(day, dict):
            continue

        date_info = day.get("date") or {}
        date_str = (
            date_info.get("date_default") if isinstance(date_info, dict) else None
        )
        forecast_dt: datetime | None = None
        if date_str:
            try:
                forecast_dt = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                forecast_dt = None

        native_condition = None
        condition_obj = day.get("condition")
        if isinstance(condition_obj, dict):
            native_condition = condition_obj.get("label")
        elif isinstance(condition_obj, str):
            native_condition = condition_obj

        forecasts.append(
            MaltaMetForecast(
                datetime=forecast_dt,
                condition=map_condition(native_condition),
                native_condition=native_condition,
                temperature=_to_float(day.get("high")),
                templow=_to_float(day.get("low")),
                wind_bearing=parse_wind_bearing_from_direction(
                    day.get("wind_direction")
                ),
            )
        )

    if not forecasts:
        raise MaltaMetOfficeParseError("No usable forecast days found")

    return forecasts


def parse_warnings(payload: Any) -> list[MaltaMetWarning]:
    """Parse weather warnings payload."""
    if not isinstance(payload, list):
        return []

    warnings: list[MaltaMetWarning] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        warnings.append(
            MaltaMetWarning(
                label=item.get("label"),
                level=item.get("level"),
                message=item.get("warning"),
                until=item.get("until_formatted") or item.get("until"),
            )
        )
    return warnings


def parse_weather_payloads(
    current_payload: dict[str, Any],
    forecast_payload: dict[str, Any],
    warnings_payload: Any | None = None,
) -> MaltaMetWeatherData:
    """Combine API payloads into MaltaMetWeatherData."""
    current = parse_current_report(current_payload)
    forecasts = parse_forecast(forecast_payload)
    warnings = parse_warnings(warnings_payload) if warnings_payload is not None else []

    if current["temperature"] is None and not forecasts:
        raise MaltaMetOfficeParseError("No usable weather data found")

    return MaltaMetWeatherData(
        condition=current["condition"],
        native_condition=current["native_condition"],
        temperature=current["temperature"],
        apparent_temperature=current["apparent_temperature"],
        humidity=current["humidity"],
        pressure=current["pressure"],
        wind_speed=current["wind_speed"],
        wind_bearing=current["wind_bearing"],
        visibility=current["visibility"],
        dew_point=current["dew_point"],
        last_updated=current["last_updated"],
        forecasts=forecasts,
        warnings=warnings,
        raw={
            "source": FORECAST_PAGE_URL,
            "parser": "json_api",
            "api_base": API_BASE_URL,
            "forecast_count": len(forecasts),
            "warning_count": len(warnings),
        },
    )


async def async_get_weather_data(session: ClientSession) -> MaltaMetWeatherData:
    """Fetch and parse Malta Met Office weather data."""
    xsrf_token = await async_ensure_csrf(session)

    current_payload = await async_fetch_json(
        session, CURRENT_REPORT_PATH, xsrf_token=xsrf_token
    )
    forecast_payload = await async_fetch_json(
        session, FORECAST_PATH, xsrf_token=xsrf_token
    )

    warnings_payload: Any | None
    try:
        warnings_payload = await async_fetch_json(
            session, WARNINGS_PATH, xsrf_token=xsrf_token
        )
    except MaltaMetOfficeError:
        warnings_payload = None

    if not isinstance(current_payload, dict):
        raise MaltaMetOfficeEndpointError("Current report response was not an object")
    if not isinstance(forecast_payload, dict):
        raise MaltaMetOfficeEndpointError("Forecast response was not an object")

    return parse_weather_payloads(current_payload, forecast_payload, warnings_payload)


async def async_validate_connection(session: ClientSession) -> None:
    """Validate that the Malta Met Office API is reachable."""
    xsrf_token = await async_ensure_csrf(session)
    payload = await async_fetch_json(
        session, CURRENT_REPORT_PATH, xsrf_token=xsrf_token
    )
    if not isinstance(payload, dict):
        raise MaltaMetOfficeEndpointError("Current report response was not an object")
    parse_current_report(payload)
