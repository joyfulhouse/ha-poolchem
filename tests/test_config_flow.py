"""Tests for Pool Chemistry config flow."""

from __future__ import annotations

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.poolchem.const import (
    CONF_CH_ENTITY,
    CONF_CYA_ENTITY,
    CONF_FC_ENTITY,
    CONF_PH_ENTITY,
    CONF_POOL_NAME,
    CONF_POOL_TYPE,
    CONF_SURFACE_TYPE,
    CONF_TA_ENTITY,
    CONF_TEMP_ENTITY,
    CONF_VOLUME_GALLONS,
    DOMAIN,
    PoolType,
    SurfaceType,
)


async def test_user_flow_creates_entry(
    hass: HomeAssistant,
    mock_source_entities: None,
) -> None:
    """Test complete user config flow creates an entry."""
    # Start the flow
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"] == {}

    # Step 1: Pool configuration
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_POOL_NAME: "My Pool",
            CONF_VOLUME_GALLONS: 15000,
            CONF_POOL_TYPE: PoolType.CHLORINE,
            CONF_SURFACE_TYPE: SurfaceType.PLASTER,
        },
    )

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "required_entities"

    # Step 2: Required entities
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_TEMP_ENTITY: "sensor.pool_temp",
            CONF_PH_ENTITY: "sensor.pool_ph",
            CONF_FC_ENTITY: "sensor.pool_fc",
            CONF_TA_ENTITY: "sensor.pool_ta",
            CONF_CH_ENTITY: "sensor.pool_ch",
        },
    )

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "optional_entities"

    # Step 3: Optional entities (skip by providing empty)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_CYA_ENTITY: "sensor.pool_cya",
        },
    )

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "My Pool"
    assert result["data"][CONF_POOL_NAME] == "My Pool"
    assert result["data"][CONF_VOLUME_GALLONS] == 15000
    assert result["data"][CONF_POOL_TYPE] == PoolType.CHLORINE
    assert result["data"][CONF_TEMP_ENTITY] == "sensor.pool_temp"
    assert result["data"][CONF_CYA_ENTITY] == "sensor.pool_cya"


async def test_user_flow_minimal_config(
    hass: HomeAssistant,
    mock_source_entities: None,
) -> None:
    """Test config flow with only required sensors."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    # Step 1: Pool configuration
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_POOL_NAME: "Simple Pool",
            CONF_VOLUME_GALLONS: 10000,
            CONF_POOL_TYPE: PoolType.CHLORINE,
            CONF_SURFACE_TYPE: SurfaceType.VINYL,
        },
    )

    # Step 2: Required entities
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_TEMP_ENTITY: "sensor.pool_temp",
            CONF_PH_ENTITY: "sensor.pool_ph",
            CONF_FC_ENTITY: "sensor.pool_fc",
            CONF_TA_ENTITY: "sensor.pool_ta",
            CONF_CH_ENTITY: "sensor.pool_ch",
        },
    )

    # Step 3: Optional entities (all empty)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {},
    )

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "Simple Pool"
    # Optional entities should not be in data
    assert CONF_CYA_ENTITY not in result["data"]


async def test_user_flow_saltwater_pool(
    hass: HomeAssistant,
    mock_source_entities: None,
) -> None:
    """Test config flow for a saltwater pool."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    # Step 1: Pool configuration
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_POOL_NAME: "Salt Pool",
            CONF_VOLUME_GALLONS: 20000,
            CONF_POOL_TYPE: PoolType.SALTWATER,
            CONF_SURFACE_TYPE: SurfaceType.PEBBLE,
        },
    )

    # Step 2: Required entities
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_TEMP_ENTITY: "sensor.pool_temp",
            CONF_PH_ENTITY: "sensor.pool_ph",
            CONF_FC_ENTITY: "sensor.pool_fc",
            CONF_TA_ENTITY: "sensor.pool_ta",
            CONF_CH_ENTITY: "sensor.pool_ch",
        },
    )

    # Step 3: Optional entities with salt
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            "salt_entity": "sensor.pool_salt",
            "cya_entity": "sensor.pool_cya",
        },
    )

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_POOL_TYPE] == PoolType.SALTWATER
