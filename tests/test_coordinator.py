"""Tests for Pool Chemistry coordinator."""

from __future__ import annotations

from typing import Any

from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.poolchem.const import (
    DOMAIN,
    WaterBalanceState,
)
from custom_components.poolchem.coordinator import PoolChemCoordinator


async def test_coordinator_calculates_csi(
    hass: HomeAssistant,
    mock_source_entities: None,
    mock_config_entry_data: dict[str, Any],
) -> None:
    """Test coordinator calculates CSI correctly."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data=mock_config_entry_data,
        options={},
    )
    entry.add_to_hass(hass)

    coordinator = PoolChemCoordinator(hass, entry)
    await coordinator.async_setup()

    assert coordinator.data is not None
    assert coordinator.data.csi is not None
    # With pH=7.5, temp=84, TA=80, CH=300, CYA=40, CSI should be slightly negative
    assert -1.0 < coordinator.data.csi < 1.0
    assert coordinator.data.balance_state in [
        WaterBalanceState.BALANCED,
        WaterBalanceState.SLIGHTLY_CORROSIVE,
        WaterBalanceState.SLIGHTLY_SCALING,
    ]


async def test_coordinator_calculates_lsi(
    hass: HomeAssistant,
    mock_source_entities: None,
    mock_config_entry_data: dict[str, Any],
) -> None:
    """Test coordinator calculates LSI correctly."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data=mock_config_entry_data,
        options={},
    )
    entry.add_to_hass(hass)

    coordinator = PoolChemCoordinator(hass, entry)
    await coordinator.async_setup()

    assert coordinator.data is not None
    assert coordinator.data.lsi is not None
    # LSI should also be reasonable
    assert -2.0 < coordinator.data.lsi < 2.0


async def test_coordinator_calculates_fc_cya_ratio(
    hass: HomeAssistant,
    mock_source_entities: None,
    mock_config_entry_data: dict[str, Any],
) -> None:
    """Test coordinator calculates FC/CYA ratio correctly."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data=mock_config_entry_data,
        options={},
    )
    entry.add_to_hass(hass)

    coordinator = PoolChemCoordinator(hass, entry)
    await coordinator.async_setup()

    assert coordinator.data is not None
    # FC=5, CYA=40 -> ratio = 5/40 * 100 = 12.5%
    assert coordinator.data.fc_cya_ratio == pytest.approx(12.5, rel=0.01)
    assert coordinator.data.fc_is_adequate is True  # 12.5% > 7.5% minimum


async def test_coordinator_handles_celsius_temperature(
    hass: HomeAssistant,
    mock_source_entities_celsius: None,
    mock_config_entry_data_minimal: dict[str, Any],
) -> None:
    """Test coordinator converts Celsius to Fahrenheit correctly."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data=mock_config_entry_data_minimal,
        options={},
    )
    entry.add_to_hass(hass)

    coordinator = PoolChemCoordinator(hass, entry)
    await coordinator.async_setup()

    assert coordinator.data is not None
    assert coordinator.data.water is not None
    # 28.89°C should convert to approximately 84°F
    assert coordinator.data.water.temperature_f == pytest.approx(84.0, rel=0.1)


async def test_coordinator_handles_unavailable_sensor(
    hass: HomeAssistant,
    mock_source_entities: None,
    mock_config_entry_data: dict[str, Any],
) -> None:
    """Test coordinator handles unavailable sensors gracefully."""
    # Make pH sensor unavailable
    hass.states.async_set("sensor.pool_ph", STATE_UNAVAILABLE)

    entry = MockConfigEntry(
        domain=DOMAIN,
        data=mock_config_entry_data,
        options={},
    )
    entry.add_to_hass(hass)

    coordinator = PoolChemCoordinator(hass, entry)
    await coordinator.async_setup()

    # CSI/LSI should not be calculable without pH
    assert coordinator.data is not None
    assert coordinator.data.csi is None
    assert coordinator.data.lsi is None
    assert coordinator.data.balance_state == WaterBalanceState.UNKNOWN
    assert coordinator.data.errors is not None
    assert "pH" in coordinator.data.errors[0]


async def test_coordinator_calculates_doses(
    hass: HomeAssistant,
    mock_source_entities: None,
    mock_config_entry_data: dict[str, Any],
) -> None:
    """Test coordinator calculates dosing recommendations."""
    # Set pH slightly high to need acid
    hass.states.async_set("sensor.pool_ph", "7.8")
    # Set FC low to need chlorine
    hass.states.async_set("sensor.pool_fc", "2.0")

    entry = MockConfigEntry(
        domain=DOMAIN,
        data=mock_config_entry_data,
        options={},
    )
    entry.add_to_hass(hass)

    coordinator = PoolChemCoordinator(hass, entry)
    await coordinator.async_setup()

    assert coordinator.data is not None

    # Should have acid dose recommendation (pH 7.8 -> 7.5)
    assert coordinator.data.dose_acid is not None
    assert coordinator.data.dose_acid.amount > 0

    # Should have chlorine dose recommendation (FC 2 -> 5)
    assert coordinator.data.dose_chlorine is not None
    assert coordinator.data.dose_chlorine.amount > 0


async def test_coordinator_updates_on_state_change(
    hass: HomeAssistant,
    mock_source_entities: None,
    mock_config_entry_data: dict[str, Any],
) -> None:
    """Test coordinator updates when source entities change."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data=mock_config_entry_data,
        options={},
    )
    entry.add_to_hass(hass)

    coordinator = PoolChemCoordinator(hass, entry)
    await coordinator.async_setup()

    initial_csi = coordinator.data.csi

    # Change pH
    hass.states.async_set("sensor.pool_ph", "7.8")
    await hass.async_block_till_done()

    # Trigger refresh (simulating state change event)
    await coordinator.async_request_refresh()

    # CSI should have changed
    assert coordinator.data.csi != initial_csi


async def test_coordinator_minimal_config(
    hass: HomeAssistant,
    mock_source_entities: None,
    mock_config_entry_data_minimal: dict[str, Any],
) -> None:
    """Test coordinator works with minimal configuration."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data=mock_config_entry_data_minimal,
        options={},
    )
    entry.add_to_hass(hass)

    coordinator = PoolChemCoordinator(hass, entry)
    await coordinator.async_setup()

    assert coordinator.data is not None
    # CSI/LSI should still work with defaults for optional sensors
    assert coordinator.data.csi is not None
    assert coordinator.data.lsi is not None
