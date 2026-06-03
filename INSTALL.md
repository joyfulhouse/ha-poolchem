# Installing Pool Chem

## Prerequisites

- Home Assistant 2024.1.0 or newer.
- [HACS](https://hacs.xyz) installed (recommended), or filesystem access to your
  Home Assistant `config` directory (for manual installation).

## Method 1 — HACS (recommended)

1. Open **HACS** in Home Assistant.
2. Click the **⋮** menu → **Custom repositories**.
3. Add `https://github.com/joyfulhouse/ha-poolchem` with category **Integration**.
4. Search for **Pool Chem** and click **Download**.
5. **Restart Home Assistant.**

Or use this one-click link:

[![Open in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=joyfulhouse&repository=ha-poolchem&category=integration)

## Method 2 — Manual installation

1. Download the latest release from the
   [releases page](https://github.com/joyfulhouse/ha-poolchem/releases).
2. Copy the `custom_components/poolchem` folder into your Home Assistant
   `config/custom_components/` directory. The result should be
   `config/custom_components/poolchem/`.
3. **Restart Home Assistant.**

## Adding the Integration

1. Go to **Settings → Devices & Services**.
2. Click **+ Add Integration**.
3. Search for **Pool Chem** and select it.
4. Follow the configuration flow.

## Verifying

After setup, the integration's devices and entities appear under
**Settings → Devices & Services → Pool Chem**.

## Updating

- **HACS:** update from the HACS dashboard when a new version is available, then
  restart Home Assistant.
- **Manual:** replace the `custom_components/poolchem` folder with the new
  release and restart.

## Troubleshooting

If the integration does not appear or fails to set up, see the **Troubleshooting**
section of the [README](README.md#troubleshooting) and enable debug logging:

```yaml
logger:
  default: info
  logs:
    custom_components.poolchem: debug
```
