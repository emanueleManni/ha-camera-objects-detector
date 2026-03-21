"""AI Service clients for image analysis."""

from __future__ import annotations

from abc import ABC, abstractmethod
import base64
import logging
from typing import Any

import aiohttp

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
    """Client for Moondream AI service using HTTP API.
    
    NOTE: Moondream API does NOT return confidence scores.
    Detection logic: if object appears in response list, it's detected.
    Empty list = nothing detected.
    """

    API_URL = "https://api.moondream.ai/v1/detect"

    def __init__(self, api_key: str, timeout: int = 30) -> None:
        """Initialize the Moondream AI client."""
        self.api_key = api_key
        self.timeout = timeout
        _LOGGER.info("Moondream HTTP API client initialized")

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
                - detected_objects: list of objects with bounding boxes
                - request_id: str (empty, API doesn't provide it)
                - confidence: float (1.0 if objects found, else 0.0)
        """
        _LOGGER.debug("Detecting '%s' with Moondream HTTP API", detection_object)
        
        try:
            # Encode image to base64
            image_b64 = base64.b64encode(image_data).decode("utf-8")

            # Prepare request headers (using X-Moondream-Auth as per documentation)
            headers = {
                "X-Moondream-Auth": self.api_key,
                "Content-Type": "application/json",
            }

            # Prepare request payload
            payload = {
                "image_url": f"data:image/jpeg;base64,{image_b64}",
                "object": detection_object,
            }

            # Make API request
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    self.API_URL,
                    json=payload,
                    headers=headers,
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        _LOGGER.error(
                            "Moondream API error (status %s): %s",
                            response.status,
                            error_text,
                        )
                        raise Exception(f"API error: {response.status} - {error_text}")

                    result = await response.json()

            _LOGGER.debug("API response: %s", result)

            # Parse the response from Moondream API
            # Format: {"objects": [{"x_min": float, "y_min": float, "x_max": float, "y_max": float}]}
            # - Objects are in normalized coordinates (0-1)
            # - NO confidence field - if object is in the list, it's detected
            # - NO request_id field  
            # - Empty list means nothing detected
            raw_objects = result.get("objects", [])
            
            # Convert from API format to our format
            # Note: We don't have image dimensions, so we keep normalized coordinates
            # Home Assistant can scale them if needed
            detected_objects = []
            for obj in raw_objects:
                # Get normalized coordinates
                x_min = obj.get("x_min", 0)
                y_min = obj.get("y_min", 0)
                x_max = obj.get("x_max", 0)
                y_max = obj.get("y_max", 0)
                
                # Store with both normalized and relative coordinates
                detected_objects.append({
                    "confidence": 1.0,  # API doesn't provide confidence
                    "x_min": x_min,
                    "y_min": y_min,
                    "x_max": x_max,
                    "y_max": y_max,
                    # Calculate center and size in normalized coords
                    "x": (x_min + x_max) / 2,
                    "y": (y_min + y_max) / 2,
                    "width": x_max - x_min,
                    "height": y_max - y_min,
                })
            
            # Calculate results
            object_count = len(detected_objects)
            object_present = object_count > 0
            confidence = 1.0 if object_count > 0 else 0.0
            
            _LOGGER.info(
                "Moondream API detection completed: %d objects detected",
                object_count
            )

            return {
                "object_present": object_present,
                "object_count": object_count,
                "detected_objects": detected_objects,
                "request_id": "",  # API doesn't provide request_id
                "confidence": confidence,
            }
            
        except aiohttp.ClientError as err:
            _LOGGER.error("HTTP error communicating with Moondream API: %s", err)
            raise
        except Exception as err:
            _LOGGER.error("Unexpected error analyzing image: %s", err)
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
