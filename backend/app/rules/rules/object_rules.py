from dataclasses import dataclass, field
from datetime import datetime

from app.detection.base import BoundingBox
from app.rules.base_rule import EventCandidate, MetricSample, RuleContext
from app.rules.config import RulesConfig
from app.rules.utils import bbox_center, distance


@dataclass(slots=True)
class _StationaryTrack:
    first_seen: datetime
    stationary_since: datetime
    last_center: tuple[float, float]
    object_class: str
    event_emitted: bool = False


@dataclass(slots=True)
class AbandonedObjectRule:
    duration_seconds: float
    movement_threshold: float
    target_classes: frozenset[str]
    _tracks: dict[int, _StationaryTrack] = field(default_factory=dict, init=False)

    @property
    def rule_name(self) -> str:
        return "abandoned_object"

    @property
    def is_placeholder(self) -> bool:
        return False

    def evaluate(self, context: RuleContext) -> list[EventCandidate]:
        active: set[int] = set()
        candidates: list[EventCandidate] = []

        for detection in context.tracked_detections:
            if detection.object_class not in self.target_classes:
                continue
            if detection.object_class == "person":
                continue

            center = bbox_center(detection.bbox)
            active.add(detection.track_id)
            track = self._tracks.get(detection.track_id)

            if track is None:
                self._tracks[detection.track_id] = _StationaryTrack(
                    first_seen=context.occurred_at,
                    stationary_since=context.occurred_at,
                    last_center=center,
                    object_class=detection.object_class,
                )
                continue

            if distance(center, track.last_center) > self.movement_threshold:
                track.stationary_since = context.occurred_at
                track.last_center = center
                track.event_emitted = False

            stationary = (
                context.occurred_at - track.stationary_since
            ).total_seconds()
            if stationary < self.duration_seconds or track.event_emitted:
                continue

            track.event_emitted = True
            candidates.append(
                EventCandidate(
                    event_type="abandoned_object",
                    severity="medium",
                    occurred_at=context.occurred_at,
                    started_at=track.stationary_since,
                    metadata={
                        "duration_seconds": int(stationary),
                        "object_class": detection.object_class,
                        "track_id": detection.track_id,
                    },
                    rule_name=self.rule_name,
                )
            )

        for track_id in list(self._tracks):
            if track_id not in active:
                del self._tracks[track_id]
        return candidates

    def collect_metrics(self, context: RuleContext) -> list[MetricSample]:
        return []

    def reset(self) -> None:
        self._tracks.clear()


def build_object_rules(config: RulesConfig) -> list[object]:
    if not config.abandoned_object_enabled:
        return []
    return [
        AbandonedObjectRule(
            duration_seconds=config.abandoned_object_seconds,
            movement_threshold=config.abandoned_object_movement_threshold,
            target_classes=config.abandoned_object_classes,
        )
    ]
