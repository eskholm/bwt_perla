from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional, List, Tuple

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import DOMAIN, MANUFACTURER, MODEL


@dataclass
class BwtDesc(SensorEntityDescription):
    key: str = ""
    factor: float = 1.0
    decimals: Optional[int] = None
    translation_key: Optional[str] = None


SENSOR_DESCRIPTIONS: List[BwtDesc] = [
    BwtDesc(
        key="WaterTreatedCurrentDay_l",
        translation_key="water_treated_today",
        native_unit_of_measurement="m³",
        device_class=SensorDeviceClass.WATER,
        state_class=SensorStateClass.TOTAL,
        factor=0.001,
        decimals=3,
    ),
    BwtDesc(
        key="WaterTreatedCurrentMonth_l",
        translation_key="water_treated_month",
        native_unit_of_measurement="m³",
        device_class=SensorDeviceClass.WATER,
        state_class=SensorStateClass.TOTAL,
        factor=0.001,
        decimals=3,
    ),
    BwtDesc(
        key="WaterTreatedCurrentYear_l",
        translation_key="water_treated_year",
        native_unit_of_measurement="m³",
        device_class=SensorDeviceClass.WATER,
        state_class=SensorStateClass.TOTAL,
        factor=0.001,
        decimals=3,
    ),
    BwtDesc(
        key="WaterSinceSetup_l",
        translation_key="water_since_setup",
        native_unit_of_measurement="m³",
        device_class=SensorDeviceClass.WATER,
        state_class=SensorStateClass.TOTAL_INCREASING,
        factor=0.001,
        decimals=3,
    ),
    BwtDesc(
        key="BlendedWaterSinceSetup_l",
        translation_key="blended_water_since_setup",
        native_unit_of_measurement="m³",
        device_class=SensorDeviceClass.WATER,
        state_class=SensorStateClass.TOTAL_INCREASING,
        factor=0.001,
        decimals=3,
    ),
    BwtDesc(
        key="CurrentFlowrate_l_h",
        translation_key="current_flow",
        native_unit_of_measurement="L/h",
        state_class=SensorStateClass.MEASUREMENT,
        factor=1.0,
        decimals=0,
    ),
    BwtDesc(
        key="HardnessIN_dH",
        translation_key="hardness_in",
        native_unit_of_measurement="°dH",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BwtDesc(
        key="HardnessIN_CaCO3",
        translation_key="hardness_in_caco3",
        native_unit_of_measurement="mg/L",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BwtDesc(
        key="HardnessOUT_dH",
        translation_key="hardness_out",
        native_unit_of_measurement="°dH",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BwtDesc(
        key="HardnessOUT_CaCO3",
        translation_key="hardness_out_caco3",
        native_unit_of_measurement="mg/L",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BwtDesc(
        key="RegenerationCountSinceSetup",
        translation_key="regens_total",
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    BwtDesc(
        key="RegenerationCounterColumn1",
        translation_key="regens_col1",
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    BwtDesc(
        key="RegenerationCounterColumn2",
        translation_key="regens_col2",
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    BwtDesc(
        key="RegenerativSinceSetup_g",
        translation_key="salt_used_since_setup",
        native_unit_of_measurement="g",
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    BwtDesc(
        key="RegenerativLevel",
        translation_key="salt_level",
        native_unit_of_measurement="%",
        state_class=SensorStateClass.MEASUREMENT,
        decimals=0,
    ),
    BwtDesc(
        key="RegenerativRemainingDays",
        translation_key="salt_remaining_days",
        native_unit_of_measurement="days",
        state_class=SensorStateClass.MEASUREMENT,
        decimals=0,
    ),
    BwtDesc(
        key="DosingSinceSetup_ml",
        translation_key="dosing_since_setup",
        native_unit_of_measurement="mL",
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
]

TIMESTAMP_KEYS: List[Tuple[str, str]] = [
    ("LastRegenerationColumn1", "last_regen_col1"),
    ("LastRegenerationColumn2", "last_regen_col2"),
    ("LastServiceCustomer", "last_service_customer"),
    ("LastServiceTechnican", "last_service_technician"),
]


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    device_info = DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        manufacturer=MANUFACTURER,
        model=MODEL,
        name="BWT Perla",
    )

    entities: list[SensorEntity] = []
    for d in SENSOR_DESCRIPTIONS:
        entities.append(BwtNumberSensor(coordinator, entry.entry_id, d, device_info))
    for key, t_key in TIMESTAMP_KEYS:
        entities.append(BwtTimestampSensor(coordinator, entry.entry_id, key, t_key, device_info))

    async_add_entities(entities)


class BwtNumberSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True  

    def __init__(self, coordinator, entry_id: str, desc: BwtDesc, device_info: DeviceInfo):
        super().__init__(coordinator)
        self.entity_description = desc
        self._key = desc.key
        self._attr_unique_id = f"{entry_id}_{desc.key}"
        self._attr_device_info = device_info
        self._attr_translation_key = desc.translation_key
        self._attr_name = None

    @property
    def native_unit_of_measurement(self) -> Optional[str]:
        return self.entity_description.native_unit_of_measurement

    @property
    def device_class(self) -> Optional[str]:
        return self.entity_description.device_class

    @property
    def state_class(self) -> Optional[str]:
        return self.entity_description.state_class

    @property
    def native_value(self) -> Optional[float]:
        data: dict[str, Any] = self.coordinator.data or {}
        val = data.get(self._key)
        if val in (None, ""):
            return None
        try:
            v = float(val) * (self.entity_description.factor or 1.0)
            if self.entity_description.decimals is not None:
                v = round(v, self.entity_description.decimals)
            return v
        except (ValueError, TypeError):
            return None


class BwtTimestampSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, coordinator, entry_id: str, key: str, translation_key: str, device_info: DeviceInfo):
        super().__init__(coordinator)
        self._key = key
        self._attr_unique_id = f"{entry_id}_{key}"
        self._attr_device_info = device_info
        self._attr_translation_key = translation_key
        self._attr_name = None

    @property
    def native_value(self):
        data: dict[str, Any] = self.coordinator.data or {}
        raw = data.get(self._key)
        if not raw or str(raw).startswith("-"):
            return None
        try:
            dt_naive = datetime.strptime(str(raw), "%Y-%m-%d %H:%M:%S")
            tz = dt_util.get_time_zone(self.hass.config.time_zone)
            return dt_naive.replace(tzinfo=tz)
        except Exception:
            return None
