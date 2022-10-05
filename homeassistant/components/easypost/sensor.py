"""A platform which allows you to get information from EasyPost."""
from __future__ import annotations

import datetime
from collections.abc import Callable
from dataclasses import dataclass
from typing import cast, List

import easypost

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory, DeviceInfo, EntityDescription
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType, StateType
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DEFAULT_NAME,
    DOMAIN,
    SERVICE_ADD_TRACKER,
    SERVICE_ADD_TRACKER_SCHEMA,
)
from .coordinator import EasyPostDataUpdateCoordinator
from .services import handle_add_tracker, register_services
from ...const import CONF_API_KEY


def get_last_location(
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


def get_last_update_time(
        tracker: easypost.Tracker
) -> str | None:
    """Get last update time."""
    value = None
    if tracker.tracking_details:
        last_location_update = tracker.tracking_details[-1]
        update_time = last_location_update.datetime
        value = from_date(date=update_time)
    return value


def from_date(date: datetime.datetime, template: str = "%Y-%m-%d %H:%M") -> str | None:
    if date:
        if isinstance(date, datetime.datetime):
            return date.strftime(template)
        if isinstance(date, str):
            return date
    return None


class EasyPostEntity(CoordinatorEntity[EasyPostDataUpdateCoordinator]):
    """Defines a base EasyPost entity."""

    _attr_has_entity_name = True

    def __init__(
            self,
            coordinator: EasyPostDataUpdateCoordinator,
            description: EntityDescription
    ) -> None:
        """Initialize the Tautulli entity."""
        super().__init__(coordinator)
        entry_id = coordinator.config_entry.entry_id
        self._attr_unique_id = f"{entry_id}_{description.key}"
        self.entity_description = description
        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, entry_id)},
            manufacturer=DEFAULT_NAME,
            name=DEFAULT_NAME,
        )


class EasyPostSensor(EasyPostEntity, SensorEntity):
    """Representation of an EasyPost sensor."""

    entity_description: EasyPostSensorEntityDescription

    def __init__(
            self,
            coordinator: EasyPostDataUpdateCoordinator,
            description: EntityDescription,
    ) -> None:
        """Initialize the EasyPost sensor."""
        super().__init__(coordinator, description)
        entry_id = coordinator.config_entry.entry_id
        self._attr_unique_id = f"{entry_id}_{description.key}"

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        return self.entity_description.value_fn(None, None, self.entity_description.key)


@dataclass
class EasyPostSensorEntityMixin:
    """Mixin for EasyPost sensor."""

    value_fn: Callable[[None, None, str], StateType]


@dataclass
class EasyPostSensorEntityDescription(
    SensorEntityDescription, EasyPostSensorEntityMixin
):
    """Describes a EasyPost sensor."""


SENSOR_TYPES: tuple[EasyPostSensorEntityDescription, ...] = (
    EasyPostSensorEntityDescription(
        icon="mdi:package-variant-closed",
        key="tracker_count",
        name="Tracker Count",
        native_unit_of_measurement="Trackers",
        entity_category=None,
        entity_registry_enabled_default=True,
        state_class=SensorStateClass.TOTAL,
        value_fn=lambda trackers, _, __: cast(int, len(trackers)),
    ),
)


class EasyPostTrackerSensor(EasyPostEntity, SensorEntity):
    """Representation of an EasyPost tracker sensor."""

    entity_description: EasyPostTrackerSensorEntityDescription

    def __init__(
            self,
            coordinator: EasyPostDataUpdateCoordinator,
            description: EntityDescription,
            tracker: easypost.Tracker,
    ) -> None:
        """Initialize the EasyPost tracker sensor."""
        super().__init__(coordinator, description)
        entry_id = coordinator.config_entry.entry_id
        self._attr_unique_id = f"{entry_id}_{tracker.id}_{description.key}"

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if self.coordinator.trackers:
            for tracker in self.coordinator.trackers:
                return self.entity_description.value_fn(tracker)
        return None


@dataclass
class EasyPostTrackerSensorEntityMixin:
    """Mixin for EasyPost tracker sensor."""

    value_fn: Callable[[easypost.Tracker], StateType]


