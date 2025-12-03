"""Number entities for Pool Chemistry integration.

These number entities allow users to configure target chemistry values
using sliders in the Home Assistant UI. Changes are saved to the config
entry options and trigger recalculation of dosing recommendations.
"""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_POOL_TYPE,
    CONF_TARGET_BORATES,
    CONF_TARGET_CH,
    CONF_TARGET_CYA,
    CONF_TARGET_FC,
    CONF_TARGET_PH,
    CONF_TARGET_SALT,
    CONF_TARGET_TA,
    DEFAULT_TARGET_BORATES,
    DEFAULT_TARGET_CH,
    DEFAULT_TARGET_CYA,
    DEFAULT_TARGET_FC,
    DEFAULT_TARGET_PH,
    DEFAULT_TARGET_SALT,
    DEFAULT_TARGET_TA,
    PoolType,
)
from .coordinator import PoolChemCoordinator
from .entity import PoolChemEntity


@dataclass(frozen=True, kw_only=True)
class PoolChemNumberEntityDescription(NumberEntityDescription):
    """Describes a Pool Chemistry number entity."""

    config_key: str
    default_value: float


# Target number entities
TARGET_NUMBERS: tuple[PoolChemNumberEntityDescription, ...] = (
    PoolChemNumberEntityDescription(
        key="target_ph",
        translation_key="target_ph",
        config_key=CONF_TARGET_PH,
        default_value=DEFAULT_TARGET_PH,
        native_min_value=6.8,
        native_max_value=8.0,
        native_step=0.1,
        mode=NumberMode.SLIDER,
        icon="mdi:ph",
    ),
    PoolChemNumberEntityDescription(
        key="target_fc",
        translation_key="target_fc",
        config_key=CONF_TARGET_FC,
        default_value=DEFAULT_TARGET_FC,
        native_min_value=1.0,
        native_max_value=20.0,
        native_step=0.5,
        native_unit_of_measurement="ppm",
        mode=NumberMode.SLIDER,
        icon="mdi:water-plus-outline",
    ),
    PoolChemNumberEntityDescription(
        key="target_ta",
        translation_key="target_ta",
        config_key=CONF_TARGET_TA,
        default_value=DEFAULT_TARGET_TA,
        native_min_value=50,
        native_max_value=150,
        native_step=5,
        native_unit_of_measurement="ppm",
        mode=NumberMode.SLIDER,
        icon="mdi:water-opacity",
    ),
    PoolChemNumberEntityDescription(
        key="target_ch",
        translation_key="target_ch",
        config_key=CONF_TARGET_CH,
        default_value=DEFAULT_TARGET_CH,
        native_min_value=150,
        native_max_value=500,
        native_step=10,
        native_unit_of_measurement="ppm",
        mode=NumberMode.SLIDER,
        icon="mdi:water-circle",
    ),
    PoolChemNumberEntityDescription(
        key="target_cya",
        translation_key="target_cya",
        config_key=CONF_TARGET_CYA,
        default_value=DEFAULT_TARGET_CYA,
        native_min_value=0,
        native_max_value=100,
        native_step=5,
        native_unit_of_measurement="ppm",
        mode=NumberMode.SLIDER,
        icon="mdi:shield-sun-outline",
    ),
    PoolChemNumberEntityDescription(
        key="target_borates",
        translation_key="target_borates",
        config_key=CONF_TARGET_BORATES,
        default_value=DEFAULT_TARGET_BORATES,
        native_min_value=0,
        native_max_value=100,
        native_step=5,
        native_unit_of_measurement="ppm",
        mode=NumberMode.SLIDER,
        icon="mdi:flask-outline",
    ),
)

# Salt target (only for saltwater pools)
SALT_TARGET_NUMBER = PoolChemNumberEntityDescription(
    key="target_salt",
    translation_key="target_salt",
    config_key=CONF_TARGET_SALT,
    default_value=DEFAULT_TARGET_SALT,
    native_min_value=2500,
    native_max_value=4000,
    native_step=100,
    native_unit_of_measurement="ppm",
    mode=NumberMode.SLIDER,
    icon="mdi:shaker",
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Pool Chemistry number entities from a config entry."""
    coordinator: PoolChemCoordinator = entry.runtime_data

    entities: list[PoolChemNumber] = []

    # Add target number entities
    for description in TARGET_NUMBERS:
        entities.append(PoolChemNumber(coordinator, entry, description))

    # Add salt target for saltwater pools
    if entry.data.get(CONF_POOL_TYPE) == PoolType.SALTWATER:
        entities.append(PoolChemNumber(coordinator, entry, SALT_TARGET_NUMBER))

    async_add_entities(entities)


class PoolChemNumber(PoolChemEntity, NumberEntity):
    """Representation of a Pool Chemistry target number entity."""

    entity_description: PoolChemNumberEntityDescription

    def __init__(
        self,
        coordinator: PoolChemCoordinator,
        entry: ConfigEntry,
        description: PoolChemNumberEntityDescription,
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator, description.key)
        self.entity_description = description
        self._entry = entry

    @property
    def native_value(self) -> float:
        """Return the current value."""
        return self._entry.options.get(
            self.entity_description.config_key,
            self.entity_description.default_value,
        )

    async def async_set_native_value(self, value: float) -> None:
        """Set the target value."""
        new_options = dict(self._entry.options)
        new_options[self.entity_description.config_key] = value

        self.hass.config_entries.async_update_entry(
            self._entry,
            options=new_options,
        )

        # Request coordinator refresh to recalculate with new target
        await self.coordinator.async_request_refresh()
