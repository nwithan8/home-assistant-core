"""Tests for the EasyPost integration."""

from unittest.mock import AsyncMock, patch

import easypost

from homeassistant.components.easypost.const import DOMAIN
from homeassistant.const import (
    CONF_API_KEY,
    CONTENT_TYPE_JSON,
)
from homeassistant.core import HomeAssistant

from tests.common import MockConfigEntry, load_fixture
from tests.components.easypost.fixtures import get_multiple_trackers
from tests.test_util.aiohttp import AiohttpClientMocker

API_KEY = "abcd"
NAME = "EasyPost"

CONF_DATA = {
    CONF_API_KEY: API_KEY,
}


def patch_easypost_user_retrieval(mocked_easypost) -> AsyncMock:
    """Mock EasyPost user retrieval (API key test) function."""
    # easypost.User.retrieve_method will return a User object
    return patch(
        "easypost.User.retrieve_me",
        return_value=easypost.User(),
    )


def patch_config_flow_validation_easypost_success(mocked_easypost) -> AsyncMock:
    """Mock EasyPost config flow."""
    # validate_input method (called during setup methods) will return None
    return patch(
        "homeassistant.components.easypost.config_flow.validate_input",
        return_value=None,
    )


def patch_config_flow_validation_easypost_missing_key(mocked_easypost) -> AsyncMock:
    """Mock EasyPost config flow."""
    # validate_input method (called during setup methods) will return "missing_api_key"
    return patch(
        "homeassistant.components.easypost.config_flow.validate_input",
        return_value="missing_api_key",
    )


def patch_config_flow_validation_easypost_invalid_key(mocked_easypost) -> AsyncMock:
    """Mock EasyPost config flow."""
    # validate_input method (called during setup methods) will return "invalid_api_key"
    return patch(
        "homeassistant.components.easypost.config_flow.validate_input",
        return_value="invalid_api_key",
    )


def patch_easypost_tracker_list(mocked_easypost) -> AsyncMock:
    """Mock EasyPost tracker all function."""
    # easypost.Tracker.all will return a list of Tracker objects
    return patch(
        "easypost.Tracker.all",
        return_value=get_multiple_trackers(),
    )


def patch_easypost_add_tracker(mocked_easypost) -> AsyncMock:
    """Mock EasyPost tracker create function."""
    # easypost.Tracker.create will return a Tracker object
    return patch(
        "easypost.Tracker.create",
        return_value=easypost.Tracker(),
    )