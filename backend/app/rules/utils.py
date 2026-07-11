from dataclasses import dataclass, field

from app.detection.base import BoundingBox
from app.tracking.base import TrackedDetection

VEHICLE_CLASSES = frozenset({"car", "motorcycle", "bus", "truck", "bicycle"})
PERSON_CLASS = "person"


def bbox_center(bbox: BoundingBox) -> tuple[float, float]:
    return (bbox.x + bbox.width / 2, bbox.y + bbox.height / 2)


def distance(a: tuple[float, float], b: tuple[float, float]) -> float:
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


def normalized_center(
    detection: TrackedDetection,
    frame_width: int,
    frame_height: int,
) -> tuple[float, float]:
    cx, cy = bbox_center(detection.bbox)
    return (cx / frame_width, cy / frame_height)


def in_normalized_zone(
    detection: TrackedDetection,
    zone: tuple[float, float, float, float],
    frame_width: int,
    frame_height: int,
) -> bool:
    nx, ny = normalized_center(detection, frame_width, frame_height)
    x1, y1, x2, y2 = zone
    return x1 <= nx <= x2 and y1 <= ny <= y2


def filter_class(
    detections: list[TrackedDetection],
    classes: frozenset[str],
) -> list[TrackedDetection]:
    return [item for item in detections if item.object_class in classes]


def filter_persons(detections: list[TrackedDetection]) -> list[TrackedDetection]:
    return filter_class(detections, frozenset({PERSON_CLASS}))


def filter_vehicles(detections: list[TrackedDetection]) -> list[TrackedDetection]:
    return filter_class(detections, VEHICLE_CLASSES)


@dataclass(slots=True)
class CooldownState:
    cooldown_seconds: float
    _last_event_at: dict[str, object] = field(default_factory=dict)

    def ready(self, key: str, occurred_at: object) -> bool:
        from datetime import datetime

        if not isinstance(occurred_at, datetime):
            return True
        last = self._last_event_at.get(key)
        if last is None or not isinstance(last, datetime):
            return True
        return (occurred_at - last).total_seconds() >= self.cooldown_seconds

    def mark(self, key: str, occurred_at: object) -> None:
        self._last_event_at[key] = occurred_at

    def reset(self) -> None:
        self._last_event_at.clear()