@dataclass
class EasyPostTrackerSensorEntityDescription(
    SensorEntityDescription, EasyPostTrackerSensorEntityMixin
):
    """Describes a EasyPost tracker sensor."""


TRACKER_SENSOR_TYPES: tuple[EasyPostTrackerSensorEntityDescription, ...] = (
    EasyPostTrackerSensorEntityDescription(
        icon=None,
        key="id",
        name="Id",
        native_unit_of_measurement=None,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda tracker: tracker.id,
    ),
    EasyPostTrackerSensorEntityDescription(
        icon=None,
        key="last_updated",
        name="Last Updated",
        native_unit_of_measurement=None,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda tracker: from_date(date=tracker.updated_at, template="%Y-%m-%d")
    ),
    EasyPostTrackerSensorEntityDescription(
        icon="mdi:barcode",
        key="code",
        name="Tracking Code",
        native_unit_of_measurement=None,
        entity_category=None,
        entity_registry_enabled_default=True,
        value_fn=lambda tracker: tracker.tracking_code,
    ),
    EasyPostTrackerSensorEntityDescription(
        icon="mdi:information-outline",
        key="status",
        name="Status",
        native_unit_of_measurement=None,
        entity_category=None,
        entity_registry_enabled_default=True,
        value_fn=lambda tracker: tracker.status,
    ),
    EasyPostTrackerSensorEntityDescription(
        icon="mdi:map-marker",
        key="location",
        name="Last Location",
        native_unit_of_measurement=None,
        entity_category=None,
        entity_registry_enabled_default=True,
        value_fn=lambda tracker: get_last_location(tracker=tracker),
    ),
    EasyPostTrackerSensorEntityDescription(
        icon="mdi:update",
        key="last_status_update",
        name="Last Status Update",
        native_unit_of_measurement=None,
        entity_category=None,
        entity_registry_enabled_default=True,
        value_fn=lambda tracker: get_last_update_time(tracker=tracker),
    ),
    EasyPostTrackerSensorEntityDescription(
        icon="mdi:weight",
        key="weight",
        name="Weight",
        native_unit_of_measurement="Ounces",
        entity_category=None,
        entity_registry_enabled_default=True,
        value_fn=lambda tracker: cast(float, tracker.weight),
    ),
    EasyPostTrackerSensorEntityDescription(
        icon="mdi:calendar-range",
        key="delivery_date",
        name="Delivery Date",
        native_unit_of_measurement=None,
        entity_category=None,
        entity_registry_enabled_default=True,
        value_fn=lambda tracker: from_date(date=tracker.est_delivery_date, template="%Y-%m-%d")
    ),
    EasyPostTrackerSensorEntityDescription(
        icon="mdi:truck",
        key="carrier",
        name="Carrier",
        native_unit_of_measurement=None,
        entity_category=None,
        entity_registry_enabled_default=True,
        value_fn=lambda tracker: tracker.carrier,
    ),
    EasyPostTrackerSensorEntityDescription(
        icon="mdi:link",
        key="link",
        name="Link",
        native_unit_of_measurement=None,
        entity_category=None,
        entity_registry_enabled_default=True,
        value_fn=lambda tracker: tracker.public_url,
    ),
)


async def async_setup_platform(
        hass: HomeAssistant,
        config: ConfigType,
        async_add_entities: AddEntitiesCallback,
        discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Initialize the EasyPost platform."""
    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_IMPORT}, data=config
        )
    )

    await register_services(hass, config)


async def async_setup_entry(
        hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up EasyPost sensors."""
    coordinator: EasyPostDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: List[EasyPostSensor | EasyPostTrackerSensor] = []
    # Add general EasyPost sensors
    for description in SENSOR_TYPES:
        entities.append(
            EasyPostSensor(coordinator, description)
        )
    # Add EasyPost tracker sensor for each valid tracker
    if coordinator.trackers:
        for tracker in coordinator.trackers:
            for description in TRACKER_SENSOR_TYPES:
                entities.append(
                    EasyPostTrackerSensor(coordinator, description, tracker)
                )
    async_add_entities(entities)
