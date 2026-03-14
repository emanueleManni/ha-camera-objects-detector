"""AI Service clients for image analysis."""
from __future__ import annotations

import asyncio
import io
import logging
from abc import ABC, abstractmethod
from typing import Any

try:
    import moondream as md
    from PIL import Image
except ImportError:
    md = None
    Image = None

from .const import (
    AI_SERVICE_LOCAL,
    AI_SERVICE_MOONDREAM,
)

_LOGGER = logging.getLogger(__name__)


class AIServiceClient(ABC):
    """Abstract base class for AI service clients."""

    @abstractmethod
    async def analyze_image(self, image_data: bytes, detection_object: str) -> dict[str, Any]:
        """Analyze image and return detection results."""


class MoondreamAIClient(AIServiceClient):
    """Client for Moondream AI service using object detection."""

    def __init__(self, api_key: str, timeout: int = 30) -> None:
        """Initialize the Moondream AI client."""
        if md is None:
            raise ImportError(
                "moondream package not installed. "
                "Install it with: pip install moondream"
            )
        
        self.api_key = api_key
        self.timeout = timeout
        self._model = None

    def _get_model(self):
        """Get or create moondream model instance."""
        if self._model is None:
            self._model = md.vl(api_key=self.api_key)
        return self._model

    async def analyze_image(self, image_data: bytes, detection_object: str) -> dict[str, Any]:
        """
        Analyze image using Moondream AI object detection.
        
        Args:
            image_data: Raw image bytes
            detection_object: Object to detect (e.g., "drying_rack", "person", etc.)
        
        Returns:
            dict with keys:
                - object_present: bool (True if at least one object detected)
                - object_count: int (number of objects detected)
                - detected_objects: list of objects with confidence and bbox
                - request_id: str (Moondream request ID)
                - confidence: float (max confidence if objects found, else 0)
        """
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # Get model
            model = self._get_model()
            
            _LOGGER.debug("Detecting '%s' with Moondream AI", detection_object)
            
            # Run detection in executor to avoid blocking
            loop = asyncio.get_event_loop()
            result = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: model.detect(image, detection_object)
                ),
                timeout=self.timeout
            )
            
            _LOGGER.debug("Received response from Moondream AI: %s", result)
            
            # Parse the response
            objects = result.get("objects", [])
            request_id = result.get("request_id", "")
            
            # Calculate results
            object_count = len(objects)
            object_present = object_count > 0
            
            # Get max confidence if objects found
            confidence = 0.0
            if objects:
                confidences = [obj.get("confidence", 0) for obj in objects]
                confidence = max(confidences) if confidences else 0.0
            
            return {
                "object_present": object_present,
                "object_count": object_count,
                "detected_objects": objects,
                "request_id": request_id,
                "confidence": confidence,
            }

        except asyncio.TimeoutError:
            _LOGGER.error("Timeout communicating with Moondream AI")
            raise
        except Exception as err:
            _LOGGER.error("Unexpected error analyzing image: %s", err)
            raise


class LocalAIClient(AIServiceClient):
    """Client for local AI models (placeholder for future implementation)."""

    async def analyze_image(self, image_data: bytes, detection_object: str) -> dict[str, Any]:
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
    elif service == AI_SERVICE_LOCAL:
        return LocalAIClient()
    else:
        raise ValueError(f"Unknown AI service: {service}")
