"""Services for the EasyPost integration."""
from typing import Any

from . import EasyPostApi
from .const import (
    CONF_TRACKING_NUMBER,
    CONF_CARRIER,
    SERVICE_ADD_TRACKER,
    DOMAIN,
    SERVICE_ADD_TRACKER_SCHEMA,
    CARRIER_TRANSLATIONS, LOGGER
)
from ...config_entries import ConfigEntry
from ...const import CONF_API_KEY, CONF_NAME
from ...core import ServiceCall, HomeAssistant
from ...helpers.typing import ConfigType

EASYPOST_GLOBAL_SERVICES = {
}

EASYPOST_PER_ACCOUNT_SERVICES = {
    SERVICE_ADD_TRACKER: [SERVICE_ADD_TRACKER_SCHEMA, "async_easypost_add_tracker", []],
}


async def async_easypost_add_tracker(call: ServiceCall, config: ConfigType, *args: Any) -> None:
    """Call when a user adds an EasyPost tracker via Home Assistant."""

    api_key = config.get(CONF_API_KEY)  # because of global API key, we can only have one account
    account_name = config.get(CONF_NAME)
    api = EasyPostApi(api_key=api_key)

    carrier_name = call.data.get(CONF_CARRIER)
    carrier_key = CARRIER_TRANSLATIONS.get(carrier_name)
    tracking_code = call.data.get(CONF_TRACKING_NUMBER)

    success = await api.async_add_tracker(tracking_code=tracking_code, carrier_key=carrier_key)
    if not success:
        LOGGER.error(
            f"Could not add tracking code {tracking_code} for carrier {carrier_name} to {account_name} EasyPost account.")
    else:
        LOGGER.info(
            f"Added tracking code {tracking_code} for carrier {carrier_name} to {account_name} EasyPost account.")


async def _async_service_handler(services_list: dict, call: ServiceCall, config) -> None:
    args = []
    for arg in services_list[call.service][2]:  # append extra arguments
        args.append(call.data[arg])
    func = globals()[services_list[call.service][1]]  # get function
    await func(call, config, *args)


def register_global_services(
        hass: HomeAssistant,
        easypost_global_config: ConfigType):
    """Register services for the EasyPost integration."""

    # NOTE: All services are user-account-agnostic at call time.
    # User-specific services are registered in register_per_account_services

    for service, (schema, method, extra_fields) in EASYPOST_GLOBAL_SERVICES.items():
        if hass.services.has_service(DOMAIN, service):
            # Skip if service already registered
            continue

        hass.services.async_register(
            domain=DOMAIN,
            service=service,
            service_func=lambda call: _async_service_handler(services_list=EASYPOST_GLOBAL_SERVICES,
                                                             call=call,
                                                             config=easypost_global_config),
            schema=schema
        )


def register_per_account_services(
        hass: HomeAssistant,
        easypost_account_config: ConfigEntry):
    """Register services for the EasyPost integration."""

    # NOTE: All services are user-account-specific at call time.
    # User-agnostic services are registered in register_global_services

    for service, (schema, method, extra_fields) in EASYPOST_PER_ACCOUNT_SERVICES.items():
        if hass.services.has_service(DOMAIN, service):
            # Skip if service already registered
            continue

        hass.services.async_register(
            domain=DOMAIN,
            service=service,
            service_func=lambda call: _async_service_handler(services_list=EASYPOST_PER_ACCOUNT_SERVICES,
                                                             call=call,
                                                             config=easypost_account_config),
            schema=schema
        )
