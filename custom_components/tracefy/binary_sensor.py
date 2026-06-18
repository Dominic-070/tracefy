"""Tracefy binary sensors."""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import TracefyCoordinator


@dataclass(frozen=True)
class TracefyBinarySensorDescription(BinarySensorEntityDescription):
    value_fn: object = None


BINARY_SENSORS: list[TracefyBinarySensorDescription] = [
    TracefyBinarySensorDescription(
        key="moving",
        translation_key="moving",
        device_class=BinarySensorDeviceClass.MOTION,
        value_fn=lambda d: d.get("device_data", {}).get("movement", False),
    ),
    TracefyBinarySensorDescription(
        key="battery_connected",
        translation_key="battery_connected",
        device_class=BinarySensorDeviceClass.BATTERY_CHARGING,
        value_fn=lambda d: d.get("device_data", {}).get("battery_connected", False),
    ),
    TracefyBinarySensorDescription(
        key="in_investigation",
        translation_key="in_investigation",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=lambda d: d.get("investigation_status") != "AVAILABLE",
        icon="mdi:shield-alert",
    ),
]


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: TracefyCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        TracefyBinarySensorEntity(coordinator, entity_id, description)
        for entity_id in coordinator.data
        for description in BINARY_SENSORS
    )


class TracefyBinarySensorEntity(CoordinatorEntity, BinarySensorEntity):
    """A binary sensor for one boolean of one bike."""

    _attr_has_entity_name = True
    entity_description: TracefyBinarySensorDescription

    def __init__(
        self,
        coordinator: TracefyCoordinator,
        entity_id: str,
        description: TracefyBinarySensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self._entity_id = entity_id
        self.entity_description = description
        self._attr_unique_id = f"{entity_id}_{description.key}"

    @property
    def _data(self) -> dict:
        return self.coordinator.data.get(self._entity_id, {})

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._entity_id)},
            name=self._data.get("name", "Tracefy Bike"),
            manufacturer="Tracefy",
            model="GPS Tracker",
        )

    @property
    def is_on(self) -> bool:
        return bool(self.entity_description.value_fn(self._data))
