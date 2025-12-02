"""Base entity for Pool Chemistry integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, VERSION

if TYPE_CHECKING:
    from .coordinator import PoolChemCoordinator


class PoolChemEntity(CoordinatorEntity["PoolChemCoordinator"]):
    """Base entity for Pool Chemistry sensors."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(
        self,
        coordinator: PoolChemCoordinator,
        key: str,
    ) -> None:
        """Initialize the entity.

        Args:
            coordinator: The data update coordinator.
            key: Unique key for this entity (e.g., "csi", "dose_acid").
        """
        super().__init__(coordinator)
        self._key = key
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{key}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info for grouping entities."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.config_entry.entry_id)},
            name=self.coordinator.pool_name,
            manufacturer="pypoolchem",
            model="Virtual Pool",
            sw_version=VERSION,
            configuration_url="https://github.com/joyfulhouse/homeassistant-poolchem",
        )
