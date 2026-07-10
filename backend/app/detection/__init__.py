"""Computer vision detection layer (FASE 5)."""

from app.detection.base import BoundingBox, ObjectDetector, RawDetection
from app.detection.factory import create_detector
from app.detection.null import NullDetector
from app.detection.pipeline import DetectionPipeline

__all__ = [
    "BoundingBox",
    "DetectionPipeline",
    "NullDetector",
    "ObjectDetector",
    "RawDetection",
    "create_detector",
]
