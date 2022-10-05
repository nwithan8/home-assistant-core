"""Data update coordinator for the EasyPost integration."""
from __future__ import annotations

import asyncio
import datetime
from datetime import datetime, timedelta
from typing import List

import easypost

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, LOGGER, MIN_TIME_BETWEEN_UPDATES


def valid_tracker(tracker: easypost.Tracker) -> bool:
    """Check if tracker is valid."""
    status = tracker.status
    last_updated = tracker.updated_at
    # Skip trackers that do not have a last updated date
    if not last_updated:
        return False
    # Check trackers that are not in transit
    if status in ["delivered", "return_to_sender", "failure", "cancelled", "error"]:
        # Skip delivered trackers that are older than 3 days
        if status == "delivered" and last_updated < datetime.now() - timedelta(days=3):
            return False
        # Skip any other trackers that are older than 1 day
        if last_updated < datetime.now() - timedelta(days=1):
            return False
        # Don't skip
        return True
    # Check trackers that are in transit but have not been updated in 30 days
    if last_updated < datetime.now() - timedelta(days=30):
        return False
    # Don't skip
    return True


class EasyPostDataUpdateCoordinator(DataUpdateCoordinator):
    """Data update coordinator for the EasyPost integration."""

    config_entry: ConfigEntry

    def __init__(
            self,
            hass: HomeAssistant,
            api_key: str,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=MIN_TIME_BETWEEN_UPDATES,  # update every hour
        )
        self.api_key = api_key
        self.trackers: List[easypost.Tracker] | None = None

    async def _async_update_data(self) -> None:
        """Get the latest data from EasyPost."""
        try:
            [self.trackers] = await asyncio.gather(
                *[
                    self.async_get_trackers(api_key=self.api_key),
                ]
            )
        except Exception as ex:
            # TODO: Improve this later to handle different exceptions
            raise UpdateFailed(ex) from ex

    async def async_get_trackers(self, api_key: str) -> List[easypost.Tracker]:
        """Get the latest data from EasyPost."""
        easypost.api_key = api_key  # because of global API key, we can only have one account
        try:
            trackers = easypost.Tracker.all()
            return [tracker for tracker in trackers if valid_tracker(tracker)]
        except easypost.Error as ex:
            raise Exception
