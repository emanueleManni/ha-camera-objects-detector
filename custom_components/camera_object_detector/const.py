"""Constants for the Camera Object Detector integration."""

DOMAIN = "camera_object_detector"

# Services
SERVICE_DETECT_OBJECT = "detect_object"

# Configuration
CONF_AI_SERVICE = "ai_service"
CONF_API_KEY = "api_key"
CONF_CAMERA_ENTITY = "camera_entity"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_DETECTION_OBJECT = "detection_object"  # NEW: oggetto da rilevare
CONF_DISABLE_BINARY_SENSOR = "disable_binary_sensor"  # NEW: disabilita binary sensor

# AI Services
AI_SERVICE_MOONDREAM = "moondream"
AI_SERVICE_LOCAL = "local"

# Defaults
DEFAULT_SCAN_INTERVAL = 300  # 5 minutes
DEFAULT_AI_SERVICE = AI_SERVICE_MOONDREAM
DEFAULT_DETECTION_OBJECT = "drying_rack"  # NEW: oggetto predefinito

# Moondream API
# Using object detection with model.detect() instead of VQA
MOONDREAM_SUPPORTED_OBJECTS = [
    "drying_rack",
    "person",
    "car",
    "bicycle",
    "dog",
    "cat",
    "umbrella",
    "chair",
    "table",
    "plant",
    "box",
    "bag",
    "bottle",
]  # Lista oggetti comuni, ma moondream supporta qualsiasi stringa

# Minimum confidence threshold for object detection
# Objects below this threshold are considered as "not detected"
# Moondream API returns objects with confidence 0.0 when nothing is found
MIN_CONFIDENCE_THRESHOLD = 0.5  # 50%

# Attributes
ATTR_CONFIDENCE = "confidence"
ATTR_DETECTED_OBJECTS = "detected_objects"  # NEW: lista oggetti rilevati
ATTR_OBJECT_COUNT = "object_count"  # NEW: numero di oggetti
ATTR_REQUEST_ID = "request_id"  # NEW: ID richiesta Moondream
ATTR_LAST_IMAGE_TIME = "last_image_time"
ATTR_AI_SERVICE = "ai_service"
ATTR_DETECTION_OBJECT = "detection_object"  # NEW: oggetto cercato

# Service fields
ATTR_OBJECT_PRESENT = "object_present"
ATTR_IMAGE_TIME = "image_time"
