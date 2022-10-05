"""Config flow for EasyPost."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import easypost
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_API_KEY
from homeassistant.data_entry_flow import FlowResult

from .const import DEFAULT_NAME, DOMAIN


class EasyPostConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for EasyPost."""

    VERSION = 1

    async def async_step_user(
            self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initiated by the user."""
        errors = {}
        if user_input is not None:
            # User has provided input data
            # Skip if EasyPost is already configured with the same API key
            self._async_abort_entries_match({CONF_API_KEY: user_input[CONF_API_KEY]})
            # Validate input
            if (error := await self.validate_input(user_input)) is None:
                # Input is valid, create entry
                return self.async_create_entry(
                    title=DEFAULT_NAME,
                    data=user_input,
                )
            # Input is invalid, show error
            errors["base"] = error

        user_input = user_input or {}
        data_schema = {
            vol.Required(CONF_API_KEY, default=user_input.get(CONF_API_KEY, "")): str,
        }

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(data_schema),
            errors=errors or {},
        )

    async def async_step_reauth(self, entry_data: Mapping[str, Any]) -> FlowResult:
        """Handle a reauthorization flow request."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
            self, user_input: dict[str, str] | None = None
    ) -> FlowResult:
        """Confirm reauth dialog."""
        errors = {}
        # User has provided input data and configuration already exists
        if user_input is not None and (
                entry := self.hass.config_entries.async_get_entry(self.context["entry_id"])
        ):
            _input = {**entry.data, CONF_API_KEY: user_input[CONF_API_KEY]}
            if (error := await self.validate_input(_input)) is None:
                # Input is valid, update entry
                self.hass.config_entries.async_update_entry(entry, data=_input)
                await self.hass.config_entries.async_reload(entry.entry_id)
                return self.async_abort(reason="reauth_successful")
            errors["base"] = error
        # Show reauth dialog
        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema({vol.Required(CONF_API_KEY): str}),
            errors=errors,
        )

    async def validate_input(self, user_input: dict[str, Any]) -> str | None:
        """Try connecting to EasyPost."""
        key = user_input.get(CONF_API_KEY)
        if key is None:
            return "missing_api_key"
        # Set API key globally
        easypost.api_key = key
        # Test connection
        try:
            easypost_user = easypost.User.retrieve_me()
            if easypost_user is None:
                # API could not pull user, assume invalid API key
                easypost.api_key = None # Reset API key
                return "invalid_api_key"
        except Exception:
            # API threw an exception, assume invalid API key
            easypost.api_key = None  # Reset API key
            return "invalid_api_key"
        easypost.api_key = None  # Reset API key
        return None
