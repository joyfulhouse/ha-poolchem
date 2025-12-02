# Architecture

This document describes the architecture and design decisions of the Pool Chemistry integration.

## Overview

The Pool Chemistry integration follows a modular architecture designed around Home Assistant's integration patterns. It acts as a "virtual" integration that consumes data from other sensors and produces calculated outputs.

```
┌─────────────────────────────────────────────────────────────────┐
│                     Source Entities                              │
│  (intellicenter, lamotte-spintouch, ESPHome, input_number, etc) │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ state_changed events
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  PoolChemCoordinator                             │
│                                                                  │
│  1. Collect current states from mapped entities                  │
│  2. Auto-detect temperature units (C→F conversion)               │
│  3. Build WaterChemistry model via pypoolchem                    │
│  4. Call pypoolchem calculation functions (CSI, LSI, dosing)     │
│  5. Store results in PoolChemData dataclass                      │
│  6. Notify sensor entities of update                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ coordinator.data
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Sensor Entities                             │
│                                                                  │
│  sensor.{pool}_csi           sensor.{pool}_acid_dose            │
│  sensor.{pool}_lsi           sensor.{pool}_chlorine_dose        │
│  sensor.{pool}_fc_cya_ratio  sensor.{pool}_baking_soda_dose     │
│  sensor.{pool}_water_balance sensor.{pool}_calcium_dose         │
│                              sensor.{pool}_stabilizer_dose      │
│                              sensor.{pool}_salt_dose            │
└─────────────────────────────────────────────────────────────────┘
```

## Design Principles

### 1. Entity-Based, Not Integration-Based

This integration depends on **entities**, not other integrations. It reads state from any sensor entity the user selects. This allows users to source data from:

- Pool equipment integrations (IntelliCenter, Pentair ScreenLogic, etc.)
- Water testing integrations (LaMotte SpinTouch, etc.)
- ESPHome sensors
- MQTT sensors
- Manual `input_number` helpers

### 2. Event-Driven Updates

The coordinator uses `async_track_state_change_event` to listen for changes in source entities. When any mapped sensor changes, the coordinator:

1. Collects all current sensor values
2. Recalculates water chemistry
3. Updates all dependent sensor entities

There is no polling interval - updates only occur when source data changes.

### 3. Graceful Degradation

When sensors are unavailable or missing:

- Water balance calculations require temperature, pH, TA, and CH
- FC/CYA ratio only needs FC and CYA
- Individual dosing sensors can function with partial data
- Clear error states indicate what's missing

### 4. Single Config Entry Per Pool

Each pool is configured as a separate integration instance. Users with multiple bodies of water (pool + spa) add the integration multiple times, each with its own configuration.

### 5. Calculation Logic in pypoolchem

All chemistry calculations live in the `pypoolchem` library. This integration is a thin wrapper that:

- Handles Home Assistant integration lifecycle
- Maps entity states to chemistry parameters
- Exposes calculation results as sensors

## File Structure

```
custom_components/poolchem/
├── __init__.py          # Integration setup/teardown
├── manifest.json        # Integration metadata
├── const.py             # Constants, defaults, enums
├── config_flow.py       # UI configuration flows
├── coordinator.py       # Data coordination and calculations
├── sensor.py            # Sensor entity definitions
├── entity.py            # Base entity class
├── diagnostics.py       # Debug diagnostics
├── strings.json         # Default strings
└── translations/
    └── en.json          # English translations
```

## Key Components

### PoolChemCoordinator

The coordinator (`coordinator.py`) is the heart of the integration:

- **Initialization**: Builds entity map from config entry data
- **Event Handling**: Subscribes to state changes for all mapped entities
- **Data Collection**: Reads current states, handles unit conversion
- **Calculations**: Invokes pypoolchem functions for CSI, LSI, dosing
- **Data Storage**: Stores results in `PoolChemData` dataclass

### Config Flow

The config flow (`config_flow.py`) implements a multi-step setup:

1. **User Step**: Pool name, volume, type, surface
2. **Required Entities**: Temperature, pH, FC, TA, CH sensors
3. **Optional Entities**: CYA, salt, TDS, borates sensors

An options flow allows post-setup configuration of:
- Target chemistry values
- Chemical types
- Dosing sensor toggles

### Sensor Entities

Sensors (`sensor.py`) use a descriptor pattern:

- `PoolChemSensorEntityDescription` defines each sensor type
- Value functions extract data from `PoolChemData`
- Attribute functions provide additional context
- Availability functions determine sensor state

## Data Flow

1. **State Change Event**
   - Source entity changes state
   - `async_track_state_change_event` fires callback

2. **Coordinator Refresh**
   - `_handle_state_change` schedules refresh
   - `_async_update_data` collects all entity states

3. **Chemistry Calculation**
   - Temperature converted to Fahrenheit if needed
   - `WaterChemistry` model built with current values
   - CSI, LSI calculated via pypoolchem
   - Dosing recommendations calculated

4. **Sensor Updates**
   - Coordinator notifies all sensor entities
   - Sensors read from `coordinator.data`
   - Home Assistant state machine updated

## Error Handling

- **Missing Entities**: Logged, partial calculations continue
- **Invalid Values**: Caught, reported in `data.errors`
- **Calculation Failures**: Logged with debug info
- **Unavailable Sensors**: Reflected in sensor availability

## Testing Strategy

Tests use `pytest-homeassistant-custom-component`:

- **Config Flow Tests**: Verify multi-step setup
- **Coordinator Tests**: Verify calculations with mock entities
- **Sensor Tests**: Verify entity creation and attributes

## Future Considerations

- **Services**: `poolchem.calculate_dose` for automation use
- **Events**: Fire events when water goes out of balance
- **Statistics**: Long-term tracking via HA statistics
- **Presets**: Common pool configurations
