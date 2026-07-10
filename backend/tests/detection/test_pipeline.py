import numpy as np

from app.core.config import Settings
from app.detection.base import BoundingBox, RawDetection
from app.detection.factory import create_detector
from app.detection.null import NullDetector
from app.detection.pipeline import DetectionPipeline
from app.tracking.iou_tracker import IoUTracker


class FakeDetector:
    model_name = "fake"

    def __init__(self, detections: list[RawDetection]) -> None:
        self._detections = detections

    def detect(self, image: np.ndarray) -> list[RawDetection]:
        return self._detections


def test_pipeline_runs_detection_then_tracking() -> None:
    detections = [
        RawDetection("person", 0.9, BoundingBox(10, 10, 40, 80)),
        RawDetection("car", 0.8, BoundingBox(200, 50, 90, 60)),
    ]
    pipeline = DetectionPipeline(
        detector=FakeDetector(detections),
        tracker=IoUTracker(),
    )
    image = np.zeros((480, 640, 3), dtype=np.uint8)

    tracked = pipeline.process(image)

    assert len(tracked) == 2
    assert {item.object_class for item in tracked} == {"person", "car"}
    assert all(item.track_id > 0 for item in tracked)


def test_pipeline_with_no_detections_returns_empty() -> None:
    pipeline = DetectionPipeline(detector=NullDetector(), tracker=IoUTracker())
    image = np.zeros((480, 640, 3), dtype=np.uint8)

    assert pipeline.process(image) == []


def test_factory_returns_null_detector_when_disabled() -> None:
    settings = Settings(app_env="testing", detection_enabled=False)

    detector = create_detector(settings)

    assert isinstance(detector, NullDetector)
