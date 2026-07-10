from dataclasses import dataclass, field
from datetime import datetime

from app.detection.base import BoundingBox
from app.events.base import EventCandidate, RuleContext


def _bbox_center(bbox: BoundingBox) -> tuple[float, float]:
    return (bbox.x + bbox.width / 2, bbox.y + bbox.height / 2)


def _distance(a: tuple[float, float], b: tuple[float, float]) -> float:
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


@dataclass(slots=True)
class _StationaryTrack:
    first_seen: datetime
    stationary_since: datetime
    last_center: tuple[float, float]
    object_class: str
    event_emitted: bool = False


@dataclass(slots=True)
class AbandonedObjectRule:
    """Emit when a non-person object stays still longer than a duration."""

    duration_seconds: float
    movement_threshold: float
    target_classes: frozenset[str]
    _tracks: dict[int, _StationaryTrack] = field(default_factory=dict, init=False)

    @property
    def rule_name(self) -> str:
        return "abandoned_object"

    def evaluate(self, context: RuleContext) -> list[EventCandidate]:
        active_track_ids: set[int] = set()
        candidates: list[EventCandidate] = []

        for detection in context.tracked_detections:
            if detection.object_class not in self.target_classes:
                continue
            if detection.object_class == "person":
                continue

            center = _bbox_center(detection.bbox)
            active_track_ids.add(detection.track_id)
            track = self._tracks.get(detection.track_id)

            if track is None:
                self._tracks[detection.track_id] = _StationaryTrack(
                    first_seen=context.occurred_at,
                    stationary_since=context.occurred_at,
                    last_center=center,
                    object_class=detection.object_class,
                )
                continue

            if _distance(center, track.last_center) > self.movement_threshold:
                track.stationary_since = context.occurred_at
                track.last_center = center
                track.event_emitted = False

            stationary_seconds = (
                context.occurred_at - track.stationary_since
            ).total_seconds()
            if stationary_seconds < self.duration_seconds or track.event_emitted:
                continue

            track.event_emitted = True
            candidates.append(
                EventCandidate(
                    event_type="abandoned_object",
                    severity="medium",
                    occurred_at=context.occurred_at,
                    started_at=track.stationary_since,
                    metadata={
                        "duration_seconds": int(stationary_seconds),
                        "object_class": detection.object_class,
                        "track_id": detection.track_id,
                    },
                )
            )

        for track_id in list(self._tracks.keys()):
            if track_id not in active_track_ids:
                del self._tracks[track_id]

        return candidates

    def reset(self) -> None:
        self._tracks.clear()
