from dataclasses import dataclass
from typing import Protocol

import numpy as np


@dataclass(frozen=True, slots=True)
class BoundingBox:
    """Axis-aligned bounding box in pixel coordinates."""

    x: int
    y: int
    width: int
    height: int

    def as_dict(self) -> dict[str, int]:
        return {"x": self.x, "y": self.y, "width": self.width, "height": self.height}


@dataclass(frozen=True, slots=True)
class RawDetection:
    """A single object detected in one frame, before tracking."""

    object_class: str
    confidence: float
    bbox: BoundingBox


class ObjectDetector(Protocol):
    """Adapter interface for object detection models.

    Implementations must be swappable (YOLO, remote model, no-op) without
    changing the detection pipeline.
    """

    @property
    def model_name(self) -> str: ...

    def detect(self, image: np.ndarray) -> list[RawDetection]: ...
