"""The Camera Object Detector integration."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform, CONF_API_KEY
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, CONF_AI_SERVICE, CONF_CAMERA_ENTITY
from .ai_client import get_ai_client

if TYPE_CHECKING:
    pass

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.BINARY_SENSOR]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Camera Object Detector component."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Camera Object Detector from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    # Validate camera entity exists
    camera_entity = entry.data[CONF_CAMERA_ENTITY]
    if not hass.states.get(camera_entity):
        raise ConfigEntryNotReady(f"Camera entity {camera_entity} not found")
    
    # Validate AI client can be created
    ai_service = entry.data[CONF_AI_SERVICE]
    api_key = entry.data.get(CONF_API_KEY)
    
    try:
        get_ai_client(ai_service, api_key)
    except ValueError as err:
        _LOGGER.error("Failed to create AI client: %s", err)
        raise ConfigEntryNotReady(f"Failed to create AI client: {err}") from err
    
    hass.data[DOMAIN][entry.entry_id] = entry.data

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
