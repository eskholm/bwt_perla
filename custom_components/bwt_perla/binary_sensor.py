from __future__ import annotations
from typing import Any

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    device_info = DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        manufacturer=MANUFACTURER,
        model=MODEL,
        name="BWT Perla",
    )

    entry_id = entry.entry_id
    registry = er.async_get(hass)

    # Pre-register with English, prefixed entity_ids
    registry.async_get_or_create(
        domain="binary_sensor",
        platform=DOMAIN,
        unique_id=f"{entry_id}_error",
        suggested_object_id="bwt_perla_error",
        config_entry=entry,
    )
    registry.async_get_or_create(
        domain="binary_sensor",
        platform=DOMAIN,
        unique_id=f"{entry_id}_out_of_service",
        suggested_object_id="bwt_perla_out_of_service",
        config_entry=entry,
    )

    entities: list[BinarySensorEntity] = [
        BwtErrorBinarySensor(coordinator, entry_id, device_info),
        BwtOutOfServiceBinarySensor(coordinator, entry_id, device_info),
    ]
    async_add_entities(entities)


class _BaseBwtBinary(CoordinatorEntity, BinarySensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry_id: str, fallback_name: str, unique_key: str, translation_key: str, device_info: DeviceInfo):
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._attr_unique_id = f"{entry_id}_{unique_key}"
        self._attr_device_info = device_info
        self._attr_translation_key = translation_key
        self._attr_name = fallback_name  # fallback display name

    @property
    def _data(self) -> dict[str, Any]:
        return self.coordinator.data or {}


class BwtErrorBinarySensor(_BaseBwtBinary):
    _attr_device_class = "problem"

    def __init__(self, coordinator, entry_id: str, device_info: DeviceInfo):
        super().__init__(coordinator, entry_id, "Error", "error", "error", device_info)

    @property
    def is_on(self) -> bool:
        show_error = int(self._data.get("ShowError", 0)) == 1
        active_ids = str(self._data.get("ActiveErrorIDs", "") or "")
        return show_error or (len(active_ids.strip()) > 0)

    @property
    def extra_state_attributes(self) -> dict:
        return {
            "ShowError": self._data.get("ShowError"),
            "ActiveErrorIDs": self._data.get("ActiveErrorIDs"),
        }


class BwtOutOfServiceBinarySensor(_BaseBwtBinary):
    _attr_device_class = "problem"

    def __init__(self, coordinator, entry_id: str, device_info: DeviceInfo):
        super().__init__(coordinator, entry_id, "Out of service", "out_of_service", "out_of_service", device_info)

    @property
    def is_on(self) -> bool:
        return int(self._data.get("OutOfService", 0)) == 1

    @property
    def extra_state_attributes(self) -> dict:
        return {"OutOfService": self._data.get("OutOfService")}
