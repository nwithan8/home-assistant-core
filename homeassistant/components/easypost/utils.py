from datetime import datetime

import easypost


def _get_last_location_for_tracker(
        tracker: easypost.Tracker
) -> str | None:
    """Get last location."""
    value = None
    if tracker.tracking_details:
        last_location_update = tracker.tracking_details[-1]
        location = last_location_update.tracking_location
        city = location.city
        state = location.state
        country = location.country
        value = f"{city}, {state}, {country}"
    return value


def _get_last_update_time_for_tracker(
        tracker: easypost.Tracker
) -> str | None:
    """Get last update time."""
    value = None
    if tracker.tracking_details:
        last_location_update = tracker.tracking_details[-1]
        update_time = last_location_update.datetime
        value = _from_date(date=update_time)
    return value


def _from_date(date: datetime, template: str = "%Y-%m-%d %H:%M") -> str | None:
    if date:
        if isinstance(date, datetime):
            return date.strftime(template)
        if isinstance(date, str):
            return date
    return None
