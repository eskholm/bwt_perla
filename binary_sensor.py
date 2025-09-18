from __future__ import annotations
from typing import Any
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
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
    entities: list[BinarySensorEntity] = [
        BwtErrorBinarySensor(coordinator, entry.entry_id, device_info),
        BwtOutOfServiceBinarySensor(coordinator, entry.entry_id, device_info),
    ]
    async_add_entities(entities)

class _BaseBwtBinary(CoordinatorEntity, BinarySensorEntity):
    def __init__(self, coordinator, entry_id: str, name: str, unique_key: str, device_info: DeviceInfo):
        super().__init__(coordinator)
        self._attr_name = f"BWT Perla {name}"
        self._attr_unique_id = f"{entry_id}_{unique_key}"
        self._attr_device_info = device_info
    @property
    def _data(self) -> dict[str, Any]:
        return self.coordinator.data or {}

class BwtErrorBinarySensor(_BaseBwtBinary):
    _attr_device_class = "problem"
    _attr_translation_key = "error"
    def __init__(self, coordinator, entry_id: str, device_info: DeviceInfo):
        super().__init__(coordinator, entry_id, "Error", "error", device_info)
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
    _attr_translation_key = "out_of_service"
    def __init__(self, coordinator, entry_id: str, device_info: DeviceInfo):
        super().__init__(coordinator, entry_id, "Out of service", "out_of_service", device_info)
    @property
    def is_on(self) -> bool:
        return int(self._data.get("OutOfService", 0)) == 1
    @property
    def extra_state_attributes(self) -> dict:
        return {"OutOfService": self._data.get("OutOfService")}
