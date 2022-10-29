"""Data update coordinator for the EasyPost integration."""
from __future__ import annotations

import asyncio
from datetime import timedelta
from typing import List

import easypost

from . import EasyPostApi
from .const import DOMAIN, LOGGER
from ...config_entries import ConfigEntry
from ...core import HomeAssistant
from ...helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed


class EasyPostDataUpdateCoordinator(DataUpdateCoordinator):
    """Data update coordinator for the EasyPost integration."""

    config_entry: ConfigEntry

    def __init__(
            self,
            hass: HomeAssistant,
            api: EasyPostApi,
            update_interval: timedelta
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=update_interval
        )
        self.api = api
        self.trackers: List[easypost.Tracker] | None = None

    async def _async_update_data(self) -> None:
        """Get the latest data from EasyPost via the API."""
        try:
            [self.trackers] = await asyncio.gather(
                *[
                    self.api.async_get_trackers(),
                ]
            )
        except Exception as ex:
            # TODO: Improve this later to handle different exceptions
            raise UpdateFailed(ex) from ex
