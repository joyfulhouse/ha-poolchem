"""Diagnostics support for Pool Chemistry integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .coordinator import PoolChemCoordinator

TO_REDACT = {
    "unique_id",
    "entry_id",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,  # noqa: ARG001
    entry: ConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator: PoolChemCoordinator = entry.runtime_data

    # Get coordinator data
    data = coordinator.data

    diagnostics: dict[str, Any] = {
        "config_entry": {
            "entry_id": entry.entry_id,
            "version": entry.version,
            "minor_version": entry.minor_version,
            "domain": entry.domain,
            "title": entry.title,
            "data": async_redact_data(dict(entry.data), TO_REDACT),
            "options": dict(entry.options),
        },
        "coordinator": {
            "pool_name": coordinator.pool_name,
            "pool_volume": coordinator.pool_volume,
            "pool_type": coordinator.pool_type.value,
            "is_saltwater": coordinator.is_saltwater,
            "targets": {
                "ph": coordinator.target_ph,
                "fc": coordinator.target_fc,
                "ta": coordinator.target_ta,
                "ch": coordinator.target_ch,
                "cya": coordinator.target_cya,
                "salt": coordinator.target_salt,
            },
        },
        "data": None,
    }

    if data is not None:
        data_dict: dict[str, Any] = {
            "last_updated": data.last_updated.isoformat()
            if data.last_updated
            else None,
            "errors": data.errors,
            "csi": data.csi,
            "lsi": data.lsi,
            "balance_state": data.balance_state.value if data.balance_state else None,
            "fc_cya_ratio": data.fc_cya_ratio,
            "fc_is_adequate": data.fc_is_adequate,
        }

        # Add water chemistry if available
        if data.water:
            data_dict["water"] = {
                "ph": data.water.ph,
                "temperature_f": data.water.temperature_f,
                "free_chlorine": data.water.free_chlorine,
                "total_alkalinity": data.water.total_alkalinity,
                "calcium_hardness": data.water.calcium_hardness,
                "cyanuric_acid": data.water.cyanuric_acid,
                "salt": data.water.salt,
                "tds": data.water.tds,
                "borates": data.water.borates,
            }

        # Add dosing data if available
        doses: dict[str, Any] = {}
        for dose_name in [
            "dose_acid",
            "dose_chlorine",
            "dose_alkalinity",
            "dose_calcium",
            "dose_cya",
            "dose_salt",
        ]:
            dose = getattr(data, dose_name, None)
            if dose is not None:
                doses[dose_name] = {
                    "chemical": dose.chemical.name,
                    "amount": dose.amount,
                    "unit": dose.unit,
                    "amount_volume": dose.amount_volume,
                    "volume_unit": dose.volume_unit,
                    "notes": dose.notes,
                }
        if doses:
            data_dict["doses"] = doses

        diagnostics["data"] = data_dict

    return diagnostics
