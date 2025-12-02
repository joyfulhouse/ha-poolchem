# Installation Guide

This guide covers all methods for installing the Pool Chemistry integration.

## Prerequisites

- Home Assistant 2024.1.0 or newer
- Source sensors for pool water chemistry readings (temperature, pH, chlorine, etc.)

## Installation Methods

### Method 1: HACS (Recommended)

[HACS](https://hacs.xyz/) (Home Assistant Community Store) is the recommended installation method.

#### Quick Install via My Home Assistant

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=joyfulhouse&repository=ha-poolchem&category=integration)

Click the button above to add this repository to HACS, then:

1. Click "Download" in the bottom right
2. Select the version and click "Download"
3. Restart Home Assistant
4. Add the integration (see [Adding the Integration](#adding-the-integration))

#### Manual HACS Installation

If the button above doesn't work:

1. Open Home Assistant
2. Navigate to **HACS** in the sidebar
3. Click the **three dots menu** (top right)
4. Select **Custom repositories**
5. Enter repository URL: `https://github.com/joyfulhouse/ha-poolchem`
6. Select category: **Integration**
7. Click **Add**
8. Search for "Pool Chemistry" in HACS
9. Click **Download**
10. Restart Home Assistant
11. Add the integration (see [Adding the Integration](#adding-the-integration))

### Method 2: Manual Installation

1. Download the latest release from the [GitHub releases page](https://github.com/joyfulhouse/ha-poolchem/releases)

2. Extract the downloaded file

3. Copy the `custom_components/poolchem` folder to your Home Assistant configuration directory:
   ```
   config/
   └── custom_components/
       └── poolchem/
           ├── __init__.py
           ├── manifest.json
           ├── config_flow.py
           ├── coordinator.py
           ├── sensor.py
           └── ...
   ```

4. Restart Home Assistant

5. Add the integration (see [Adding the Integration](#adding-the-integration))

### Method 3: Docker Development Setup

For development or testing with Docker:

```yaml
# docker-compose.yaml
services:
  homeassistant:
    image: homeassistant/home-assistant:latest
    volumes:
      - ./config:/config
      - ./ha-poolchem/custom_components/poolchem:/config/custom_components/poolchem
```

## Adding the Integration

After installation, add the integration through the Home Assistant UI:

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=poolchem)

Or manually:

1. Go to **Settings** > **Devices & Services**
2. Click **+ Add Integration** (bottom right)
3. Search for "Pool Chemistry"
4. Click to begin setup

## Configuration Steps

### Step 1: Pool Configuration

| Field | Description | Example |
|-------|-------------|---------|
| Pool Name | Friendly name for your pool | "Backyard Pool" |
| Pool Volume | Volume in gallons | 15000 |
| Pool Type | Chlorine, Saltwater, or Mineral | Saltwater |
| Surface Type | Plaster, Pebble, Vinyl, Fiberglass, Painted | Pebble |

### Step 2: Required Sensors

Select existing sensor entities for:

| Sensor | Description | Example Entity |
|--------|-------------|----------------|
| Temperature | Water temperature (°F or °C) | `sensor.pool_temperature` |
| pH | Current pH level | `sensor.pool_ph` |
| Free Chlorine | FC in ppm | `sensor.pool_free_chlorine` |
| Total Alkalinity | TA in ppm | `sensor.pool_alkalinity` |
| Calcium Hardness | CH in ppm | `sensor.pool_calcium` |

### Step 3: Optional Sensors

Optionally select sensors for:

| Sensor | Description | When to Use |
|--------|-------------|-------------|
| Cyanuric Acid | CYA/Stabilizer in ppm | Outdoor pools with stabilizer |
| Salt | Salt level in ppm | Saltwater pools |
| TDS | Total dissolved solids | If available |
| Borates | Borate level in ppm | If using borates |

## Post-Installation Configuration

After initial setup, configure additional options:

1. Go to **Settings** > **Devices & Services**
2. Find "Pool Chemistry" and click **Configure**

### Target Chemistry Values

Set your desired target values for dosing calculations:

| Parameter | Default | Description |
|-----------|---------|-------------|
| Target pH | 7.5 | Desired pH level |
| Target FC | 5.0 ppm | Desired free chlorine |
| Target TA | 80 ppm | Desired total alkalinity |
| Target CH | 350 ppm | Desired calcium hardness |
| Target CYA | 40 ppm | Desired cyanuric acid |
| Target Salt | 3200 ppm | Desired salt (SWG only) |

### Chemical Types

Select the chemicals you use:

**Acid Type:**
- Muriatic Acid (various concentrations)
- Dry Acid (Sodium Bisulfate)

**Chlorine Type:**
- Liquid Bleach (various concentrations)
- Cal-Hypo
- Dichlor
- Trichlor

### Dosing Sensors

Enable or disable individual dosing sensors based on your needs.

## Troubleshooting

### Integration Not Showing

1. Verify files are in `config/custom_components/poolchem/`
2. Check Home Assistant logs for errors
3. Restart Home Assistant

### Sensors Show "Unknown"

1. Verify source sensors have valid numeric values
2. Check that required sensors are not "unavailable"
3. Review Home Assistant logs

### Calculations Seem Wrong

1. Verify source sensor units (especially temperature)
2. Check that pool volume is in gallons
3. Review target values in options

### Getting Diagnostics

For troubleshooting, download diagnostics:

1. Go to **Settings** > **Devices & Services**
2. Find "Pool Chemistry"
3. Click the three dots menu
4. Select **Download diagnostics**

## Updating

### Via HACS

1. Open HACS
2. Go to **Integrations**
3. Find "Pool Chemistry"
4. Click **Update** if available
5. Restart Home Assistant

### Manual Update

1. Download the new release
2. Replace the `custom_components/poolchem` folder
3. Restart Home Assistant

## Uninstalling

1. Go to **Settings** > **Devices & Services**
2. Find "Pool Chemistry"
3. Click the three dots menu
4. Select **Delete**
5. Remove the integration via HACS or delete the `poolchem` folder
6. Restart Home Assistant
