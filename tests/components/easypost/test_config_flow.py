"""Test EasyPost config flow."""
from unittest.mock import AsyncMock

from homeassistant import data_entry_flow
from homeassistant.components.easypost import config_flow
from homeassistant.components.easypost.const import DOMAIN
from homeassistant.config_entries import SOURCE_USER
from homeassistant.const import (
    CONF_API_KEY,
    CONF_NAME,
    CONF_SOURCE
)
from homeassistant.core import HomeAssistant
from tests.common import MockConfigEntry
from . import (
    CONF_DATA,
    NAME,
    patch_config_flow_validation_easypost_invalid_key,
    patch_config_flow_validation_easypost_success
)


async def test_flow_user(hass: HomeAssistant) -> None:
    """Test user initiated flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={CONF_SOURCE: SOURCE_USER}
    )
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"] == {}

    with patch_config_flow_validation_easypost_success(AsyncMock()):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input=CONF_DATA,
        )
    await hass.async_block_till_done()

    assert result2["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result2["title"] == NAME
    assert result2["data"] == CONF_DATA


async def test_one_config_allowed(hass: HomeAssistant) -> None:
    """Test that only one EasyPost configuration is allowed."""
    flow = config_flow.EasyPostConfigFlow()
    flow.hass = hass

    MockConfigEntry(
        domain=DOMAIN,
        data={CONF_NAME: "account_2", CONF_API_KEY: "fake_api_key_2"},
    ).add_to_hass(hass)

    step_user_result = await flow.async_step_user()

    assert step_user_result["type"] == data_entry_flow.FlowResultType.ABORT
    assert step_user_result["reason"] == "single_instance_allowed"


async def test_invalid_credentials(hass: HomeAssistant) -> None:
    """Test that invalid credentials throws an error."""
    conf = {CONF_NAME: "account", CONF_API_KEY: "fake_api_key"}

    flow = config_flow.EasyPostConfigFlow()
    flow.hass = hass

    with patch_config_flow_validation_easypost_invalid_key(AsyncMock()) as easypost_mock:
        result = await flow.async_step_user(user_input=conf)
        assert result["errors"] == {"base": "invalid_api_key"}
