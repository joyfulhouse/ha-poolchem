"""Tests for Pool Chemistry config flow."""

from __future__ import annotations

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.poolchem.const import (
    CONF_ACID_TYPE,
    CONF_CH_ENTITY,
    CONF_CHLORINE_TYPE,
    CONF_CYA_ENTITY,
    CONF_ENABLE_DOSE_ACID,
    CONF_FC_ENTITY,
    CONF_PH_ENTITY,
    CONF_POOL_NAME,
    CONF_POOL_TYPE,
    CONF_SALT_ENTITY,
    CONF_SURFACE_TYPE,
    CONF_TA_ENTITY,
    CONF_TEMP_ENTITY,
    CONF_VOLUME_GALLONS,
    DEFAULT_ACID_TYPE,
    DEFAULT_CHLORINE_TYPE,
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

    # Step 3: Optional entities
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_CYA_ENTITY: "sensor.pool_cya",
        },
    )

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "chemicals"

    # Step 4: Chemical types (use defaults)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_ACID_TYPE: DEFAULT_ACID_TYPE,
            CONF_CHLORINE_TYPE: DEFAULT_CHLORINE_TYPE,
        },
    )

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "dosing_sensors"

    # Step 5: Dosing sensors (use defaults)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_ENABLE_DOSE_ACID: True,
        },
    )

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "My Pool"
    # Pool info and entities go in data (immutable)
    assert result["data"][CONF_POOL_NAME] == "My Pool"
    assert result["data"][CONF_VOLUME_GALLONS] == 15000
    assert result["data"][CONF_POOL_TYPE] == PoolType.CHLORINE
    assert result["data"][CONF_TEMP_ENTITY] == "sensor.pool_temp"
    assert result["data"][CONF_CYA_ENTITY] == "sensor.pool_cya"
    # Chemicals, dosing toggles go in options (targets are now number entities)
    assert result["options"][CONF_ACID_TYPE] == DEFAULT_ACID_TYPE
    assert result["options"][CONF_CHLORINE_TYPE] == DEFAULT_CHLORINE_TYPE
    assert result["options"][CONF_ENABLE_DOSE_ACID] is True


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

    # Step 4: Chemical types (use defaults)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {},
    )

    # Step 5: Dosing sensors (use defaults)
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

    # Step 4: Chemical types
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {},
    )

    # Step 5: Dosing sensors
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {},
    )

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_POOL_TYPE] == PoolType.SALTWATER


async def test_reconfigure_flow(
    hass: HomeAssistant,
    mock_source_entities: None,
) -> None:
    """Test reconfiguration flow."""
    # First create an entry
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_POOL_NAME: "Old Pool",
            CONF_VOLUME_GALLONS: 10000,
            CONF_POOL_TYPE: PoolType.CHLORINE,
            CONF_SURFACE_TYPE: SurfaceType.VINYL,
            CONF_TEMP_ENTITY: "sensor.pool_temp",
            CONF_PH_ENTITY: "sensor.pool_ph",
            CONF_FC_ENTITY: "sensor.pool_fc",
            CONF_TA_ENTITY: "sensor.pool_ta",
            CONF_CH_ENTITY: "sensor.pool_ch",
        },
        options={
            CONF_ACID_TYPE: DEFAULT_ACID_TYPE,
        },
    )
    entry.add_to_hass(hass)

    # Start reconfigure flow
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={
            "source": config_entries.SOURCE_RECONFIGURE,
            "entry_id": entry.entry_id,
        },
    )

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "reconfigure_pool"

    # Step 1: Update pool configuration
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_POOL_NAME: "New Pool",
            CONF_VOLUME_GALLONS: 20000,
            CONF_POOL_TYPE: PoolType.SALTWATER,
            CONF_SURFACE_TYPE: SurfaceType.PEBBLE,
        },
    )

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "reconfigure_entities"

    # Step 2: Update entities (only required + selected optional fields)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_TEMP_ENTITY: "sensor.pool_temp",
            CONF_PH_ENTITY: "sensor.pool_ph",
            CONF_FC_ENTITY: "sensor.pool_fc",
            CONF_TA_ENTITY: "sensor.pool_ta",
            CONF_CH_ENTITY: "sensor.pool_ch",
            CONF_SALT_ENTITY: "sensor.pool_salt",
        },
    )

    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"

    # Verify the entry was updated
    assert entry.data[CONF_POOL_NAME] == "New Pool"
    assert entry.data[CONF_VOLUME_GALLONS] == 20000
    assert entry.data[CONF_POOL_TYPE] == PoolType.SALTWATER
    assert entry.data[CONF_SALT_ENTITY] == "sensor.pool_salt"
    # Options should be preserved
    assert entry.options[CONF_ACID_TYPE] == DEFAULT_ACID_TYPE
