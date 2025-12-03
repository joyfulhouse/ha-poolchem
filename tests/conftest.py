"""Pytest fixtures for Pool Chemistry integration tests."""

from __future__ import annotations

from collections.abc import Generator
from typing import Any

from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
import pytest

from custom_components.poolchem.const import (
    CONF_BORATES_ENTITY,
    CONF_CH_ENTITY,
    CONF_CYA_ENTITY,
    CONF_FC_ENTITY,
    CONF_PH_ENTITY,
    CONF_POOL_NAME,
    CONF_POOL_TYPE,
    CONF_SALT_ENTITY,
    CONF_SURFACE_TYPE,
    CONF_TA_ENTITY,
    CONF_TDS_ENTITY,
    CONF_TEMP_ENTITY,
    CONF_VOLUME_GALLONS,
    PoolType,
    SurfaceType,
)

pytest_plugins = "pytest_homeassistant_custom_component"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(
    enable_custom_integrations: None,
) -> Generator[None]:
    """Enable custom integrations for all tests."""
    return


@pytest.fixture
def mock_source_entities(hass: HomeAssistant) -> None:
    """Set up mock source sensor entities."""
    # Temperature sensor (in Fahrenheit)
    hass.states.async_set(
        "sensor.pool_temp",
        "84",
        {"unit_of_measurement": UnitOfTemperature.FAHRENHEIT},
    )
    # pH sensor
    hass.states.async_set("sensor.pool_ph", "7.5")
    # Free chlorine sensor
    hass.states.async_set("sensor.pool_fc", "5.0")
    # Total alkalinity sensor
    hass.states.async_set("sensor.pool_ta", "80")
    # Calcium hardness sensor
    hass.states.async_set("sensor.pool_ch", "300")
    # Cyanuric acid sensor
    hass.states.async_set("sensor.pool_cya", "40")
    # Salt sensor
    hass.states.async_set("sensor.pool_salt", "3200")
    # TDS sensor
    hass.states.async_set("sensor.pool_tds", "1000")
    # Borates sensor
    hass.states.async_set("sensor.pool_borates", "0")


@pytest.fixture
def mock_source_entities_celsius(hass: HomeAssistant) -> None:
    """Set up mock source sensor entities with Celsius temperature."""
    # Temperature sensor (in Celsius - equivalent to 84°F)
    hass.states.async_set(
        "sensor.pool_temp",
        "28.89",
        {"unit_of_measurement": UnitOfTemperature.CELSIUS},
    )
    # pH sensor
    hass.states.async_set("sensor.pool_ph", "7.5")
    # Free chlorine sensor
    hass.states.async_set("sensor.pool_fc", "5.0")
    # Total alkalinity sensor
    hass.states.async_set("sensor.pool_ta", "80")
    # Calcium hardness sensor
    hass.states.async_set("sensor.pool_ch", "300")
    # Cyanuric acid sensor
    hass.states.async_set("sensor.pool_cya", "40")


@pytest.fixture
def mock_config_entry_data() -> dict[str, Any]:
    """Return mock config entry data."""
    return {
        CONF_POOL_NAME: "Test Pool",
        CONF_VOLUME_GALLONS: 15000,
        CONF_POOL_TYPE: PoolType.CHLORINE,
        CONF_SURFACE_TYPE: SurfaceType.PLASTER,
        CONF_TEMP_ENTITY: "sensor.pool_temp",
        CONF_PH_ENTITY: "sensor.pool_ph",
        CONF_FC_ENTITY: "sensor.pool_fc",
        CONF_TA_ENTITY: "sensor.pool_ta",
        CONF_CH_ENTITY: "sensor.pool_ch",
        CONF_CYA_ENTITY: "sensor.pool_cya",
        CONF_SALT_ENTITY: "sensor.pool_salt",
        CONF_TDS_ENTITY: "sensor.pool_tds",
        CONF_BORATES_ENTITY: "sensor.pool_borates",
    }


@pytest.fixture
def mock_config_entry_data_minimal() -> dict[str, Any]:
    """Return minimal mock config entry data (no optional sensors)."""
    return {
        CONF_POOL_NAME: "Test Pool",
        CONF_VOLUME_GALLONS: 15000,
        CONF_POOL_TYPE: PoolType.CHLORINE,
        CONF_SURFACE_TYPE: SurfaceType.PLASTER,
        CONF_TEMP_ENTITY: "sensor.pool_temp",
        CONF_PH_ENTITY: "sensor.pool_ph",
        CONF_FC_ENTITY: "sensor.pool_fc",
        CONF_TA_ENTITY: "sensor.pool_ta",
        CONF_CH_ENTITY: "sensor.pool_ch",
    }


@pytest.fixture
def mock_config_entry_data_saltwater() -> dict[str, Any]:
    """Return mock config entry data for a saltwater pool."""
    return {
        CONF_POOL_NAME: "Salt Pool",
        CONF_VOLUME_GALLONS: 20000,
        CONF_POOL_TYPE: PoolType.SALTWATER,
        CONF_SURFACE_TYPE: SurfaceType.PEBBLE,
        CONF_TEMP_ENTITY: "sensor.pool_temp",
        CONF_PH_ENTITY: "sensor.pool_ph",
        CONF_FC_ENTITY: "sensor.pool_fc",
        CONF_TA_ENTITY: "sensor.pool_ta",
        CONF_CH_ENTITY: "sensor.pool_ch",
        CONF_CYA_ENTITY: "sensor.pool_cya",
        CONF_SALT_ENTITY: "sensor.pool_salt",
    }
