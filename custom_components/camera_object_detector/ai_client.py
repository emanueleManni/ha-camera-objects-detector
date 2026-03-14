"""AI Service clients for image analysis."""
from __future__ import annotations

import asyncio
import base64
import io
import logging
from abc import ABC, abstractmethod
from typing import Any

import aiohttp

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
    """Client for Moondream AI service using HTTP API."""

    API_URL = "https://api.moondream.ai/v1/detect"

    def __init__(self, api_key: str, timeout: int = 30) -> None:
        """Initialize the Moondream AI client."""
        self.api_key = api_key
        self.timeout = timeout

    async def analyze_image(self, image_data: bytes, detection_object: str) -> dict[str, Any]:
        """
        Analyze image using Moondream AI object detection via HTTP API.
        
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
            # Encode image to base64
            image_b64 = base64.b64encode(image_data).decode('utf-8')
            
            _LOGGER.debug("Detecting '%s' with Moondream AI", detection_object)
            
            # Prepare request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            
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
                            error_text
                        )
                        raise Exception(f"API error: {response.status}")
                    
                    result = await response.json()
            
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
