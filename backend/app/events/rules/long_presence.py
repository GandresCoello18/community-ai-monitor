from dataclasses import dataclass, field
from datetime import datetime

from app.events.base import EventCandidate, RuleContext


@dataclass(slots=True)
class _TrackPresence:
    first_seen: datetime
    object_class: str
    event_emitted: bool = False


@dataclass(slots=True)
class LongPresenceRule:
    """Emit when a tracked object remains visible longer than a duration."""

    duration_seconds: float
    target_classes: frozenset[str]
    _tracks: dict[int, _TrackPresence] = field(default_factory=dict, init=False)

    @property
    def rule_name(self) -> str:
        return "long_presence"

    def evaluate(self, context: RuleContext) -> list[EventCandidate]:
        active_track_ids: set[int] = set()
        candidates: list[EventCandidate] = []

        for detection in context.tracked_detections:
            if detection.object_class not in self.target_classes:
                continue

            active_track_ids.add(detection.track_id)
            presence = self._tracks.get(detection.track_id)
            if presence is None:
                self._tracks[detection.track_id] = _TrackPresence(
                    first_seen=context.occurred_at,
                    object_class=detection.object_class,
                )
                continue

            duration = (context.occurred_at - presence.first_seen).total_seconds()
            if duration < self.duration_seconds or presence.event_emitted:
                continue

            presence.event_emitted = True
            candidates.append(
                EventCandidate(
                    event_type="long_presence",
                    severity="medium",
                    occurred_at=context.occurred_at,
                    started_at=presence.first_seen,
                    metadata={
                        "duration_seconds": int(duration),
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
