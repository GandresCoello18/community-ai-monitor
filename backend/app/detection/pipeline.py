from dataclasses import dataclass

import numpy as np

from app.detection.base import ObjectDetector
from app.tracking.base import ObjectTracker, TrackedDetection


@dataclass(slots=True)
class DetectionPipeline:
    """Runs detection then tracking for a single camera.

    Pure computer-vision step: no database access and no business rules.
    This method is CPU-bound (model inference) and should be executed off the
    event loop (e.g. via `asyncio.to_thread`).
    """

    detector: ObjectDetector
    tracker: ObjectTracker

    def process(self, image: np.ndarray) -> list[TrackedDetection]:
        raw_detections = self.detector.detect(image)
        return self.tracker.update(raw_detections)
