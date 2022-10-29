from datetime import datetime, timedelta
from typing import List

import easypost


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


class EasyPostApi:
    def __init__(self, api_key: str, account_name: str = None):
        """Construct an EasyPost API connector"""
        self.api_key = api_key
        self.account_name = account_name

    async def async_test_api(self) -> bool:
        """Test the EasyPost API."""
        try:
            await self.async_get_self()
            return True
        except Exception:
            return False

    async def async_get_trackers(self) -> List[easypost.Tracker]:
        """Get the latest tracker data from EasyPost."""
        easypost.api_key = self.api_key  # because of global API key, we can only have one account

        try:
            trackers = easypost.Tracker.all()
            return [tracker for tracker in trackers if valid_tracker(tracker)]
        except easypost.Error:
            raise Exception

    async def async_add_tracker(self, tracking_code: str, carrier_key: str) -> bool:
        """Add a new tracker to EasyPost."""
        easypost.api_key = self.api_key

        try:
            _ = easypost.Tracker.create(
                tracking_code=tracking_code,
                carrier=carrier_key,
            )
            return True
        except easypost.Error:
            return False

    async def async_get_self(self) -> easypost.User:
        """Get the authenticated EasyPost user."""
        easypost.api_key = self.api_key  # because of global API key, we can only have one account

        try:
            return easypost.User.retrieve()
        except easypost.Error:
            raise Exception
