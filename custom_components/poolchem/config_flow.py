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
    CONF_TARGET_CH,
    CONF_TARGET_CYA,
    CONF_TARGET_FC,
    CONF_TARGET_PH,
    CONF_TARGET_SALT,
    CONF_TARGET_TA,
    CONF_TDS_ENTITY,
    CONF_TEMP_ENTITY,
    CONF_VOLUME_GALLONS,
    DEFAULT_ACID_TYPE,
    DEFAULT_CHLORINE_TYPE,
    DEFAULT_ENABLE_DOSE_ACID,
    DEFAULT_ENABLE_DOSE_ALKALINITY,
    DEFAULT_ENABLE_DOSE_CALCIUM,
    DEFAULT_ENABLE_DOSE_CHLORINE,
    DEFAULT_ENABLE_DOSE_CYA,
    DEFAULT_ENABLE_DOSE_SALT,
    DEFAULT_TARGET_CH,
    DEFAULT_TARGET_CYA,
    DEFAULT_TARGET_FC,
    DEFAULT_TARGET_PH,
    DEFAULT_TARGET_SALT,
    DEFAULT_TARGET_TA,
    DOMAIN,
    PoolType,
    SurfaceType,
)

_LOGGER = logging.getLogger(__name__)


class PoolChemConfigFlow(HAConfigFlow, domain=DOMAIN):  # type: ignore[call-arg]
    """Handle a config flow for Pool Chemistry."""

    VERSION = 1
    MINOR_VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._data: dict[str, Any] = {}

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlowHandler:
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)

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
            return await self.async_step_targets()

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

    async def async_step_targets(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the target chemistry values step."""
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_chemicals()

        is_saltwater = self._data.get(CONF_POOL_TYPE) == PoolType.SALTWATER

        schema_dict: dict[vol.Marker, Any] = {
            vol.Optional(CONF_TARGET_PH, default=DEFAULT_TARGET_PH): NumberSelector(
                NumberSelectorConfig(
                    min=6.8,
                    max=8.0,
                    step=0.1,
                    mode=NumberSelectorMode.BOX,
                )
            ),
            vol.Optional(CONF_TARGET_FC, default=DEFAULT_TARGET_FC): NumberSelector(
                NumberSelectorConfig(
                    min=1,
                    max=20,
                    step=0.5,
                    mode=NumberSelectorMode.BOX,
                    unit_of_measurement="ppm",
                )
            ),
            vol.Optional(CONF_TARGET_TA, default=DEFAULT_TARGET_TA): NumberSelector(
                NumberSelectorConfig(
                    min=50,
                    max=150,
                    step=5,
                    mode=NumberSelectorMode.BOX,
                    unit_of_measurement="ppm",
                )
            ),
            vol.Optional(CONF_TARGET_CH, default=DEFAULT_TARGET_CH): NumberSelector(
                NumberSelectorConfig(
                    min=150,
                    max=500,
                    step=10,
                    mode=NumberSelectorMode.BOX,
                    unit_of_measurement="ppm",
                )
            ),
            vol.Optional(CONF_TARGET_CYA, default=DEFAULT_TARGET_CYA): NumberSelector(
                NumberSelectorConfig(
                    min=0,
                    max=100,
                    step=5,
                    mode=NumberSelectorMode.BOX,
                    unit_of_measurement="ppm",
                )
            ),
        }

        # Only show salt target for saltwater pools
        if is_saltwater:
            schema_dict[vol.Optional(CONF_TARGET_SALT, default=DEFAULT_TARGET_SALT)] = (
                NumberSelector(
                    NumberSelectorConfig(
                        min=2500,
                        max=4000,
                        step=100,
                        mode=NumberSelectorMode.BOX,
                        unit_of_measurement="ppm",
                    )
                )
            )

        return self.async_show_form(
            step_id="targets",
            data_schema=vol.Schema(schema_dict),
        )

    async def async_step_chemicals(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the chemical types step."""
        if user_input is not None:
            self._data.update(user_input)
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
            self._data.update(user_input)
            # Create the config entry with all data
            return self.async_create_entry(
                title=self._data[CONF_POOL_NAME],
                data=self._data,
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
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the main options."""
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_chemicals()

        # Get current values or defaults
        current = self.config_entry.options

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_TARGET_PH,
                        default=current.get(CONF_TARGET_PH, DEFAULT_TARGET_PH),
                    ): NumberSelector(
                        NumberSelectorConfig(
                            min=6.8,
                            max=8.0,
                            step=0.1,
                            mode=NumberSelectorMode.BOX,
                        )
                    ),
                    vol.Optional(
                        CONF_TARGET_FC,
                        default=current.get(CONF_TARGET_FC, DEFAULT_TARGET_FC),
                    ): NumberSelector(
                        NumberSelectorConfig(
                            min=1,
                            max=20,
                            step=0.5,
                            mode=NumberSelectorMode.BOX,
                            unit_of_measurement="ppm",
                        )
                    ),
                    vol.Optional(
                        CONF_TARGET_TA,
                        default=current.get(CONF_TARGET_TA, DEFAULT_TARGET_TA),
                    ): NumberSelector(
                        NumberSelectorConfig(
                            min=50,
                            max=150,
                            step=5,
                            mode=NumberSelectorMode.BOX,
                            unit_of_measurement="ppm",
                        )
                    ),
                    vol.Optional(
                        CONF_TARGET_CH,
                        default=current.get(CONF_TARGET_CH, DEFAULT_TARGET_CH),
                    ): NumberSelector(
                        NumberSelectorConfig(
                            min=150,
                            max=500,
                            step=10,
                            mode=NumberSelectorMode.BOX,
                            unit_of_measurement="ppm",
                        )
                    ),
                    vol.Optional(
                        CONF_TARGET_CYA,
                        default=current.get(CONF_TARGET_CYA, DEFAULT_TARGET_CYA),
                    ): NumberSelector(
                        NumberSelectorConfig(
                            min=0,
                            max=100,
                            step=5,
                            mode=NumberSelectorMode.BOX,
                            unit_of_measurement="ppm",
                        )
                    ),
                    vol.Optional(
                        CONF_TARGET_SALT,
                        default=current.get(CONF_TARGET_SALT, DEFAULT_TARGET_SALT),
                    ): NumberSelector(
                        NumberSelectorConfig(
                            min=2500,
                            max=4000,
                            step=100,
                            mode=NumberSelectorMode.BOX,
                            unit_of_measurement="ppm",
                        )
                    ),
                }
            ),
            description_placeholders={
                "name": self.config_entry.data.get(CONF_POOL_NAME, "Pool")
            },
        )

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
