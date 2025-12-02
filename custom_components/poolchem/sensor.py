"""Sensor entities for Pool Chemistry integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from pypoolchem.dosing.calculator import DosingResult

from .const import (
    CONF_ENABLE_DOSE_ACID,
    CONF_ENABLE_DOSE_ALKALINITY,
    CONF_ENABLE_DOSE_CALCIUM,
    CONF_ENABLE_DOSE_CHLORINE,
    CONF_ENABLE_DOSE_CYA,
    CONF_ENABLE_DOSE_SALT,
    CONF_POOL_TYPE,
    DEFAULT_ENABLE_DOSE_ACID,
    DEFAULT_ENABLE_DOSE_ALKALINITY,
    DEFAULT_ENABLE_DOSE_CALCIUM,
    DEFAULT_ENABLE_DOSE_CHLORINE,
    DEFAULT_ENABLE_DOSE_CYA,
    DEFAULT_ENABLE_DOSE_SALT,
    SENSOR_CSI,
    SENSOR_DOSE_ACID,
    SENSOR_DOSE_ALKALINITY,
    SENSOR_DOSE_CALCIUM,
    SENSOR_DOSE_CHLORINE,
    SENSOR_DOSE_CYA,
    SENSOR_DOSE_SALT,
    SENSOR_FC_CYA_RATIO,
    SENSOR_LSI,
    SENSOR_WATER_BALANCE,
    PoolType,
    WaterBalanceState,
)
from .coordinator import PoolChemCoordinator, PoolChemData
from .entity import PoolChemEntity


@dataclass(frozen=True, kw_only=True)
class PoolChemSensorEntityDescription(SensorEntityDescription):
    """Describes a Pool Chemistry sensor entity."""

    value_fn: Callable[[PoolChemData], Any]
    extra_attrs_fn: Callable[[PoolChemData], dict[str, Any]] | None = None
    available_fn: Callable[[PoolChemData], bool] | None = None


def _csi_value(data: PoolChemData) -> float | None:
    """Get CSI value."""
    return round(data.csi, 2) if data.csi is not None else None


def _csi_attrs(data: PoolChemData) -> dict[str, Any]:
    """Get CSI attributes."""
    attrs: dict[str, Any] = {}
    if data.water:
        attrs["ph"] = data.water.ph
        attrs["temperature_f"] = data.water.temperature_f
        attrs["calcium_hardness"] = data.water.calcium_hardness
        attrs["total_alkalinity"] = data.water.total_alkalinity
        attrs["cyanuric_acid"] = data.water.cyanuric_acid
        attrs["salt"] = data.water.salt
        attrs["borates"] = data.water.borates
    if data.balance_state:
        attrs["balance_state"] = data.balance_state.value
    return attrs


def _lsi_value(data: PoolChemData) -> float | None:
    """Get LSI value."""
    return round(data.lsi, 2) if data.lsi is not None else None


def _lsi_attrs(data: PoolChemData) -> dict[str, Any]:
    """Get LSI attributes."""
    attrs: dict[str, Any] = {}
    if data.water:
        attrs["ph"] = data.water.ph
        attrs["temperature_f"] = data.water.temperature_f
        attrs["calcium_hardness"] = data.water.calcium_hardness
        attrs["total_alkalinity"] = data.water.total_alkalinity
        attrs["tds"] = data.water.tds
    return attrs


def _water_balance_value(data: PoolChemData) -> str:
    """Get water balance state."""
    return data.balance_state.value


def _water_balance_attrs(data: PoolChemData) -> dict[str, Any]:
    """Get water balance attributes."""
    attrs: dict[str, Any] = {}
    if data.csi is not None:
        attrs["csi"] = round(data.csi, 2)
    if data.lsi is not None:
        attrs["lsi"] = round(data.lsi, 2)
    return attrs


def _fc_cya_value(data: PoolChemData) -> float | None:
    """Get FC/CYA ratio value."""
    return round(data.fc_cya_ratio, 1) if data.fc_cya_ratio is not None else None


def _fc_cya_attrs(data: PoolChemData) -> dict[str, Any]:
    """Get FC/CYA ratio attributes."""
    attrs: dict[str, Any] = {}
    if data.water:
        attrs["free_chlorine"] = data.water.free_chlorine
        attrs["cyanuric_acid"] = data.water.cyanuric_acid
    if data.fc_is_adequate is not None:
        attrs["is_adequate"] = data.fc_is_adequate
    return attrs


def _make_dose_value_fn(
    dose_attr: str,
) -> Callable[[PoolChemData], float | None]:
    """Create a value function for a dosing sensor."""

    def _value_fn(data: PoolChemData) -> float | None:
        dose: DosingResult | None = getattr(data, dose_attr, None)
        if dose is None:
            return None
        return dose.amount

    return _value_fn


def _make_dose_attrs_fn(
    dose_attr: str,
) -> Callable[[PoolChemData], dict[str, Any]]:
    """Create an attributes function for a dosing sensor."""

    def _attrs_fn(data: PoolChemData) -> dict[str, Any]:
        dose: DosingResult | None = getattr(data, dose_attr, None)
        if dose is None:
            return {}
        attrs: dict[str, Any] = {
            "chemical": dose.chemical.name,
            "unit": dose.unit,
        }
        if dose.amount_volume is not None:
            attrs["amount_volume"] = dose.amount_volume
            attrs["volume_unit"] = dose.volume_unit
        if dose.notes:
            attrs["notes"] = dose.notes
        return attrs

    return _attrs_fn


def _make_dose_available_fn(
    dose_attr: str,
) -> Callable[[PoolChemData], bool]:
    """Create an available function for a dosing sensor."""

    def _available_fn(data: PoolChemData) -> bool:
        return getattr(data, dose_attr, None) is not None

    return _available_fn


# Core water balance sensors (always created)
WATER_BALANCE_SENSORS: tuple[PoolChemSensorEntityDescription, ...] = (
    PoolChemSensorEntityDescription(
        key=SENSOR_CSI,
        translation_key="csi",
        native_unit_of_measurement=None,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_csi_value,
        extra_attrs_fn=_csi_attrs,
        available_fn=lambda d: d.csi is not None,
    ),
    PoolChemSensorEntityDescription(
        key=SENSOR_LSI,
        translation_key="lsi",
        native_unit_of_measurement=None,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_lsi_value,
        extra_attrs_fn=_lsi_attrs,
        available_fn=lambda d: d.lsi is not None,
    ),
    PoolChemSensorEntityDescription(
        key=SENSOR_WATER_BALANCE,
        translation_key="water_balance",
        device_class=SensorDeviceClass.ENUM,
        options=[state.value for state in WaterBalanceState],
        value_fn=_water_balance_value,
        extra_attrs_fn=_water_balance_attrs,
    ),
    PoolChemSensorEntityDescription(
        key=SENSOR_FC_CYA_RATIO,
        translation_key="fc_cya_ratio",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_fc_cya_value,
        extra_attrs_fn=_fc_cya_attrs,
        available_fn=lambda d: d.fc_cya_ratio is not None,
    ),
)

# Dosing sensors (created based on options)
DOSING_SENSORS: dict[str, PoolChemSensorEntityDescription] = {
    SENSOR_DOSE_ACID: PoolChemSensorEntityDescription(
        key=SENSOR_DOSE_ACID,
        translation_key="dose_acid",
        native_unit_of_measurement="fl oz",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:flask-outline",
        value_fn=_make_dose_value_fn("dose_acid"),
        extra_attrs_fn=_make_dose_attrs_fn("dose_acid"),
        available_fn=_make_dose_available_fn("dose_acid"),
    ),
    SENSOR_DOSE_CHLORINE: PoolChemSensorEntityDescription(
        key=SENSOR_DOSE_CHLORINE,
        translation_key="dose_chlorine",
        native_unit_of_measurement="fl oz",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:water-plus-outline",
        value_fn=_make_dose_value_fn("dose_chlorine"),
        extra_attrs_fn=_make_dose_attrs_fn("dose_chlorine"),
        available_fn=_make_dose_available_fn("dose_chlorine"),
    ),
    SENSOR_DOSE_ALKALINITY: PoolChemSensorEntityDescription(
        key=SENSOR_DOSE_ALKALINITY,
        translation_key="dose_alkalinity",
        native_unit_of_measurement="oz",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:shaker-outline",
        value_fn=_make_dose_value_fn("dose_alkalinity"),
        extra_attrs_fn=_make_dose_attrs_fn("dose_alkalinity"),
        available_fn=_make_dose_available_fn("dose_alkalinity"),
    ),
    SENSOR_DOSE_CALCIUM: PoolChemSensorEntityDescription(
        key=SENSOR_DOSE_CALCIUM,
        translation_key="dose_calcium",
        native_unit_of_measurement="oz",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:shaker-outline",
        value_fn=_make_dose_value_fn("dose_calcium"),
        extra_attrs_fn=_make_dose_attrs_fn("dose_calcium"),
        available_fn=_make_dose_available_fn("dose_calcium"),
    ),
    SENSOR_DOSE_CYA: PoolChemSensorEntityDescription(
        key=SENSOR_DOSE_CYA,
        translation_key="dose_cya",
        native_unit_of_measurement="oz",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:shield-sun-outline",
        value_fn=_make_dose_value_fn("dose_cya"),
        extra_attrs_fn=_make_dose_attrs_fn("dose_cya"),
        available_fn=_make_dose_available_fn("dose_cya"),
    ),
    SENSOR_DOSE_SALT: PoolChemSensorEntityDescription(
        key=SENSOR_DOSE_SALT,
        translation_key="dose_salt",
        native_unit_of_measurement="lbs",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:shaker",
        value_fn=_make_dose_value_fn("dose_salt"),
        extra_attrs_fn=_make_dose_attrs_fn("dose_salt"),
        available_fn=_make_dose_available_fn("dose_salt"),
    ),
}

# Mapping of config keys to sensor keys
DOSING_CONFIG_MAP: dict[str, tuple[str, bool]] = {
    CONF_ENABLE_DOSE_ACID: (SENSOR_DOSE_ACID, DEFAULT_ENABLE_DOSE_ACID),
    CONF_ENABLE_DOSE_CHLORINE: (SENSOR_DOSE_CHLORINE, DEFAULT_ENABLE_DOSE_CHLORINE),
    CONF_ENABLE_DOSE_ALKALINITY: (
        SENSOR_DOSE_ALKALINITY,
        DEFAULT_ENABLE_DOSE_ALKALINITY,
    ),
    CONF_ENABLE_DOSE_CALCIUM: (SENSOR_DOSE_CALCIUM, DEFAULT_ENABLE_DOSE_CALCIUM),
    CONF_ENABLE_DOSE_CYA: (SENSOR_DOSE_CYA, DEFAULT_ENABLE_DOSE_CYA),
    CONF_ENABLE_DOSE_SALT: (SENSOR_DOSE_SALT, DEFAULT_ENABLE_DOSE_SALT),
}


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Pool Chemistry sensors from a config entry."""
    coordinator: PoolChemCoordinator = entry.runtime_data

    entities: list[PoolChemSensor] = []

    # Add core water balance sensors
    for description in WATER_BALANCE_SENSORS:
        entities.append(PoolChemSensor(coordinator, description))

    # Add enabled dosing sensors
    is_saltwater = entry.data.get(CONF_POOL_TYPE) == PoolType.SALTWATER

    for conf_key, (sensor_key, default) in DOSING_CONFIG_MAP.items():
        # Skip salt sensor for non-saltwater pools
        if sensor_key == SENSOR_DOSE_SALT and not is_saltwater:
            continue

        # Check if enabled in options
        if entry.options.get(conf_key, default):
            description = DOSING_SENSORS[sensor_key]
            entities.append(PoolChemSensor(coordinator, description))

    async_add_entities(entities)


class PoolChemSensor(PoolChemEntity, SensorEntity):
    """Representation of a Pool Chemistry sensor."""

    entity_description: PoolChemSensorEntityDescription

    def __init__(
        self,
        coordinator: PoolChemCoordinator,
        description: PoolChemSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> Any:
        """Return the sensor value."""
        if self.coordinator.data is None:
            return None
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return extra state attributes."""
        if self.coordinator.data is None:
            return None
        if self.entity_description.extra_attrs_fn is None:
            return None
        return self.entity_description.extra_attrs_fn(self.coordinator.data)

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        if not super().available:
            return False
        if self.coordinator.data is None:
            return False
        if self.entity_description.available_fn is None:
            return True
        return self.entity_description.available_fn(self.coordinator.data)
