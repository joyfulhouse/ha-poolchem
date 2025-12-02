# Home Assistant Pool Chemistry Integration

[![GitHub Release](https://img.shields.io/github/release/joyfulhouse/ha-poolchem.svg?style=flat-square)](https://github.com/joyfulhouse/ha-poolchem/releases)
[![License](https://img.shields.io/github/license/joyfulhouse/ha-poolchem.svg?style=flat-square)](LICENSE)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=flat-square)](https://github.com/hacs/integration)

A Home Assistant custom integration that provides pool water chemistry analysis and dosing recommendations. This integration consumes sensor entities from any source and produces calculated sensors for water balance indices and chemical dosing.

## Features

- **Water Balance Indices**
  - CSI (Calcium Saturation Index) - Primary index using TFP methodology
  - LSI (Langelier Saturation Index) - Traditional water balance index
  - Water balance state classification (balanced, corrosive, scaling)

- **FC/CYA Ratio Monitoring**
  - Track chlorine effectiveness relative to stabilizer levels
  - Adequacy check based on TFP recommendations

- **Dosing Recommendations**
  - Acid dose (muriatic acid or dry acid)
  - Chlorine dose (bleach, cal-hypo, dichlor, trichlor)
  - Alkalinity adjustment (baking soda)
  - Calcium hardness adjustment
  - Cyanuric acid (stabilizer) dose
  - Salt dose (for saltwater pools)

- **Entity-Based Architecture**
  - Works with ANY sensor source (pool equipment, ESPHome, MQTT, manual input helpers)
  - No hard dependencies on specific integrations
  - Event-driven updates when source sensors change

## Requirements

- Home Assistant 2024.1.0 or newer
- Python 3.13 or newer
- Source sensors for water chemistry readings

## Installation

### HACS (Recommended)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=joyfulhouse&repository=ha-poolchem&category=integration)

Click the button above, or manually add via HACS:

1. Open HACS in Home Assistant
2. Click the three dots menu in the top right
3. Select "Custom repositories"
4. Add `https://github.com/joyfulhouse/ha-poolchem` with category "Integration"
5. Click "Add"
6. Search for "Pool Chemistry" and install
7. Restart Home Assistant
8. Add the integration:

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=poolchem)

### Manual Installation

1. Download the latest release from the [releases page](https://github.com/joyfulhouse/ha-poolchem/releases)
2. Extract and copy `custom_components/poolchem` to your Home Assistant `config/custom_components/` directory
3. Restart Home Assistant
4. Add the integration via Settings > Devices & Services > Add Integration > Pool Chemistry

## Configuration

The integration is configured entirely through the Home Assistant UI.

### Step 1: Pool Configuration

- **Pool Name**: A friendly name for your pool
- **Pool Volume**: Volume in gallons
- **Pool Type**: Chlorine, Saltwater (SWG), or Mineral
- **Surface Type**: Plaster, Pebble, Vinyl, Fiberglass, or Painted

### Step 2: Required Sensors

Map your existing sensors for:
- Temperature (auto-detects Celsius/Fahrenheit)
- pH
- Free Chlorine (FC)
- Total Alkalinity (TA)
- Calcium Hardness (CH)

### Step 3: Optional Sensors

Optionally map sensors for:
- Cyanuric Acid (CYA/Stabilizer)
- Salt (for saltwater pools)
- Total Dissolved Solids (TDS)
- Borates

### Options (Post-Setup)

After initial setup, configure via the integration options:
- Target chemistry values (pH, FC, TA, CH, CYA, salt)
- Chemical types (acid concentration, chlorine source)
- Enable/disable individual dosing sensors

## Sensors Created

### Water Balance Sensors

| Sensor | Description |
|--------|-------------|
| `sensor.{pool}_csi` | Calcium Saturation Index (-1.0 to +1.0 typical) |
| `sensor.{pool}_lsi` | Langelier Saturation Index |
| `sensor.{pool}_water_balance` | State: balanced, slightly_corrosive, slightly_scaling, severely_corrosive, severely_scaling |
| `sensor.{pool}_fc_cya_ratio` | FC/CYA ratio as percentage (7.5%+ recommended) |

### Dosing Sensors

| Sensor | Unit | Description |
|--------|------|-------------|
| `sensor.{pool}_acid_dose` | fl oz | Acid needed to reach target pH |
| `sensor.{pool}_chlorine_dose` | fl oz | Chlorine needed to reach target FC |
| `sensor.{pool}_baking_soda_dose` | oz | Baking soda needed to raise TA |
| `sensor.{pool}_calcium_dose` | oz | Calcium chloride to raise CH |
| `sensor.{pool}_stabilizer_dose` | oz | CYA needed to reach target |
| `sensor.{pool}_salt_dose` | lbs | Salt needed (saltwater pools only) |

## Water Balance Thresholds

The integration uses CSI (Calcium Saturation Index) as the primary water balance indicator:

| CSI Range | State | Description |
|-----------|-------|-------------|
| < -0.6 | Severely Corrosive | Water will aggressively dissolve surfaces |
| -0.6 to -0.3 | Slightly Corrosive | Water tends to be corrosive |
| -0.3 to +0.3 | Balanced | Ideal range |
| +0.3 to +0.6 | Slightly Scaling | Water tends to deposit scale |
| > +0.6 | Severely Scaling | Water will deposit scale rapidly |

## Supported Chemical Types

### Acids (for lowering pH)
- Muriatic Acid 14.5%, 28.3%, 31.45%, 34.6%
- Dry Acid (Sodium Bisulfate)

### Chlorine Sources
- Liquid Bleach: 6%, 8.25%, 10%, 12.5%
- Cal-Hypo: 65%, 73%
- Dichlor
- Trichlor

## Example Automations

### Alert on Unbalanced Water

```yaml
automation:
  - alias: "Pool Water Balance Alert"
    trigger:
      - platform: state
        entity_id: sensor.pool_water_balance
        to:
          - "severely_corrosive"
          - "severely_scaling"
    action:
      - service: notify.mobile_app
        data:
          title: "Pool Water Alert"
          message: "Pool water is {{ states('sensor.pool_water_balance') }}. Check chemistry!"
```

### Daily Chemistry Report

```yaml
automation:
  - alias: "Daily Pool Chemistry Report"
    trigger:
      - platform: time
        at: "08:00:00"
    action:
      - service: notify.mobile_app
        data:
          title: "Pool Chemistry Report"
          message: >
            pH: {{ states('sensor.pool_ph') }}
            FC: {{ states('sensor.pool_fc') }} ppm
            CSI: {{ states('sensor.pool_csi') }}
            Balance: {{ states('sensor.pool_water_balance') }}
```

## Related Projects

- [pypoolchem](https://github.com/joyfulhouse/pypoolchem) - Core calculation library
- [intellicenter](https://github.com/joyfulhouse/intellicenter) - Pentair IntelliCenter integration
- [lamotte-spintouch](https://github.com/joyfulhouse/lamotte-spintouch) - LaMotte SpinTouch water testing

## Contributing

Contributions are welcome! Please read our [Contributing Guide](docs/CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This integration provides dosing recommendations based on mathematical calculations. Always verify recommendations against professional water testing and follow manufacturer guidelines for chemical handling. The authors are not responsible for any damage or injury resulting from use of this software.
