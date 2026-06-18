"""Tracefy device tracker – shows bike on the HA map."""
from __future__ import annotations

from homeassistant.components.device_tracker import SourceType, TrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import TracefyCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: TracefyCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        TracefyTrackerEntity(coordinator, entity_id)
        for entity_id in coordinator.data
    )


class TracefyTrackerEntity(CoordinatorEntity, TrackerEntity):
    """One tracker per bike."""

    _attr_has_entity_name = True
    _attr_name = None  # device name is used

    def __init__(self, coordinator: TracefyCoordinator, entity_id: str) -> None:
        super().__init__(coordinator)
        self._entity_id = entity_id
        self._attr_unique_id = f"{entity_id}_tracker"

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
    def latitude(self) -> float | None:
        pos = self._data.get("device_data", {}).get("position", {})
        return pos.get("latitude")

    @property
    def longitude(self) -> float | None:
        pos = self._data.get("device_data", {}).get("position", {})
        return pos.get("longitude")

    @property
    def source_type(self) -> SourceType:
        return SourceType.GPS

    @property
    def icon(self) -> str:
        return "mdi:bicycle"

    @property
    def extra_state_attributes(self) -> dict:
        dd = self._data.get("device_data", {})
        return {
            "direction": dd.get("direction"),
            "speed_kmh": dd.get("speed"),
            "gps_fix": dd.get("fix"),
            "last_seen": dd.get("last_seen_at"),
            "investigation_status": self._data.get("investigation_status"),
            "frame_number": self._data.get("frame_number"),
            "imei": self._data.get("imei"),
        }
