"""Config flow for Camera Object Detector integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector
import homeassistant.helpers.config_validation as cv

from .const import (
    CONF_AI_SERVICE,
    CONF_CAMERA_ENTITY,
    CONF_DETECTION_OBJECT,
    CONF_SCAN_INTERVAL,
    DEFAULT_AI_SERVICE,
    DEFAULT_DETECTION_OBJECT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    AI_SERVICE_MOONDREAM,
    AI_SERVICE_LOCAL,
    MOONDREAM_SUPPORTED_OBJECTS,
)

_LOGGER = logging.getLogger(__name__)


class CameraObjectDetectorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Camera Object Detector."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate that camera exists
            camera_entity = user_input[CONF_CAMERA_ENTITY]
            if not self.hass.states.get(camera_entity):
                errors[CONF_CAMERA_ENTITY] = "camera_not_found"
            
            # Validate API key if using Moondream
            if user_input[CONF_AI_SERVICE] == AI_SERVICE_MOONDREAM:
                if not user_input.get(CONF_API_KEY):
                    errors[CONF_API_KEY] = "api_key_required"
            
            if not errors:
                # Create unique ID based on camera entity
                await self.async_set_unique_id(f"{DOMAIN}_{camera_entity}")
                self._abort_if_unique_id_configured()
                
                return self.async_create_entry(
                    title=f"Camera Object Detector ({camera_entity})",
                    data=user_input,
                )

        # Build schema
        data_schema = vol.Schema(
            {
                vol.Required(CONF_CAMERA_ENTITY): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="camera")
                ),
                vol.Required(CONF_AI_SERVICE, default=DEFAULT_AI_SERVICE): vol.In(
                    {
                        AI_SERVICE_MOONDREAM: "Moondream AI (Cloud)",
                        AI_SERVICE_LOCAL: "Local (Coming Soon)",
                    }
                ),
                vol.Optional(CONF_API_KEY): cv.string,
                vol.Optional(
                    CONF_DETECTION_OBJECT, default=DEFAULT_DETECTION_OBJECT
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=MOONDREAM_SUPPORTED_OBJECTS,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                        custom_value=True,  # Permette valori personalizzati
                    )
                ),
                vol.Optional(
                    CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                ): vol.All(vol.Coerce(int), vol.Range(min=30, max=3600)),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> "CameraObjectDetectorOptionsFlow":
        """Get the options flow for this handler."""
        return CameraObjectDetectorOptionsFlow()


class CameraObjectDetectorOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Camera Object Detector."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate API key if using Moondream
            if user_input[CONF_AI_SERVICE] == AI_SERVICE_MOONDREAM:
                if not user_input.get(CONF_API_KEY):
                    errors[CONF_API_KEY] = "api_key_required"
            
            if not errors:
                # Update config entry data
                self.hass.config_entries.async_update_entry(
                    self.config_entry,
                    data={**self.config_entry.data, **user_input},
                )
                return self.async_create_entry(title="", data={})

        current_config = self.config_entry.data
        
        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_AI_SERVICE,
                    default=current_config.get(CONF_AI_SERVICE, DEFAULT_AI_SERVICE),
                ): vol.In(
                    {
                        AI_SERVICE_MOONDREAM: "Moondream AI (Cloud)",
                        AI_SERVICE_LOCAL: "Local (Coming Soon)",
                    }
                ),
                vol.Optional(
                    CONF_API_KEY,
                    default=current_config.get(CONF_API_KEY, ""),
                ): cv.string,
                vol.Optional(
                    CONF_DETECTION_OBJECT,
                    default=current_config.get(CONF_DETECTION_OBJECT, DEFAULT_DETECTION_OBJECT),
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=MOONDREAM_SUPPORTED_OBJECTS,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                        custom_value=True,
                    )
                ),
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=current_config.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                ): vol.All(vol.Coerce(int), vol.Range(min=30, max=3600)),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
            errors=errors,
        )
