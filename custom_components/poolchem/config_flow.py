"""Config flow for Pool Chemistry integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow as HAConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    EntitySelector,
    EntitySelectorConfig,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)
import voluptuous as vol

from .const import (
    ACID_TYPE_OPTIONS,
    CHLORINE_TYPE_OPTIONS,
    CONF_ACID_TYPE,
    CONF_BORATES_ENTITY,
    CONF_CH_ENTITY,
    CONF_CHLORINE_TYPE,
    CONF_CYA_ENTITY,
    CONF_ENABLE_DOSE_ACID,
    CONF_ENABLE_DOSE_ALKALINITY,
    CONF_ENABLE_DOSE_BORATES,
    CONF_ENABLE_DOSE_CALCIUM,
    CONF_ENABLE_DOSE_CHLORINE,
    CONF_ENABLE_DOSE_CYA,
    CONF_ENABLE_DOSE_SALT,
    CONF_FC_ENTITY,
    CONF_PH_ENTITY,
    CONF_POOL_NAME,
    CONF_POOL_TYPE,
    CONF_SALT_ENTITY,
    CONF_SURFACE_TYPE,
    CONF_TA_ENTITY,
    CONF_TDS_ENTITY,
    CONF_TEMP_ENTITY,
    CONF_VOLUME_GALLONS,
    DEFAULT_ACID_TYPE,
    DEFAULT_CHLORINE_TYPE,
    DEFAULT_ENABLE_DOSE_ACID,
    DEFAULT_ENABLE_DOSE_ALKALINITY,
    DEFAULT_ENABLE_DOSE_BORATES,
    DEFAULT_ENABLE_DOSE_CALCIUM,
    DEFAULT_ENABLE_DOSE_CHLORINE,
    DEFAULT_ENABLE_DOSE_CYA,
    DEFAULT_ENABLE_DOSE_SALT,
    DOMAIN,
    PoolType,
    SurfaceType,
)

_LOGGER = logging.getLogger(__name__)


class PoolChemConfigFlow(HAConfigFlow, domain=DOMAIN):
    """Handle a config flow for Pool Chemistry."""

    VERSION = 1
    MINOR_VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._data: dict[str, Any] = {}  # Pool info + entity mappings
        self._options: dict[str, Any] = {}  # Targets, chemicals, dosing toggles
        self._reconfigure_entry: ConfigEntry | None = None

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlowHandler:
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle reconfiguration of the integration."""
        self._reconfigure_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )
        if self._reconfigure_entry is None:
            return self.async_abort(reason="reconfigure_failed")

        # Pre-populate data from existing entry
        self._data = dict(self._reconfigure_entry.data)
        self._options = dict(self._reconfigure_entry.options)

        return await self.async_step_reconfigure_pool(user_input)

    async def async_step_reconfigure_pool(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle pool reconfiguration."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_reconfigure_entities()

        current = self._data

        return self.async_show_form(
            step_id="reconfigure_pool",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_POOL_NAME, default=current.get(CONF_POOL_NAME, "Pool")
                    ): TextSelector(TextSelectorConfig(type=TextSelectorType.TEXT)),
                    vol.Required(
                        CONF_VOLUME_GALLONS,
                        default=current.get(CONF_VOLUME_GALLONS, 15000),
                    ): NumberSelector(
                        NumberSelectorConfig(
                            min=100,
                            max=1000000,
                            step=100,
                            mode=NumberSelectorMode.BOX,
                            unit_of_measurement="gallons",
                        )
                    ),
                    vol.Required(
                        CONF_POOL_TYPE,
                        default=current.get(CONF_POOL_TYPE, PoolType.CHLORINE),
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=[pt.value for pt in PoolType],
                            mode=SelectSelectorMode.DROPDOWN,
                            translation_key="pool_type",
                        )
                    ),
                    vol.Required(
                        CONF_SURFACE_TYPE,
                        default=current.get(CONF_SURFACE_TYPE, SurfaceType.PLASTER),
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=[st.value for st in SurfaceType],
                            mode=SelectSelectorMode.DROPDOWN,
                            translation_key="surface_type",
                        )
                    ),
                }
            ),
            errors=errors,
        )

    async def async_step_reconfigure_entities(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle entity reconfiguration."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Filter out empty strings from optional entities
            filtered_input = {k: v for k, v in user_input.items() if v}
            # Remove any optional entities that were cleared
            for key in [
                CONF_CYA_ENTITY,
                CONF_SALT_ENTITY,
                CONF_TDS_ENTITY,
                CONF_BORATES_ENTITY,
            ]:
                if key in self._data and key not in filtered_input:
                    del self._data[key]
            self._data.update(filtered_input)

            # Update the config entry
            return self.async_update_reload_and_abort(
                self._reconfigure_entry,  # type: ignore[arg-type]
                data=self._data,
                options=self._options,
            )

        current = self._data
        sensor_selector = EntitySelector(EntitySelectorConfig(domain="sensor"))

        # Build schema - optional fields without defaults to allow empty selection
        schema_dict: dict[vol.Marker, Any] = {
            vol.Required(
                CONF_TEMP_ENTITY, default=current.get(CONF_TEMP_ENTITY)
            ): sensor_selector,
            vol.Required(
                CONF_PH_ENTITY, default=current.get(CONF_PH_ENTITY)
            ): sensor_selector,
            vol.Required(
                CONF_FC_ENTITY, default=current.get(CONF_FC_ENTITY)
            ): sensor_selector,
            vol.Required(
                CONF_TA_ENTITY, default=current.get(CONF_TA_ENTITY)
            ): sensor_selector,
            vol.Required(
                CONF_CH_ENTITY, default=current.get(CONF_CH_ENTITY)
            ): sensor_selector,
            vol.Optional(CONF_CYA_ENTITY): sensor_selector,
            vol.Optional(CONF_SALT_ENTITY): sensor_selector,
            vol.Optional(CONF_TDS_ENTITY): sensor_selector,
            vol.Optional(CONF_BORATES_ENTITY): sensor_selector,
        }

        # Set suggested values for optional fields if they exist
        suggested_values: dict[str, Any] = {}
        for key in [
            CONF_CYA_ENTITY,
            CONF_SALT_ENTITY,
            CONF_TDS_ENTITY,
            CONF_BORATES_ENTITY,
        ]:
            if current.get(key):
                suggested_values[key] = current[key]

        return self.async_show_form(
            step_id="reconfigure_entities",
            data_schema=self.add_suggested_values_to_schema(
                vol.Schema(schema_dict), suggested_values
            ),
            errors=errors,
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step - pool configuration."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_required_entities()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_POOL_NAME, default="Pool"): TextSelector(
                        TextSelectorConfig(type=TextSelectorType.TEXT)
                    ),
                    vol.Required(CONF_VOLUME_GALLONS): NumberSelector(
                        NumberSelectorConfig(
                            min=100,
                            max=1000000,
                            step=100,
                            mode=NumberSelectorMode.BOX,
                            unit_of_measurement="gallons",
                        )
                    ),
                    vol.Required(
                        CONF_POOL_TYPE, default=PoolType.CHLORINE
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=[pt.value for pt in PoolType],
                            mode=SelectSelectorMode.DROPDOWN,
                            translation_key="pool_type",
                        )
                    ),
                    vol.Required(
                        CONF_SURFACE_TYPE, default=SurfaceType.PLASTER
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=[st.value for st in SurfaceType],
                            mode=SelectSelectorMode.DROPDOWN,
                            translation_key="surface_type",
                        )
                    ),
                }
            ),
            errors=errors,
        )

    async def async_step_required_entities(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the required entities step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_optional_entities()

        sensor_selector = EntitySelector(EntitySelectorConfig(domain="sensor"))

        return self.async_show_form(
            step_id="required_entities",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_TEMP_ENTITY): sensor_selector,
                    vol.Required(CONF_PH_ENTITY): sensor_selector,
                    vol.Required(CONF_FC_ENTITY): sensor_selector,
                    vol.Required(CONF_TA_ENTITY): sensor_selector,
                    vol.Required(CONF_CH_ENTITY): sensor_selector,
                }
            ),
            errors=errors,
        )

    async def async_step_optional_entities(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the optional entities step."""
        if user_input is not None:
            # Filter out empty strings
            filtered_input = {k: v for k, v in user_input.items() if v}
            self._data.update(filtered_input)
            return await self.async_step_chemicals()

        sensor_selector = EntitySelector(EntitySelectorConfig(domain="sensor"))

        return self.async_show_form(
            step_id="optional_entities",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_CYA_ENTITY): sensor_selector,
                    vol.Optional(CONF_SALT_ENTITY): sensor_selector,
                    vol.Optional(CONF_TDS_ENTITY): sensor_selector,
                    vol.Optional(CONF_BORATES_ENTITY): sensor_selector,
                }
            ),
        )

    async def async_step_chemicals(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the chemical types step."""
        if user_input is not None:
            self._options.update(user_input)
            return await self.async_step_dosing_sensors()

        return self.async_show_form(
            step_id="chemicals",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_ACID_TYPE, default=DEFAULT_ACID_TYPE
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=ACID_TYPE_OPTIONS,
                            mode=SelectSelectorMode.DROPDOWN,
                            translation_key="acid_type",
                        )
                    ),
                    vol.Optional(
                        CONF_CHLORINE_TYPE, default=DEFAULT_CHLORINE_TYPE
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=CHLORINE_TYPE_OPTIONS,
                            mode=SelectSelectorMode.DROPDOWN,
                            translation_key="chlorine_type",
                        )
                    ),
                }
            ),
        )

    async def async_step_dosing_sensors(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the dosing sensors enablement step."""
        if user_input is not None:
            self._options.update(user_input)
            # Create the config entry with data (pool info + entities)
            # and options (targets, chemicals, dosing toggles)
            return self.async_create_entry(
                title=self._data[CONF_POOL_NAME],
                data=self._data,
                options=self._options,
            )

        is_saltwater = self._data.get(CONF_POOL_TYPE) == PoolType.SALTWATER

        schema_dict: dict[vol.Marker, Any] = {
            vol.Optional(CONF_ENABLE_DOSE_ACID, default=DEFAULT_ENABLE_DOSE_ACID): bool,
            vol.Optional(
                CONF_ENABLE_DOSE_CHLORINE, default=DEFAULT_ENABLE_DOSE_CHLORINE
            ): bool,
            vol.Optional(
                CONF_ENABLE_DOSE_ALKALINITY, default=DEFAULT_ENABLE_DOSE_ALKALINITY
            ): bool,
            vol.Optional(
                CONF_ENABLE_DOSE_CALCIUM, default=DEFAULT_ENABLE_DOSE_CALCIUM
            ): bool,
            vol.Optional(CONF_ENABLE_DOSE_CYA, default=DEFAULT_ENABLE_DOSE_CYA): bool,
            vol.Optional(
                CONF_ENABLE_DOSE_BORATES, default=DEFAULT_ENABLE_DOSE_BORATES
            ): bool,
        }

        # Only show salt dosing for saltwater pools
        if is_saltwater:
            schema_dict[
                vol.Optional(CONF_ENABLE_DOSE_SALT, default=DEFAULT_ENABLE_DOSE_SALT)
            ] = bool

        return self.async_show_form(
            step_id="dosing_sensors",
            data_schema=vol.Schema(schema_dict),
        )


class OptionsFlowHandler(OptionsFlow):
    """Handle options flow for Pool Chemistry integration."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry
        self._data: dict[str, Any] = dict(config_entry.options)

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,  # noqa: ARG002
    ) -> ConfigFlowResult:
        """Redirect to chemicals step (targets are now number entities)."""
        return await self.async_step_chemicals()

    async def async_step_chemicals(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Configure chemical types."""
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_dosing_sensors()

        current = self.config_entry.options

        return self.async_show_form(
            step_id="chemicals",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_ACID_TYPE,
                        default=current.get(CONF_ACID_TYPE, DEFAULT_ACID_TYPE),
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=ACID_TYPE_OPTIONS,
                            mode=SelectSelectorMode.DROPDOWN,
                            translation_key="acid_type",
                        )
                    ),
                    vol.Optional(
                        CONF_CHLORINE_TYPE,
                        default=current.get(CONF_CHLORINE_TYPE, DEFAULT_CHLORINE_TYPE),
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=CHLORINE_TYPE_OPTIONS,
                            mode=SelectSelectorMode.DROPDOWN,
                            translation_key="chlorine_type",
                        )
                    ),
                }
            ),
        )

    async def async_step_dosing_sensors(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Configure which dosing sensors to enable."""
        if user_input is not None:
            self._data.update(user_input)
            return self.async_create_entry(title="", data=self._data)

        current = self.config_entry.options
        is_saltwater = self.config_entry.data.get(CONF_POOL_TYPE) == PoolType.SALTWATER

        schema_dict: dict[vol.Marker, Any] = {
            vol.Optional(
                CONF_ENABLE_DOSE_ACID,
                default=current.get(CONF_ENABLE_DOSE_ACID, DEFAULT_ENABLE_DOSE_ACID),
            ): bool,
            vol.Optional(
                CONF_ENABLE_DOSE_CHLORINE,
                default=current.get(
                    CONF_ENABLE_DOSE_CHLORINE, DEFAULT_ENABLE_DOSE_CHLORINE
                ),
            ): bool,
            vol.Optional(
                CONF_ENABLE_DOSE_ALKALINITY,
                default=current.get(
                    CONF_ENABLE_DOSE_ALKALINITY, DEFAULT_ENABLE_DOSE_ALKALINITY
                ),
            ): bool,
            vol.Optional(
                CONF_ENABLE_DOSE_CALCIUM,
                default=current.get(
                    CONF_ENABLE_DOSE_CALCIUM, DEFAULT_ENABLE_DOSE_CALCIUM
                ),
            ): bool,
            vol.Optional(
                CONF_ENABLE_DOSE_CYA,
                default=current.get(CONF_ENABLE_DOSE_CYA, DEFAULT_ENABLE_DOSE_CYA),
            ): bool,
            vol.Optional(
                CONF_ENABLE_DOSE_BORATES,
                default=current.get(
                    CONF_ENABLE_DOSE_BORATES, DEFAULT_ENABLE_DOSE_BORATES
                ),
            ): bool,
        }

        # Only show salt dosing for saltwater pools
        if is_saltwater:
            schema_dict[
                vol.Optional(
                    CONF_ENABLE_DOSE_SALT,
                    default=current.get(
                        CONF_ENABLE_DOSE_SALT, DEFAULT_ENABLE_DOSE_SALT
                    ),
                )
            ] = bool

        return self.async_show_form(
            step_id="dosing_sensors",
            data_schema=vol.Schema(schema_dict),
        )
