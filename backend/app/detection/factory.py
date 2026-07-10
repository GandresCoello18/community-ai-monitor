import logging

from app.core.config import Settings
from app.detection.base import ObjectDetector
from app.detection.null import NullDetector

logger = logging.getLogger(__name__)


def create_detector(settings: Settings) -> ObjectDetector:
    """Build the configured detector, degrading gracefully.

    Returns a `NullDetector` when detection is disabled, when the optional
    `ultralytics` dependency is missing, or when the model fails to load. This
    keeps capture running even in lightweight environments (e.g. the Docker
    image without ML dependencies).
    """
    if not settings.detection_enabled:
        logger.info("Detection disabled by configuration; using NullDetector")
        return NullDetector()

    allowed = settings.detection_class_set

    try:
        from app.detection.yolo import YOLODetector  # noqa: PLC0415

        return YOLODetector(
            settings.detection_model,
            confidence=settings.detection_confidence,
            allowed_classes=allowed or None,
            device=settings.detection_device,
        )
    except ImportError:
        logger.warning(
            "ultralytics is not installed; detection disabled. "
            "Install backend/requirements-ml.txt to enable YOLO.",
        )
        return NullDetector()
    except Exception:
        logger.exception("Failed to load YOLO model; using NullDetector")
        return NullDetector()
