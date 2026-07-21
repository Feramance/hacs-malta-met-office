"""Constants for the Malta Met Office integration."""

from __future__ import annotations

from datetime import timedelta

DOMAIN = "malta_met_office"

DEFAULT_NAME = "Malta Met Office"
DEFAULT_UPDATE_INTERVAL = timedelta(hours=6)

API_BASE_URL = "https://content.maltametoffice.com"
SITE_ORIGIN = "https://maltametoffice.com"
SITE_REFERER = "https://maltametoffice.com/"
FORECAST_PAGE_URL = "https://maltametoffice.com/en/forecast/"

CSRF_COOKIE_PATH = "/sanctum/csrf-cookie"
CURRENT_REPORT_PATH = "/api/weather-current-report"
FORECAST_PATH = "/api/weather-7day-forecast/current"
WARNINGS_PATH = "/api/weather-warnings"

ATTRIBUTION = "Data provided by Malta Met Office"
MANUFACTURER = "Malta Met Office"

USER_AGENT = (
    "Home Assistant Malta Met Office Integration "
    "(https://www.home-assistant.io/)"
)
