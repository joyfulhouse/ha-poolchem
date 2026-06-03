# Pool Chem

A Home Assistant custom integration that provides pool water chemistry analysis and dosing recommendations.

[![GitHub Release][releases-shield]][releases]
[![License][license-shield]](LICENSE)
[![HACS][hacs-shield]][hacs]
[![Project Maintenance][maintenance-shield]][maintenance]
[![GitHub Sponsors][sponsors-shield]][sponsors]
[![Ko-fi][kofi-shield]][kofi]

## What It Does

Pool Chem consumes sensor entities from any source — pool equipment integrations, ESPHome, MQTT,
manual input helpers — and produces calculated sensors for water balance indices and chemical dosing
recommendations. All chemistry math is delegated to the
[pypoolchem](https://github.com/joyfulhouse/pypoolchem) library; this integration is a thin Home
Assistant wrapper around it.

## Features

- **Water Balance Indices** — CSI (Calcium Saturation Index, primary, TFP methodology) and LSI (Langelier Saturation Index, traditional)
- **Water Balance State** — classifies water as balanced, slightly/severely corrosive, or slightly/severely scaling
- **FC/CYA Ratio Monitoring** — tracks chlorine effectiveness relative to stabilizer levels
- **Dosing Recommendations** — acid, chlorine, baking soda, calcium chloride, cyanuric acid, and salt; configurable chemical types and concentrations
- **Entity-Based Architecture** — works with ANY sensor source; no hard dependencies on specific integrations
- **Event-Driven Updates** — recalculates only when source sensors change; no polling

## Prerequisites

- Home Assistant 2024.1.0 or newer
- Source sensors for water chemistry readings (temperature, pH, free chlorine, total alkalinity, calcium hardness)

## Installation

See **[INSTALL.md](INSTALL.md)** for the complete guide.

**Quick version (HACS):** add this repository as a custom repository in HACS,
install **Pool Chem**, restart Home Assistant, then add the integration
from **Settings → Devices & Services**.

[![Open in HACS][hacs-repo-shield]][hacs-repo]

## Configuration

The integration is configured entirely through the Home Assistant UI.

**Step 1 — Pool Configuration:** pool name, volume (gallons), pool type (chlorine, saltwater, or mineral), and surface type (plaster, pebble, vinyl, fiberglass, or painted).

**Step 2 — Required Sensors:** map existing sensor entities for temperature (auto-detects °C/°F),
pH, free chlorine (FC), total alkalinity (TA), and calcium hardness (CH).

**Step 3 — Optional Sensors:** optionally map sensors for cyanuric acid (CYA/stabilizer), salt
(saltwater pools), total dissolved solids (TDS), and borates.

**Options (post-setup):** target chemistry values (pH, FC, TA, CH, CYA, salt), chemical types
(acid concentration, chlorine source), and per-sensor enable/disable toggles. Access via
**Settings → Devices & Services → Pool Chem → Configure**.

## Supported Equipment

Pool Chem works with any sensor entity. Tested source integrations include:

- [intellicenter](https://github.com/joyfulhouse/intellicenter) — Pentair IntelliCenter pool equipment
- [lamotte-spintouch](https://github.com/joyfulhouse/lamotte-spintouch) — LaMotte SpinTouch water testing
- ESPHome, MQTT, and `input_number` helpers

### Sensors Created

| Entity | Description |
|---|---|
| `sensor.{pool}_csi` | Calcium Saturation Index (−1.0 to +1.0 typical) |
| `sensor.{pool}_lsi` | Langelier Saturation Index |
| `sensor.{pool}_water_balance` | State: balanced, slightly_corrosive, slightly_scaling, severely_corrosive, severely_scaling |
| `sensor.{pool}_fc_cya_ratio` | FC/CYA ratio as a percentage (7.5 %+ recommended) |
| `sensor.{pool}_acid_dose` | Acid needed to reach target pH (fl oz) |
| `sensor.{pool}_chlorine_dose` | Chlorine needed to reach target FC (fl oz) |
| `sensor.{pool}_baking_soda_dose` | Baking soda needed to raise TA (oz) |
| `sensor.{pool}_calcium_dose` | Calcium chloride to raise CH (oz) |
| `sensor.{pool}_stabilizer_dose` | CYA needed to reach target (oz) |
| `sensor.{pool}_salt_dose` | Salt needed — saltwater pools only (lbs) |

### Water Balance Thresholds

| CSI Range | State |
|---|---|
| < −0.6 | Severely Corrosive |
| −0.6 to −0.3 | Slightly Corrosive |
| −0.3 to +0.3 | Balanced |
| +0.3 to +0.6 | Slightly Scaling |
| > +0.6 | Severely Scaling |

## Automation Examples

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

## Troubleshooting

See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for common problems and fixes.

Enable debug logging:

```yaml
logger:
  default: info
  logs:
    custom_components.poolchem: debug
```

## Development

This integration is built on the
[pypoolchem](https://github.com/joyfulhouse/pypoolchem) Python
library. See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) to set up a development
environment.

## Support

- **Issues:** <https://github.com/joyfulhouse/ha-poolchem/issues>
- **Discussions / questions:** open an issue with the `question` label.

> **Disclaimer:** This integration provides dosing recommendations based on mathematical
> calculations. Always verify recommendations against professional water testing and follow
> manufacturer guidelines for chemical handling. The authors are not responsible for any damage or
> injury resulting from use of this software.

## Support Development

If this project is useful to you, please consider supporting its development:

- [GitHub Sponsors][sponsors]
- [Ko-fi][kofi]

## License

This project is licensed under the **MIT** License — see
[LICENSE](LICENSE) for details.

## Credits

Built and maintained by [JoyfulHouse](https://github.com/joyfulhouse) with the
[pypoolchem](https://github.com/joyfulhouse/pypoolchem) library.

<!-- Badge links -->
[releases-shield]: https://img.shields.io/github/release/joyfulhouse/ha-poolchem.svg?style=for-the-badge
[releases]: https://github.com/joyfulhouse/ha-poolchem/releases
[license-shield]: https://img.shields.io/github/license/joyfulhouse/ha-poolchem.svg?style=for-the-badge
[hacs-shield]: https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge
[hacs]: https://github.com/hacs/integration
[hacs-repo-shield]: https://my.home-assistant.io/badges/hacs_repository.svg
[hacs-repo]: https://my.home-assistant.io/redirect/hacs_repository/?owner=joyfulhouse&repository=ha-poolchem&category=integration
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40btli-blue.svg?style=for-the-badge
[maintenance]: https://github.com/btli
[sponsors-shield]: https://img.shields.io/badge/sponsor-GitHub-EA4AAA.svg?style=for-the-badge&logo=githubsponsors&logoColor=white
[sponsors]: https://github.com/sponsors/btli
[kofi-shield]: https://img.shields.io/badge/Ko--fi-donate-FF5E5B.svg?style=for-the-badge&logo=ko-fi&logoColor=white
[kofi]: https://ko-fi.com/bryanli
