"""Config flow for EasyPost."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

import voluptuous as vol

from . import EasyPostApi
from .const import DEFAULT_NAME, DOMAIN, EASYPOST_CONFIG_ENTRY_SCHEMA
from ...config_entries import ConfigFlow
from ...const import CONF_API_KEY, CONF_NAME
from ...data_entry_flow import FlowResult


async def validate_input(user_input: dict[str, Any]) -> str | None:
    """Try connecting to EasyPost."""
    key = user_input.get(CONF_API_KEY)

    if key is None:
        return "missing_api_key"

    # noinspection PyTypeChecker
    api = EasyPostApi(api_key=key, account_name=None)
    if not await api.async_test_api():
        return "invalid_api_key"  # TODO: Handle different errors

    return None


class EasyPostConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for EasyPost."""

    VERSION = 1
    CONFIG_SCHEMA = EASYPOST_CONFIG_ENTRY_SCHEMA

    def __init__(self):
        """Initialize EasyPost config flow."""
        self._account_name: str | None = None
        self._api_key: str | None = None

    async def async_step_user(
            self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initiated by the user."""
        if self._async_current_entries():
            # Currently only allow one config entry
            return self.async_abort(reason="single_instance_allowed")

        if user_input is None:
            # Show form
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(self.CONFIG_SCHEMA),
                errors={},
            )

        validation_error: str | None = await validate_input(user_input=user_input)
        if validation_error:
            # Show form again with error(s)
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(self.CONFIG_SCHEMA),  # Fields will be erased
                errors={CONF_API_KEY: validation_error}
            )

        # Store user input data
        self._api_key = user_input[CONF_API_KEY]
        self._account_name = user_input.get(CONF_NAME, DEFAULT_NAME)

        # Save entry as new or update existing
        return await self._async_create_update_easypost_account_entry()

    async def async_step_reauth(self, entry_data: Mapping[str, Any]) -> FlowResult:
        """Handle reauthorization request from Abode."""
        self._account_name = entry_data[CONF_NAME]

        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
            self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle reauthorization flow."""
        if user_input is None:
            # Show form
            return self.async_show_form(
                step_id="reauth_confirm",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_API_KEY): str,
                        vol.Required(CONF_NAME, default=self._account_name): str,
                    }
                ),
            )

        # Store user input data
        self._account_name = user_input.get(CONF_NAME, DEFAULT_NAME)
        self._api_key = user_input[CONF_API_KEY]

        # Save entry as new or update existing
        return await self._async_create_update_easypost_account_entry()

    async def _async_create_update_easypost_account_entry(self) -> FlowResult:
        """Create or update an EasyPost account entry."""
        config_data = {
            CONF_API_KEY: self._api_key,
            CONF_NAME: self._account_name,
        }

        existing_entry = await self.async_set_unique_id(unique_id=self._account_name)
        if existing_entry:
            self.hass.config_entries.async_update_entry(
                entry=existing_entry,
                data=config_data,
            )
            # Reload the EasyPost config entry otherwise devices will remain unavailable
            self.hass.async_create_task(
                self.hass.config_entries.async_reload(entry_id=existing_entry.entry_id)
            )
            return self.async_abort(reason="reauth_successful")

        return self.async_create_entry(
            title=cast(str, self._account_name),
            data=config_data,
        )
