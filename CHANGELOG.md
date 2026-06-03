# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0-rc.3] - 2025-12-02

### Added

- Interactive target configuration using number entity sliders in the options flow.
- Reconfiguration support and borate dosing sensor.
- Target chemistry values, chemical type selection, and per-sensor enable/disable toggles.
- Brand images for the Home Assistant brands repository.

### Changed

- Replaced static target configuration steps with number entity sliders.

## [0.1.0-rc1] - 2025-12-02

### Added

- Initial release of the Pool Chemistry integration.
- CSI (Calcium Saturation Index) and LSI (Langelier Saturation Index) water balance sensors.
- FC/CYA ratio monitoring sensor.
- Dosing recommendation sensors: acid, chlorine, baking soda, calcium chloride, cyanuric acid, and salt.
- Multi-step UI configuration flow (pool config → required sensors → optional sensors).
- Event-driven updates via `async_track_state_change_event` — no polling.
- Graceful degradation when source sensors are unavailable.
- Diagnostics support for troubleshooting.

<!-- Version comparison links -->
[Unreleased]: https://github.com/joyfulhouse/ha-poolchem/compare/v0.1.0-rc.3...HEAD
[0.1.0-rc.3]: https://github.com/joyfulhouse/ha-poolchem/compare/v0.1.0-rc1...v0.1.0-rc.3
[0.1.0-rc1]: https://github.com/joyfulhouse/ha-poolchem/releases/tag/v0.1.0-rc1
