"""Tracefy sensors."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfLength, UnitOfSpeed
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import TracefyCoordinator


def _parse_dt(value: str | None) -> datetime | None:
    """Parse Tracefy datetime string to timezone-aware datetime.

    Tracefy returns strings like '2026-06-18 16:00:26' (space separator, no
    timezone).  Home Assistant requires timezone-aware datetimes for TIMESTAMP
    sensors — without tzinfo HA marks the entity as unavailable.
    We treat the value as UTC (which is what the Tracefy API uses).
    """
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace(" ", "T"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, TypeError):
        return None


@dataclass(frozen=True)
class TracefySensorDescription(SensorEntityDescription):
    value_fn: object = None


SENSORS: list[TracefySensorDescription] = [
    TracefySensorDescription(
        key="speed",
        translation_key="speed",
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        device_class=SensorDeviceClass.SPEED,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.get("device_data", {}).get("speed"),
    ),
    TracefySensorDescription(
        key="distance",
        translation_key="distance",
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda d: round(int(d.get("distance", 0)) / 1000, 2),
    ),
    TracefySensorDescription(
        key="last_seen",
        translation_key="last_seen",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=lambda d: _parse_dt(d.get("device_data", {}).get("last_seen_at")),
    ),
    TracefySensorDescription(
        key="direction",
        translation_key="direction",
        native_unit_of_measurement="°",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.get("device_data", {}).get("direction"),
    ),
    TracefySensorDescription(
        key="gps_fix",
        translation_key="gps_fix",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.get("device_data", {}).get("fix"),
        icon="mdi:crosshairs-gps",
    ),
    TracefySensorDescription(
        key="investigation_status",
        translation_key="investigation_status",
        value_fn=lambda d: d.get("investigation_status"),
        icon="mdi:shield-search",
    ),
]


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: TracefyCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        TracefySensorEntity(coordinator, entity_id, description)
        for entity_id in coordinator.data
        for description in SENSORS
    )


class TracefySensorEntity(CoordinatorEntity, SensorEntity):
    """A sensor for one data point of one bike."""

    _attr_has_entity_name = True
    entity_description: TracefySensorDescription

    def __init__(
        self,
        coordinator: TracefyCoordinator,
        entity_id: str,
        description: TracefySensorDescription,
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
    def native_value(self):
        return self.entity_description.value_fn(self._data)
