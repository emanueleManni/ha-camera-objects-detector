"""The Camera Object Detector integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.components.camera import async_get_image
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, Platform
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse, SupportsResponse
from homeassistant.exceptions import ConfigEntryNotReady, ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType
from homeassistant.util import dt as dt_util

from .ai_client import get_ai_client
from .const import (
    ATTR_CONFIDENCE,
    ATTR_DETECTED_OBJECTS,
    ATTR_DETECTION_OBJECT,
    ATTR_IMAGE_TIME,
    ATTR_OBJECT_COUNT,
    ATTR_OBJECT_PRESENT,
    ATTR_REQUEST_ID,
    CONF_AI_SERVICE,
    CONF_CAMERA_ENTITY,
    CONF_DETECTION_OBJECT,
    CONF_DISABLE_BINARY_SENSOR,
    DOMAIN,
    SERVICE_DETECT_OBJECT,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.BINARY_SENSOR]

# Service schema for detect_object
SERVICE_DETECT_OBJECT_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_CAMERA_ENTITY): cv.entity_id,
        vol.Required(CONF_DETECTION_OBJECT): cv.string,
        vol.Optional(CONF_AI_SERVICE): cv.string,
        vol.Optional(CONF_API_KEY): cv.string,
    }
)


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

    # Setup platforms only if binary sensor is not disabled
    disable_binary_sensor = entry.data.get(CONF_DISABLE_BINARY_SENSOR, False)
    
    if not disable_binary_sensor:
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
        _LOGGER.info("Binary sensor enabled for entry %s", entry.entry_id)
    else:
        _LOGGER.info("Binary sensor disabled for entry %s - using action only", entry.entry_id)

    # Register service only once (on first integration setup)
    if not hass.services.has_service(DOMAIN, SERVICE_DETECT_OBJECT):
        
        async def handle_detect_object(call: ServiceCall) -> ServiceResponse:
            """Handle the detect_object service call."""
            camera_entity = call.data[CONF_CAMERA_ENTITY]
            detection_object = call.data[CONF_DETECTION_OBJECT]
            ai_service = call.data.get(CONF_AI_SERVICE)
            api_key = call.data.get(CONF_API_KEY)

            # Validate camera exists
            if not hass.states.get(camera_entity):
                raise ServiceValidationError(
                    f"Camera entity {camera_entity} not found",
                    translation_domain=DOMAIN,
                    translation_key="camera_not_found",
                )

            # If AI service not specified, try to find one from existing config entries
            if not ai_service:
                # Look for any configured entry to get default AI service
                for entry_id, entry_data in hass.data[DOMAIN].items():
                    if isinstance(entry_data, dict) and CONF_AI_SERVICE in entry_data:
                        ai_service = entry_data[CONF_AI_SERVICE]
                        api_key = entry_data.get(CONF_API_KEY)
                        _LOGGER.debug(
                            "Using AI service from config: %s", ai_service
                        )
                        break

            if not ai_service:
                raise ServiceValidationError(
                    "No AI service specified. Either configure the integration via UI "
                    "or specify 'ai_service' and 'api_key' in the service call",
                    translation_domain=DOMAIN,
                    translation_key="no_ai_service",
                )

            try:
                # Create AI client
                ai_client = get_ai_client(ai_service, api_key)

                # Get image from camera
                _LOGGER.debug("Fetching image from camera: %s", camera_entity)
                image = await async_get_image(hass, camera_entity)

                if image is None:
                    raise ServiceValidationError(
                        f"Failed to get image from camera {camera_entity}",
                        translation_domain=DOMAIN,
                        translation_key="image_fetch_failed",
                    )

                # Analyze image
                _LOGGER.debug(
                    "Analyzing image with %s for object: %s",
                    ai_service,
                    detection_object,
                )
                result = await ai_client.analyze_image(
                    image.content, detection_object
                )

                # Format response
                image_time = dt_util.utcnow().isoformat()
                
                response = {
                    ATTR_OBJECT_PRESENT: result.get("object_present", False),
                    ATTR_OBJECT_COUNT: result.get("object_count", 0),
                    ATTR_CONFIDENCE: round(result.get("confidence", 0.0), 2),
                    ATTR_IMAGE_TIME: image_time,
                    ATTR_DETECTION_OBJECT: detection_object,
                }

                # Add detected objects if present
                if result.get("detected_objects"):
                    response[ATTR_DETECTED_OBJECTS] = [
                        {
                            "confidence": round(obj.get("confidence", 0), 2),
                            "x": obj.get("x"),
                            "y": obj.get("y"),
                            "width": obj.get("width"),
                            "height": obj.get("height"),
                        }
                        for obj in result["detected_objects"]
                    ]
                else:
                    response[ATTR_DETECTED_OBJECTS] = []

                # Add request_id if available
                if result.get("request_id"):
                    response[ATTR_REQUEST_ID] = result["request_id"]

                _LOGGER.debug("Detection service response: %s", response)
                return response

            except ValueError as err:
                raise ServiceValidationError(
                    f"AI client error: {err}",
                    translation_domain=DOMAIN,
                    translation_key="ai_client_error",
                ) from err
            except Exception as err:
                _LOGGER.error("Error in detect_object service: %s", err)
                raise ServiceValidationError(
                    f"Detection failed: {err}",
                    translation_domain=DOMAIN,
                    translation_key="detection_failed",
                ) from err

        hass.services.async_register(
            DOMAIN,
            SERVICE_DETECT_OBJECT,
            handle_detect_object,
            schema=SERVICE_DETECT_OBJECT_SCHEMA,
            supports_response=SupportsResponse.ONLY,
        )
        _LOGGER.info("Registered service: %s.%s", DOMAIN, SERVICE_DETECT_OBJECT)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Only unload platforms if binary sensor was enabled
    disable_binary_sensor = entry.data.get(CONF_DISABLE_BINARY_SENSOR, False)
    
    if not disable_binary_sensor:
        unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    else:
        # Action-only mode: no platforms to unload
        unload_ok = True
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        
        # Unregister service if no more config entries exist
        if not hass.data[DOMAIN]:
            hass.services.async_remove(DOMAIN, SERVICE_DETECT_OBJECT)
            _LOGGER.info("Unregistered service: %s.%s", DOMAIN, SERVICE_DETECT_OBJECT)

    return unload_ok
