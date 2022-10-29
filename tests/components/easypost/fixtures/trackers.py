from typing import List

import easypost


class TrackingLocation:
    """Mock TrackingLocation."""

    def __init__(self, city: str, state: str, country: str) -> None:
        """Initialize."""
        self.city = city
        self.state = state
        self.country = country


class TrackingDetail:
    """Mock TrackingDetail."""

    def __init__(self, city: str, state: str, country: str, datetime: str) -> None:
        """Initialize."""
        self.tracking_location = TrackingLocation(city=city, state=state, country=country)
        self.datetime = datetime


def get_multiple_trackers() -> List[easypost.Tracker]:
    """Get multiple trackers."""
    trackers = []
    statuses = ["in_transit", "delivered", "return_to_sender"]
    updated_ats = ["2021-01-01 00:00:00", "2021-01-02 00:00:00", "2021-01-03 00:00:00"]
    for i in range(3):
        tracker = easypost.Tracker()

        setattr(tracker, "id", f"tracker_{i}")
        setattr(tracker, "last_updated", updated_ats[i])
        setattr(tracker, "tracking_code", f"{i * 15}")
        setattr(tracker, "status", statuses[i])
        setattr(tracker, "tracking_details", [
            TrackingDetail(city="San Francisco", state="CA", country="US", datetime=updated_ats[i])
        ])
        setattr(tracker, "weight", 10.0)
        setattr(tracker, "est_delivery_date", "2021-01-04 00:00:00")
        setattr(tracker, "carrier", "USPS")
        setattr(tracker, "public_url", "https://easypost.com")

        trackers.append(tracker)
    return trackers


def get_one_tracker() -> easypost.Tracker:
    """Get one tracker."""
    return get_multiple_trackers()[0]
