# Troubleshooting

Common problems with Pool Chem and how to resolve them.

## Common Issues

### Integration Not Appearing After Installation

1. Verify the files are present at `config/custom_components/poolchem/`.
2. Check Home Assistant logs for errors mentioning `poolchem`.
3. Restart Home Assistant and try again.

### Sensors Show "Unknown" or "Unavailable"

1. Verify source sensors have valid numeric values (not "unavailable" or "unknown").
2. Confirm that all required sensors (temperature, pH, FC, TA, CH) are mapped and reporting.
3. Check the temperature sensor's `unit_of_measurement` attribute — it must be `°C` or `°F`.
4. Review Home Assistant logs for calculation errors.

### Calculations Seem Wrong

1. Verify source sensor units — temperature must be in °C or °F; concentrations must be in ppm.
2. Confirm pool volume is in gallons, not liters.
3. Review target chemistry values in the options flow.
4. Cross-check with the formulas in [CHEMISTRY.md](CHEMISTRY.md).

### Dosing Sensors Missing

Dosing sensors may be disabled in the options flow. Go to
**Settings → Devices & Services → Pool Chem → Configure** and enable the sensors you need.

### No Updates After Source Sensor Changes

The integration uses event-driven updates — it subscribes to state-change events for each mapped
entity. If updates stop:

1. Confirm source entities are still reporting state changes.
2. Reload the integration from **Settings → Devices & Services → Pool Chem → ⋮ → Reload**.

## Enabling Debug Logging

Add to your `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.poolchem: debug
```

Restart Home Assistant, reproduce the issue, then review logs at
**Settings → System → Logs**.

### Downloading Diagnostics

For detailed troubleshooting information:

1. Go to **Settings → Devices & Services**.
2. Find **Pool Chem** and click the three-dot menu.
3. Select **Download diagnostics**.

Include the diagnostics file when opening a bug report.

## Getting Help

If you are still stuck, open an issue at
<https://github.com/joyfulhouse/ha-poolchem/issues> with:

- Home Assistant version
- Integration version
- Steps to reproduce
- Relevant log entries
- Diagnostics file (if possible)
