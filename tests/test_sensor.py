"""Tests for Pool Chemistry sensors."""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.poolchem.const import (
    DOMAIN,
    SENSOR_CSI,
    SENSOR_FC_CYA_RATIO,
    SENSOR_LSI,
    SENSOR_WATER_BALANCE,
    WaterBalanceState,
)


async def test_sensors_created(
    hass: HomeAssistant,
    mock_source_entities: None,
    mock_config_entry_data: dict[str, Any],
) -> None:
    """Test that sensors are created correctly."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data=mock_config_entry_data,
        options={},
    )
    entry.add_to_hass(hass)

    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    # Check CSI sensor exists
    csi_state = hass.states.get(f"sensor.test_pool_{SENSOR_CSI}")
    assert csi_state is not None
    assert csi_state.state != "unavailable"

    # Check LSI sensor exists
    lsi_state = hass.states.get(f"sensor.test_pool_{SENSOR_LSI}")
    assert lsi_state is not None
    assert lsi_state.state != "unavailable"

    # Check water balance sensor exists
    balance_state = hass.states.get(f"sensor.test_pool_{SENSOR_WATER_BALANCE}")
    assert balance_state is not None
    assert balance_state.state in [s.value for s in WaterBalanceState]

    # Check FC/CYA ratio sensor exists
    ratio_state = hass.states.get(f"sensor.test_pool_{SENSOR_FC_CYA_RATIO}")
    assert ratio_state is not None


async def test_csi_sensor_attributes(
    hass: HomeAssistant,
    mock_source_entities: None,
    mock_config_entry_data: dict[str, Any],
) -> None:
    """Test CSI sensor has expected attributes."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data=mock_config_entry_data,
        options={},
    )
    entry.add_to_hass(hass)

    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    csi_state = hass.states.get(f"sensor.test_pool_{SENSOR_CSI}")
    assert csi_state is not None

    attrs = csi_state.attributes
    assert "ph" in attrs
    assert attrs["ph"] == 7.5
    assert "temperature_f" in attrs
    assert attrs["temperature_f"] == 84
    assert "calcium_hardness" in attrs
    assert attrs["calcium_hardness"] == 300
    assert "total_alkalinity" in attrs
    assert attrs["total_alkalinity"] == 80


async def test_fc_cya_ratio_attributes(
    hass: HomeAssistant,
    mock_source_entities: None,
    mock_config_entry_data: dict[str, Any],
) -> None:
    """Test FC/CYA ratio sensor has expected attributes."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data=mock_config_entry_data,
        options={},
    )
    entry.add_to_hass(hass)

    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    ratio_state = hass.states.get(f"sensor.test_pool_{SENSOR_FC_CYA_RATIO}")
    assert ratio_state is not None

    attrs = ratio_state.attributes
    assert "free_chlorine" in attrs
    assert attrs["free_chlorine"] == 5.0
    assert "cyanuric_acid" in attrs
    assert attrs["cyanuric_acid"] == 40
    assert "is_adequate" in attrs
    assert attrs["is_adequate"] is True


async def test_dosing_sensors_created(
    hass: HomeAssistant,
    mock_source_entities: None,
    mock_config_entry_data: dict[str, Any],
) -> None:
    """Test that dosing sensors are created when enabled."""
    # Set pH high to trigger acid dose
    hass.states.async_set("sensor.pool_ph", "7.8")

    entry = MockConfigEntry(
        domain=DOMAIN,
        data=mock_config_entry_data,
        options={},  # Use defaults (all dosing enabled)
    )
    entry.add_to_hass(hass)

    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    # Check acid dose sensor exists (entity ID derived from translation name)
    acid_state = hass.states.get("sensor.test_pool_acid_dose")
    assert acid_state is not None

    # Check chlorine dose sensor exists
    chlorine_state = hass.states.get("sensor.test_pool_chlorine_dose")
    assert chlorine_state is not None

    # Check alkalinity dose sensor exists
    alk_state = hass.states.get("sensor.test_pool_baking_soda_dose")
    assert alk_state is not None


async def test_dosing_sensor_attributes(
    hass: HomeAssistant,
    mock_source_entities: None,
    mock_config_entry_data: dict[str, Any],
) -> None:
    """Test dosing sensors have expected attributes."""
    # Set pH high to trigger acid dose
    hass.states.async_set("sensor.pool_ph", "7.8")

    entry = MockConfigEntry(
        domain=DOMAIN,
        data=mock_config_entry_data,
        options={},
    )
    entry.add_to_hass(hass)

    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    acid_state = hass.states.get("sensor.test_pool_acid_dose")
    assert acid_state is not None

    attrs = acid_state.attributes
    assert "chemical" in attrs
    assert "unit" in attrs


async def test_sensor_device_info(
    hass: HomeAssistant,
    mock_source_entities: None,
    mock_config_entry_data: dict[str, Any],
) -> None:
    """Test sensors have correct device info."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data=mock_config_entry_data,
        options={},
    )
    entry.add_to_hass(hass)

    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    entity_reg = er.async_get(hass)
    entity = entity_reg.async_get(f"sensor.test_pool_{SENSOR_CSI}")

    assert entity is not None
    assert entity.unique_id == f"{entry.entry_id}_{SENSOR_CSI}"


async def test_saltwater_pool_has_salt_sensor(
    hass: HomeAssistant,
    mock_source_entities: None,
    mock_config_entry_data_saltwater: dict[str, Any],
) -> None:
    """Test saltwater pools have salt dosing sensor."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data=mock_config_entry_data_saltwater,
        options={"enable_dose_salt": True},
    )
    entry.add_to_hass(hass)

    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    # Salt dose sensor should exist for saltwater pools
    salt_state = hass.states.get("sensor.salt_pool_salt_dose")
    assert salt_state is not None
