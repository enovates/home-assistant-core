"""Config flow for the enovates integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, LOGGER
from .modbusenoone import ModbusEnoOne

_LOGGER = logging.getLogger(__name__)

# TODO adjust the data schema to the data that you need
STEP_USER_DATA_SCHEMA = vol.Schema({vol.Required(CONF_HOST): str})


def create_api(hostname) -> ModbusEnoOne | None:
    LOGGER.warning("Creating Enovates Modbus API to: " + hostname)

    try:
        return ModbusEnoOne(hostname)
    except:
        return None


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    api = await hass.async_add_executor_job(create_api, data[CONF_HOST])

    if api is None:
        raise CannotConnect

    LOGGER.info("Successfully connected to {}", data[CONF_HOST])
    return {
        "device_serial": api.get_serial(),
        "host": data[CONF_HOST],
        "model_number": api.get_model_number(),
        "has_lock": api.get_lock_state() != 2
    }


class ConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for enovates."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                validated_input = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(validated_input["device_serial"])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=validated_input["device_serial"], data=validated_input
                )

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
