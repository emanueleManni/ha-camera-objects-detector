# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.3] - 2026-03-21

### Changed

- Enhanced AI service configuration logging for better debugging
- Improved error messages during integration setup for clearer troubleshooting

## [0.2.2] - 2026-03-20

### Added

- **Action-only mode**: Option to disable binary sensor and use only on-demand detection
- Configurable detection object selection via UI
- `disable_binary_sensor` configuration option for cost-saving scenarios

### Changed

- Detection object is now fully configurable instead of fixed to "drying_rack"
- Config flow updated to support flexible object detection

## [0.2.1] - 2026-03-18

### Added

- **New service**: `detect_object` for on-demand object detection
- Service supports custom camera, object, AI service, and API key parameters
- Service returns detailed response with detected objects and bounding boxes
- New attributes: `detected_objects`, `object_count`, `request_id`
- Support for object detection with bounding box coordinates (x, y, width, height)
- List of supported objects: drying_rack, person, car, bicycle, dog, cat, umbrella, chair, table, plant, box, bag, bottle
- Minimum confidence threshold (MIN_CONFIDENCE_THRESHOLD = 0.5)

### Changed

- Binary sensor now includes object count and detailed detection information
- Enhanced attributes with bounding box data for detected objects

## [0.2.0] - 2026-03-17

### Changed

- **BREAKING**: Migrated from Moondream SDK to HTTP API
- Removed package dependency on `moondream` from requirements
- Refactored AI client to use direct HTTP API calls
- Improved error handling and logging in AI client

### Technical

- Switched from SDK-based detection to HTTP API endpoints
- Better control over API requests and responses
- Reduced external dependencies

## [0.1.8] - 2026-03-14

### Added

- Initial release
- Binary sensor for clothes drying rack detection
- Integration with Moondream AI for image analysis
- Configuration flow with UI
- Support for Home Assistant cameras
- Customizable scan interval (30 seconds to 1 hour)
- Attributes: confidence, explanation, timestamp, AI service
- Italian and English translations
- Custom icons (hanger on/off)
- Options flow for reconfiguration
- Detailed documentation and examples

### Features

- Automatic detection using AI vision models
- Cloud-based analysis via Moondream AI
- Ready for future local AI implementation
- Easy integration with automations
- Low resource impact (configurable polling)

## [Unreleased]

### Planned

- Local AI model support (YOLO, TensorFlow)
- Multi-object detection support
- Historical tracking and statistics
- Image snapshot storage of detections
- Custom training capability
- Multiple camera support per integration
- Detection zones (exclude parts of image)
- Confidence threshold configuration
- Integration with weather services
- Mobile app notifications templates
