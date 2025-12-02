# Pool Chemistry Reference

This document explains the water chemistry concepts and calculations used by the Pool Chemistry integration.

## Water Balance Indices

### Calcium Saturation Index (CSI)

The CSI is the **primary water balance index** used by this integration. It's based on the methodology from Trouble Free Pool (TFP) and accounts for cyanuric acid's buffering effect on alkalinity.

**Formula:**
```
CSI = pH + TF + CF + AF - 12.1
```

Where:
- **pH**: Actual measured pH
- **TF**: Temperature Factor (based on water temperature)
- **CF**: Calcium Factor (log10 of calcium hardness)
- **AF**: Adjusted Alkalinity Factor (accounts for CYA buffering)

**Interpretation:**

| CSI Value | Condition | Effect |
|-----------|-----------|--------|
| < -0.6 | Severely Corrosive | Rapid etching of plaster, metal corrosion |
| -0.6 to -0.3 | Slightly Corrosive | Gradual surface damage |
| -0.3 to +0.3 | **Balanced** | Ideal range for pool water |
| +0.3 to +0.6 | Slightly Scaling | Calcium deposits may form |
| > +0.6 | Severely Scaling | Rapid scale formation |

### Langelier Saturation Index (LSI)

The LSI is the **traditional water balance index**. It's provided for reference but doesn't account for CYA's effect on effective alkalinity.

**Formula:**
```
LSI = pH - pHs
```

Where pHs is the pH at saturation, calculated from temperature, TDS, calcium hardness, and total alkalinity.

## FC/CYA Relationship

Free chlorine (FC) effectiveness depends heavily on cyanuric acid (CYA) levels. The FC/CYA ratio indicates chlorine adequacy.

**Calculation:**
```
FC/CYA Ratio = (FC / CYA) × 100%
```

**Recommended Minimums:**

| Pool Type | Minimum FC/CYA Ratio |
|-----------|---------------------|
| Traditional Chlorine | 7.5% |
| Saltwater (SWG) | 5.0% |

**Example:**
- CYA = 40 ppm
- Minimum FC for traditional pool = 40 × 0.075 = 3.0 ppm
- Minimum FC for saltwater pool = 40 × 0.05 = 2.0 ppm

## Target Chemistry Values

### Default Targets

| Parameter | Default Target | Typical Range |
|-----------|---------------|---------------|
| pH | 7.5 | 7.2 - 7.8 |
| Free Chlorine | 5.0 ppm | 3 - 7 ppm |
| Total Alkalinity | 80 ppm | 60 - 120 ppm |
| Calcium Hardness | 350 ppm | 200 - 400 ppm |
| Cyanuric Acid | 40 ppm | 30 - 50 ppm |
| Salt (SWG) | 3200 ppm | 2700 - 3400 ppm |

### Surface Type Considerations

Different pool surfaces have different calcium hardness preferences:

| Surface | Recommended CH |
|---------|---------------|
| Plaster | 250 - 400 ppm |
| Pebble/Aggregate | 200 - 400 ppm |
| Vinyl | 150 - 250 ppm |
| Fiberglass | 200 - 400 ppm |

## Dosing Calculations

### pH Adjustment (Acid Dosing)

Lowering pH requires acid. The amount depends on:
- Current pH and target pH
- Pool volume
- Total alkalinity (higher TA = more acid needed)
- Temperature (affects carbonate chemistry)
- Borates (if present, affect buffering)

**Supported Acids:**
| Acid Type | Concentration |
|-----------|--------------|
| Muriatic Acid | 14.5%, 28.3%, 31.45%, 34.6% |
| Dry Acid (Sodium Bisulfate) | ~93% |

### Chlorine Dosing

Raising FC requires chlorine. The amount depends on:
- Current FC and target FC
- Pool volume
- Chlorine source strength

**Supported Chlorine Sources:**
| Source | Available Chlorine |
|--------|-------------------|
| Liquid Bleach | 6%, 8.25%, 10%, 12.5% |
| Cal-Hypo | 65%, 73% |
| Dichlor | ~56% |
| Trichlor | ~90% |

**Note:** Dichlor and Trichlor also add CYA. This integration calculates the CYA contribution in the notes attribute.

### Alkalinity Adjustment

Raising TA uses baking soda (sodium bicarbonate).

**Formula:**
```
Ounces = (Target TA - Current TA) × Pool Gallons × 0.000214
```

### Calcium Hardness Adjustment

Raising CH uses calcium chloride.

**Formula:**
```
Ounces = (Target CH - Current CH) × Pool Gallons × 0.000177
```

### Cyanuric Acid Adjustment

Raising CYA uses stabilizer (cyanuric acid).

**Formula:**
```
Ounces = (Target CYA - Current CYA) × Pool Gallons × 0.00013
```

### Salt Adjustment (Saltwater Pools)

Raising salt uses pool salt.

**Formula:**
```
Pounds = (Target Salt - Current Salt) × Pool Gallons × 0.0000834
```

## Temperature Effects

Temperature affects:
- **CSI/LSI calculations**: Higher temperatures increase saturation
- **pH adjustment**: Warmer water requires slightly more acid
- **Chlorine effectiveness**: Higher temps reduce chlorine stability

The integration auto-detects temperature units (°C or °F) from the source sensor's `unit_of_measurement` attribute and converts as needed.

## Borates

Borates (typically from boric acid or borax) provide:
- pH buffering (reduces pH drift)
- Algae inhibition
- Softer feel

When borates are present, they affect pH adjustment calculations. The integration accounts for this if a borates sensor is configured.

## References

- [Trouble Free Pool](https://www.troublefreepool.com/) - TFP methodology
- [Pool Math App](https://www.troublefreepool.com/blog/pool-math/) - Calculation reference
- APSP/ANSI Standards - Industry guidelines
