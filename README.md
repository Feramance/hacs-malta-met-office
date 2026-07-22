# Malta Met Office for Home Assistant

A custom Home Assistant integration that provides a weather entity and sensors using forecast data from Malta Met Office.

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![Validate](https://github.com/Feramance/malta-met-office/actions/workflows/validate.yml/badge.svg)](https://github.com/Feramance/malta-met-office/actions/workflows/validate.yml)

## Features

- Weather entity for Malta Met Office with daily 7-day forecast
- Sensor entities for all current observation fields
- Current conditions (temperature, humidity, pressure, wind, visibility, UV, sea temperature, and more)
- Rainfall summaries and active weather warnings as sensors
- Zero-config setup (no account or API key)
- Configurable update interval after setup (default 6 hours)
- Cloud polling via Home Assistant config flow
- HACS-compatible installation with GitHub Releases

## Data Source

The integration uses publicly available JSON APIs from Malta Met Office (via `content.maltametoffice.com`), the same backend that powers:

https://maltametoffice.com/en/forecast/

## Installation with HACS

### My Home Assistant

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Feramance&repository=malta-met-office&category=integration)

### Manual HACS steps

1. Open HACS.
2. Go to Integrations.
3. Open the three-dot menu.
4. Choose Custom repositories.
5. Add `https://github.com/Feramance/malta-met-office`.
6. Category: Integration.
7. Install **Malta Met Office**.
8. Restart Home Assistant.
9. Go to **Settings → Devices & services**.
10. Add Integration → **Malta Met Office**.

No further configuration is required to add the integration. It connects automatically.

## Configuration

Setup is zero-config. After adding the integration, Home Assistant creates a **Malta Met Office** device with:

- `weather.malta_met_office` (current conditions + daily forecast)
- Sensors for each observation field, including:
  - Temperature, feels like, dew point, humidity
  - Pressure and sea level pressure
  - Wind speed, bearing, and direction
  - Visibility, cloud amount, UV index
  - Rainfall, 24h rainfall, season total
  - Sea temperature, min/max air temperature
  - Bright sunshine hours, sunrise, sunset, moon phase
  - Condition, last updated, warning count, active warning

### Update interval

Data refreshes every **6 hours** by default. To change this:

1. Go to **Settings → Devices & services → Malta Met Office**.
2. Open **Configure**.
3. Set **Update interval (minutes)**.

The minimum allowed interval is **30 minutes**.

Releases are created automatically when a commit on `main` includes `[major]`, `[minor]`, or `[patch]` in the message.

## Notes

This integration is unofficial and is not affiliated with, endorsed by, or supported by Malta Met Office or Malta International Airport.

Brand images used in Home Assistant are sourced from the public Malta Met Office website and remain the property of Malta Met Office / Malta International Airport.

If the Malta Met Office website or API changes, parsing may break.

## Troubleshooting

If entities become unavailable:

1. Check Home Assistant logs.
2. Verify that https://maltametoffice.com/en/forecast/ is reachable.
3. Open an issue with diagnostics output (Settings → Devices & services → Malta Met Office → Download diagnostics).
