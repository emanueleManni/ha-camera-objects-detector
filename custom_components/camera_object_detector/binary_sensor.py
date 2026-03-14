"""Binary sensor platform for Camera Object Detector."""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.components.camera import async_get_image
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.util import dt as dt_util

from .ai_client import get_ai_client, AIServiceClient
from .const import (
    ATTR_AI_SERVICE,
    ATTR_CONFIDENCE,
    ATTR_DETECTED_OBJECTS,
    ATTR_DETECTION_OBJECT,
    ATTR_LAST_IMAGE_TIME,
    ATTR_OBJECT_COUNT,
    ATTR_REQUEST_ID,
    CONF_AI_SERVICE,
    CONF_CAMERA_ENTITY,
    CONF_DETECTION_OBJECT,
    CONF_SCAN_INTERVAL,
    DEFAULT_DETECTION_OBJECT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Camera Object Detector binary sensor."""
    camera_entity = config_entry.data[CONF_CAMERA_ENTITY]
    ai_service = config_entry.data[CONF_AI_SERVICE]
    api_key = config_entry.data.get(CONF_API_KEY)
    scan_interval = config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    detection_object = config_entry.data.get(CONF_DETECTION_OBJECT, DEFAULT_DETECTION_OBJECT)

    # Create AI client
    try:
        ai_client = get_ai_client(ai_service, api_key)
    except ValueError as err:
        _LOGGER.error("Failed to create AI client: %s", err)
        return

    # Create coordinator
    coordinator = CameraObjectDetectorCoordinator(
        hass,
        camera_entity,
        ai_client,
        ai_service,
        detection_object,
        scan_interval,
    )

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    # Add entity
    async_add_entities([CameraObjectDetectorBinarySensor(coordinator, config_entry)])


class CameraObjectDetectorCoordinator(DataUpdateCoordinator):
    """Coordinator to manage data updates."""

    def __init__(
        self,
        hass: HomeAssistant,
        camera_entity: str,
        ai_client: AIServiceClient,
        ai_service: str,
        detection_object: str,
        scan_interval: int,
    ) -> None:
        """Initialize the coordinator."""
        self.camera_entity = camera_entity
        self.ai_client = ai_client
        self.ai_service = ai_service
        self.detection_object = detection_object

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{camera_entity}",
            update_interval=timedelta(seconds=scan_interval),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from camera and analyze with AI."""
        try:
            # Get image from camera
            _LOGGER.debug("Fetching image from camera: %s", self.camera_entity)
            
            image = await async_get_image(self.hass, self.camera_entity)
            
            if image is None:
                raise UpdateFailed(f"Failed to get image from camera {self.camera_entity}")
            
            _LOGGER.debug(
                "Analyzing image with %s for object: %s",
                self.ai_service,
                self.detection_object,
            )
            
            result = await self.ai_client.analyze_image(image.content, self.detection_object)
            
            # Add timestamp and metadata
            result[ATTR_LAST_IMAGE_TIME] = dt_util.utcnow().isoformat()
            result[ATTR_AI_SERVICE] = self.ai_service
            result[ATTR_DETECTION_OBJECT] = self.detection_object
            
            _LOGGER.debug("Analysis result: %s", result)
            
            return result

        except Exception as err:
            _LOGGER.error("Error updating camera object detector: %s", err)
            raise UpdateFailed(f"Error updating camera object detector: {err}") from err


class CameraObjectDetectorBinarySensor(
    CoordinatorEntity[CameraObjectDetectorCoordinator], BinarySensorEntity
):
    """Binary sensor for object detection."""

    _attr_has_entity_name = True
    _attr_device_class = BinarySensorDeviceClass.OCCUPANCY

    def __init__(
        self,
        coordinator: CameraObjectDetectorCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        
        self._camera_entity = config_entry.data[CONF_CAMERA_ENTITY]
        detection_object = config_entry.data.get(CONF_DETECTION_OBJECT, DEFAULT_DETECTION_OBJECT)
        
        self._attr_unique_id = f"{config_entry.entry_id}_{detection_object}"
        self._attr_name = f"{detection_object.replace('_', ' ').title()} Detection"

    @property
    def is_on(self) -> bool | None:
        """Return true if object is detected."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("object_present", False)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        if self.coordinator.data is None:
            return {}

        attributes = {
            "camera_entity": self._camera_entity,
        }

        # Add object count
        if ATTR_OBJECT_COUNT in self.coordinator.data:
            attributes[ATTR_OBJECT_COUNT] = self.coordinator.data[ATTR_OBJECT_COUNT]

        # Add confidence if available
        if ATTR_CONFIDENCE in self.coordinator.data:
            confidence = self.coordinator.data[ATTR_CONFIDENCE]
            attributes[ATTR_CONFIDENCE] = round(confidence, 2)

        # Add detected objects list
        if ATTR_DETECTED_OBJECTS in self.coordinator.data:
            detected = self.coordinator.data[ATTR_DETECTED_OBJECTS]
            # Format for display
            if detected:
                attributes[ATTR_DETECTED_OBJECTS] = [
                    {
                        "confidence": round(obj.get("confidence", 0), 2),
                        "x": obj.get("x"),
                        "y": obj.get("y"),
                        "width": obj.get("width"),
                        "height": obj.get("height"),
                    }
                    for obj in detected
                ]
            else:
                attributes[ATTR_DETECTED_OBJECTS] = []

        # Add request ID
        if ATTR_REQUEST_ID in self.coordinator.data:
            attributes[ATTR_REQUEST_ID] = self.coordinator.data[ATTR_REQUEST_ID]

        # Add last image time
        if ATTR_LAST_IMAGE_TIME in self.coordinator.data:
            attributes[ATTR_LAST_IMAGE_TIME] = self.coordinator.data[ATTR_LAST_IMAGE_TIME]

        # Add AI service
        if ATTR_AI_SERVICE in self.coordinator.data:
            attributes[ATTR_AI_SERVICE] = self.coordinator.data[ATTR_AI_SERVICE]

        # Add detection object
        if ATTR_DETECTION_OBJECT in self.coordinator.data:
            attributes[ATTR_DETECTION_OBJECT] = self.coordinator.data[ATTR_DETECTION_OBJECT]

        return attributes

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success

    @property
    def icon(self) -> str:
        """Return the icon to use in the frontend."""
        if self.is_on:
            return "mdi:eye-check"
        return "mdi:eye-off"
