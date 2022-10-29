"""The EasyPost component."""

from .api import EasyPostApi
from .const import DOMAIN, EASYPOST_DATA, EASYPOST_CONFIG_ENTRY_SCHEMA, LOGGER, SENSOR_UPDATE_INTERVAL
from .coordinator import EasyPostDataUpdateCoordinator
from .services import register_global_services, register_per_account_services
from ...const import CONF_API_KEY, CONF_NAME, Platform
from ...core import HomeAssistant
from ...helpers import discovery
from ...helpers.typing import ConfigType


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the EasyPost package shipping component."""
    LOGGER.debug("Setting up EasyPost integration")

    # Initialize the configuration data
    hass.data.setdefault(EASYPOST_DATA, {})

    for user_account in config[DOMAIN]:
        # Extract credentials from each user account config entry
        account_name: str = user_account[CONF_NAME]
        api_key: str = user_account[CONF_API_KEY]

        # Create the EasyPost API handler
        easypost_api = EasyPostApi(
            api_key=api_key,
            account_name=account_name
        )

        # Store the API handler in hass.data
        hass.data[EASYPOST_DATA][account_name] = easypost_api

        # Load a sensor platform for each EasyPost account
        hass.async_create_task(
            discovery.async_load_platform(
                hass=hass,
                component=Platform.SENSOR,
                platform=DOMAIN,
                discovered={CONF_NAME: account_name},
                hass_config=config,
            )
        )

        # Start account-specific services
        register_per_account_services(hass=hass, easypost_account_config=user_account)

    # If no configurations entries exist (have been made), setup has failed
    if not hass.data[EASYPOST_DATA]:
        return False

    # Start global (account-agnostic) EasyPost services
    register_global_services(hass=hass, easypost_global_config=config)

    return True
