from dataclasses import dataclass
from typing import Protocol

from app.detection.base import BoundingBox, RawDetection


@dataclass(frozen=True, slots=True)
class TrackedDetection:
    """A detection associated with a temporal track identity.

    Track IDs are temporal and technical only (privacy by design): they are
    used to avoid counting the same object twice across frames and are not a
    persistent identity for any individual.
    """

    track_id: int
    object_class: str
    confidence: float
    bbox: BoundingBox


class ObjectTracker(Protocol):
    """Adapter interface for temporal object trackers.

    Implementations must be swappable (IoU tracker, ByteTrack, BoT-SORT)
    without changing the detection pipeline.
    """

    def update(self, detections: list[RawDetection]) -> list[TrackedDetection]: ...
