"""A platform which allows you to get information from EasyPost."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import cast, List

import easypost

from .const import (
    DEFAULT_NAME,
    DOMAIN,
    EASYPOST_DATA,
    SENSOR_UPDATE_INTERVAL,
)
from .coordinator import EasyPostDataUpdateCoordinator
from .utils import _from_date, _get_last_location_for_tracker, _get_last_update_time_for_tracker
from ...components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from ...const import CONF_NAME
from ...core import HomeAssistant
from ...helpers.device_registry import DeviceEntryType
from ...helpers.entity import EntityCategory, DeviceInfo, EntityDescription
from ...helpers.entity_platform import AddEntitiesCallback
from ...helpers.typing import ConfigType, DiscoveryInfoType, StateType
from ...helpers.update_coordinator import CoordinatorEntity


# https://developers.home-assistant.io/docs/integration_fetching_data/
# SCAN_INTERVAL = SENSOR_UPDATE_INTERVAL


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
        value_fn=lambda tracker: _from_date(date=tracker.updated_at, template="%Y-%m-%d")
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
        value_fn=lambda tracker: _get_last_location_for_tracker(tracker=tracker),
    ),
    EasyPostTrackerSensorEntityDescription(
        icon="mdi:update",
        key="last_status_update",
        name="Last Status Update",
        native_unit_of_measurement=None,
        entity_category=None,
        entity_registry_enabled_default=True,
        value_fn=lambda tracker: _get_last_update_time_for_tracker(tracker=tracker),
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
        value_fn=lambda tracker: _from_date(date=tracker.est_delivery_date, template="%Y-%m-%d")
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


# noinspection PyUnusedLocal
async def async_setup_platform(
        hass: HomeAssistant,
        config: ConfigType,
        async_add_entities: AddEntitiesCallback,
        discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the EasyPost sensors for a specific account."""
    if discovery_info is None:
        return

    name = discovery_info[CONF_NAME]
    api_handler = hass.data[EASYPOST_DATA][name]

    # Create coordinator to update data from EasyPost API
    easypost_data_coordinator: EasyPostDataUpdateCoordinator = \
        EasyPostDataUpdateCoordinator(
            hass=hass,
            api=api_handler,
            update_interval=SENSOR_UPDATE_INTERVAL
        )

    entities: List[EasyPostSensor | EasyPostTrackerSensor] = []
    # Add general EasyPost sensors for the account
    for description in SENSOR_TYPES:
        entities.append(
            EasyPostSensor(easypost_data_coordinator, description)
        )
    # Add EasyPost tracker sensor for each valid tracker in the account
    if easypost_data_coordinator.trackers:
        for tracker in easypost_data_coordinator.trackers:
            for description in TRACKER_SENSOR_TYPES:
                entities.append(
                    EasyPostTrackerSensor(easypost_data_coordinator, description, tracker)
                )
    async_add_entities(entities, True)  # True triggers initial data update prior to adding entities
