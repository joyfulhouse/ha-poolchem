# Configuration

Full configuration reference for Pool Chem.

## Adding the Integration

After installation (see [INSTALL.md](../INSTALL.md)), add the integration through the Home Assistant UI:

1. Go to **Settings → Devices & Services**.
2. Click **+ Add Integration**.
3. Search for **Pool Chem** and select it.
4. Complete the three-step configuration flow described below.

## Configuration Flow

### Step 1 — Pool Configuration

| Field | Description | Example |
|---|---|---|
| Pool Name | Friendly name for your pool | `Backyard Pool` |
| Pool Volume | Volume in gallons | `15000` |
| Pool Type | Chlorine, Saltwater (SWG), or Mineral | `Saltwater` |
| Surface Type | Plaster, Pebble, Vinyl, Fiberglass, or Painted | `Pebble` |

### Step 2 — Required Sensors

Map existing sensor entities for:

| Sensor | Description | Example Entity |
|---|---|---|
| Temperature | Water temperature (°F or °C auto-detected) | `sensor.pool_temperature` |
| pH | Current pH level | `sensor.pool_ph` |
| Free Chlorine | FC in ppm | `sensor.pool_free_chlorine` |
| Total Alkalinity | TA in ppm | `sensor.pool_alkalinity` |
| Calcium Hardness | CH in ppm | `sensor.pool_calcium` |

### Step 3 — Optional Sensors

Optionally map sensors for:

| Sensor | Description | When to Use |
|---|---|---|
| Cyanuric Acid | CYA/Stabilizer in ppm | Outdoor pools with stabilizer |
| Salt | Salt level in ppm | Saltwater pools |
| TDS | Total dissolved solids | If available |
| Borates | Borate level in ppm | If using borates |

## Configuration Options

Access post-setup options via **Settings → Devices & Services → Pool Chem → Configure**.

### Target Chemistry Values

| Parameter | Default | Description |
|---|---|---|
| Target pH | 7.5 | Desired pH level |
| Target FC | 5.0 ppm | Desired free chlorine |
| Target TA | 80 ppm | Desired total alkalinity |
| Target CH | 350 ppm | Desired calcium hardness |
| Target CYA | 40 ppm | Desired cyanuric acid |
| Target Salt | 3200 ppm | Desired salt (SWG pools only) |

### Chemical Types

**Acid type** (for pH lowering):
- Muriatic Acid 14.5%, 28.3%, 31.45%, 34.6%
- Dry Acid (Sodium Bisulfate)

**Chlorine source**:
- Liquid Bleach 6%, 8.25%, 10%, 12.5%
- Cal-Hypo 65%, 73%
- Dichlor
- Trichlor

### Dosing Sensor Toggles

Individual dosing sensors can be enabled or disabled to match the chemicals you actually use.

## Reconfiguration

To change pool configuration (name, volume, type, surface, or sensor mappings), delete the
integration entry and re-add it. Target values and chemical types can be changed at any time
through the options flow without re-adding.

## Advanced Options

Each pool is configured as a separate integration instance. Users with multiple bodies of water
(pool + spa) add the integration multiple times, each with its own configuration and entity set.
