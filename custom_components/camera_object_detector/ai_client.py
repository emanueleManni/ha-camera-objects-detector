"""AI Service clients for image analysis."""

from __future__ import annotations

from abc import ABC, abstractmethod
import asyncio
import io
import logging
from typing import Any

import moondream as md
from PIL import Image

# Import constants with fallback for standalone usage
try:
    from .const import AI_SERVICE_LOCAL, AI_SERVICE_MOONDREAM
except ImportError:
    # Fallback for standalone testing
    AI_SERVICE_LOCAL = "local"
    AI_SERVICE_MOONDREAM = "moondream"

_LOGGER = logging.getLogger(__name__)


class AIServiceClient(ABC):
    """Abstract base class for AI service clients."""

    @abstractmethod
    async def analyze_image(
        self, image_data: bytes, detection_object: str
    ) -> dict[str, Any]:
        """Analyze image and return detection results."""


class MoondreamAIClient(AIServiceClient):
    """Client for Moondream AI service using SDK.
    
    NOTE: Moondream API does NOT return confidence scores.
    Detection logic: if object appears in response list, it's detected.
    Empty list = nothing detected.
    """

    def __init__(self, api_key: str, timeout: int = 30) -> None:
        """Initialize the Moondream AI client."""
        self.api_key = api_key
        self.timeout = timeout
        self.model = md.vl(api_key=api_key)
        _LOGGER.info("Moondream SDK initialized successfully")

    async def analyze_image(
        self, image_data: bytes, detection_object: str
    ) -> dict[str, Any]:
        """Analyze image using Moondream AI object detection.

        Args:
            image_data: Raw image bytes
            detection_object: Object to detect (e.g., "drying_rack", "person", etc.)

        Returns:
            dict with keys:
                - object_present: bool (True if at least one object detected)
                - object_count: int (number of objects detected)
                - detected_objects: list of objects with confidence and bbox
                - request_id: str (empty, SDK doesn't provide it)
                - confidence: float (1.0 if objects found, else 0.0)
        """
        _LOGGER.debug("Detecting '%s' with Moondream SDK", detection_object)
        
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            _LOGGER.debug("Image loaded: format=%s, size=%s, mode=%s", 
                         image.format, image.size, image.mode)
            
            # Run detection in executor to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, self.model.detect, image, detection_object
            )
            
            _LOGGER.debug("SDK response: %s", result)
            
            # Parse the response from Moondream SDK
            # Format: {"objects": [{"x_min": float, "y_min": float, "x_max": float, "y_max": float}]}
            # - Objects are in normalized coordinates (0-1)
            # - NO confidence field - if object is in the list, it's detected
            # - NO request_id field
            # - Empty list means nothing detected
            raw_objects = result.get("objects", [])
            request_id = ""  # SDK doesn't return request_id
            
            # Convert from SDK format (x_min, y_min, x_max, y_max) to our format
            # Calculate pixel coordinates and add confidence=1.0 for all detected objects
            detected_objects = []
            for obj in raw_objects:
                # Get normalized coordinates
                x_min = obj.get("x_min", 0)
                y_min = obj.get("y_min", 0)
                x_max = obj.get("x_max", 0)
                y_max = obj.get("y_max", 0)
                
                # Convert to pixel coordinates
                img_width, img_height = image.size
                x = int(x_min * img_width)
                y = int(y_min * img_height)
                width = int((x_max - x_min) * img_width)
                height = int((y_max - y_min) * img_height)
                
                # Add to detected objects with confidence=1.0
                # (SDK doesn't provide confidence, but if it's in the list, it's detected)
                detected_objects.append({
                    "confidence": 1.0,
                    "x": x,
                    "y": y,
                    "width": width,
                    "height": height,
                    "x_min": x_min,  # Keep normalized coords for reference
                    "y_min": y_min,
                    "x_max": x_max,
                    "y_max": y_max,
                })
            
            # Calculate results
            object_count = len(detected_objects)
            object_present = object_count > 0
            confidence = 1.0 if object_count > 0 else 0.0
            
            _LOGGER.info(
                "Moondream SDK detection completed: %d objects detected",
                object_count
            )
            
            return {
                "object_present": object_present,
                "object_count": object_count,
                "detected_objects": detected_objects,
                "request_id": request_id,
                "confidence": confidence,
            }
            
        except Exception as err:
            _LOGGER.error("Error with Moondream SDK: %s", err)
            raise


class LocalAIClient(AIServiceClient):
    """Client for local AI models (placeholder for future implementation)."""

    async def analyze_image(
        self, image_data: bytes, detection_object: str
    ) -> dict[str, Any]:
        """Analyze image using local AI model."""
        _LOGGER.warning("Local AI is not yet implemented")
        return {
            "object_present": False,
            "object_count": 0,
            "detected_objects": [],
            "request_id": "",
            "confidence": 0.0,
        }


def get_ai_client(service: str, api_key: str | None = None) -> AIServiceClient:
    """Factory function to get the appropriate AI client."""
    if service == AI_SERVICE_MOONDREAM:
        if not api_key:
            raise ValueError("API key is required for Moondream AI")
        return MoondreamAIClient(api_key)
    if service == AI_SERVICE_LOCAL:
        return LocalAIClient()

    raise ValueError(f"Unknown AI service: {service}")
