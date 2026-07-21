# Malta Met Office for Home Assistant

A custom Home Assistant integration that provides a weather entity using forecast data from Malta Met Office.

## Features

- Weather entity for Malta Met Office
- Current conditions (temperature, humidity, pressure, wind, visibility)
- Daily 7-day forecast
- Weather warnings as entity attributes when available
- Zero-config setup (no account or API key)
- Automatic updates every 6 hours
- Cloud polling via Home Assistant config flow
- HACS-compatible installation

## Data Source

The integration uses publicly available JSON APIs from Malta Met Office (via `content.maltametoffice.com`), the same backend that powers:

https://maltametoffice.com/en/forecast/

## Installation with HACS

1. Open HACS.
2. Go to Integrations.
3. Open the three-dot menu.
4. Choose Custom repositories.
5. Add this repository URL.
6. Category: Integration.
7. Install **Malta Met Office**.
8. Restart Home Assistant.
9. Go to **Settings → Devices & services**.
10. Add Integration → **Malta Met Office**.

No further configuration is required. The integration connects automatically.

## Configuration

There are no user-facing setup options. After adding the integration, Home Assistant creates:

- Device: **Malta Met Office**
- Entity: `weather.malta_met_office`

Data is refreshed automatically every **6 hours**.

## Notes

This integration is unofficial and is not affiliated with, endorsed by, or supported by Malta Met Office or Malta International Airport.

If the Malta Met Office website or API changes, parsing may break.

## Troubleshooting

If the entity becomes unavailable:

1. Check Home Assistant logs.
2. Verify that https://maltametoffice.com/en/forecast/ is reachable.
3. Open an issue with diagnostics output (Settings → Devices & services → Malta Met Office → Download diagnostics).
