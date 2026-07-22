"""Config flow for Malta Met Office."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import async_validate_connection
from .const import (
    CONF_UPDATE_INTERVAL,
    DEFAULT_NAME,
    DEFAULT_UPDATE_INTERVAL_MINUTES,
    DOMAIN,
    MIN_UPDATE_INTERVAL_MINUTES,
)
from .exceptions import MaltaMetOfficeError

_LOGGER = logging.getLogger(__name__)


class MaltaMetOfficeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Malta Met Office."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> MaltaMetOfficeOptionsFlow:
        """Create the options flow."""
        return MaltaMetOfficeOptionsFlow()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial zero-config step."""
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        errors: dict[str, str] = {}

        # On first open and on retry, probe the API with no user input required.
        try:
            session = async_get_clientsession(self.hass)
            await async_validate_connection(session)
        except MaltaMetOfficeError as err:
            _LOGGER.warning("Malta Met Office connection failed: %s", err)
            errors["base"] = "cannot_connect"
        except Exception:
            _LOGGER.exception("Unexpected Malta Met Office setup error")
            errors["base"] = "unknown"
        else:
            return self.async_create_entry(title=DEFAULT_NAME, data={})

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({}),
            errors=errors,
        )


class MaltaMetOfficeOptionsFlow(config_entries.OptionsFlow):
    """Handle Malta Met Office options."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            minutes = user_input[CONF_UPDATE_INTERVAL]
            if minutes < MIN_UPDATE_INTERVAL_MINUTES:
                errors[CONF_UPDATE_INTERVAL] = "update_interval_too_low"
            else:
                return self.async_create_entry(
                    title="",
                    data={CONF_UPDATE_INTERVAL: minutes},
                )

        current = self.config_entry.options.get(
            CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL_MINUTES
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_UPDATE_INTERVAL, default=current): int,
                }
            ),
            errors=errors,
        )
