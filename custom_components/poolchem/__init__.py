"""Pool Chemistry Integration for Home Assistant.

This integration provides pool water chemistry analysis and dosing recommendations
by consuming sensor entities from any source and producing calculated sensors.
"""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN
from .coordinator import PoolChemCoordinator

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.empty_config_schema(DOMAIN)

PLATFORMS = [Platform.NUMBER, Platform.SENSOR]

type PoolChemConfigEntry = ConfigEntry[PoolChemCoordinator]


async def async_setup(
    hass: HomeAssistant,  # noqa: ARG001
    config: dict[str, object],  # noqa: ARG001
) -> bool:
    """Set up the Pool Chemistry integration."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: PoolChemConfigEntry) -> bool:
    """Set up Pool Chemistry from a config entry."""
    coordinator = PoolChemCoordinator(hass, entry)

    # Set up event listeners and fetch initial data
    await coordinator.async_setup()

    # Store coordinator in runtime_data
    entry.runtime_data = coordinator

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register update listener for options changes
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    _LOGGER.info("Pool Chemistry integration set up for: %s", coordinator.pool_name)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: PoolChemConfigEntry) -> bool:
    """Unload a Pool Chemistry config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        _LOGGER.info("Pool Chemistry integration unloaded: %s", entry.entry_id)

    return bool(unload_ok)


async def async_reload_entry(hass: HomeAssistant, entry: PoolChemConfigEntry) -> None:
    """Reload the config entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)
