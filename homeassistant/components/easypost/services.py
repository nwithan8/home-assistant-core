from typing import Any

import easypost

from .const import (
    CONF_TRACKING_NUMBER,
    CONF_CARRIER,
    SERVICE_ADD_TRACKER,
    DOMAIN,
    SERVICE_ADD_TRACKER_SCHEMA,
    CARRIER_TRANSLATIONS, LOGGER
)
from homeassistant.core import ServiceCall, HomeAssistant
from ...const import CONF_API_KEY
from ...helpers import ConfigType

EASYPOST_SERVICES = {
    SERVICE_ADD_TRACKER: [SERVICE_ADD_TRACKER_SCHEMA, "async_add_easypost_tracker", []],
}


async def async_service_handler(call: ServiceCall, config: ConfigType) -> None:
    args = []
    for arg in EASYPOST_SERVICES[call.service][2]:  # append extra arguments
        args.append(call.data[arg])
    func = globals()[EASYPOST_SERVICES[call.service][1]]  # get function
    await func(call, config, *args)


async def async_add_easypost_tracker(call: ServiceCall, config: ConfigType, *args: Any) -> None:
    """Call when a user adds an EasyPost tracker via Home Assistant."""
    easypost.api_key = config.get(CONF_API_KEY)  # because of global API key, we can only have one account
    carrier_name = call.data.get(CONF_CARRIER)
    carrier_key = CARRIER_TRANSLATIONS.get(carrier_name)
    tracking_code = call.data.get(CONF_TRACKING_NUMBER)
    try:
        tracker = easypost.Tracker.create(
            tracking_code=tracking_code,
            carrier=carrier_key,
        )
    except Exception:
        # TODO: handle service call errors
        LOGGER.error(f"Could not add tracking code {tracking_code} for carrier {carrier_name} to EasyPost account.")
        return


async def register_services(
        hass: HomeAssistant,
        config: ConfigType):
    """Register services for the EasyPost integration."""

    for service, (schema, method, extra_fields) in EASYPOST_SERVICES.items():
        hass.services.async_register(
            domain=DOMAIN,
            service=service,
            service_func=lambda call: async_service_handler(call=call, config=config),
            schema=schema
        )
