import numpy as np

from app.detection.base import RawDetection


class NullDetector:
    """No-op detector used when detection is disabled or ML deps are missing.

    Keeps the pipeline functional (capture keeps running) without producing
    detections, so the system degrades gracefully instead of crashing.
    """

    model_name = "null"

    def detect(self, image: np.ndarray) -> list[RawDetection]:
        return []
