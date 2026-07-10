from dataclasses import dataclass, field
from datetime import datetime

from app.events.base import EventCandidate, RuleContext


def _crowd_severity(count: int, threshold: int) -> str:
    ratio = count / threshold if threshold > 0 else 1.0
    if ratio >= 2.0:
        return "high"
    if ratio >= 1.5:
        return "medium"
    return "low"


@dataclass(slots=True)
class CrowdDetectionRule:
    """Emit when the number of detected people exceeds a threshold."""

    people_threshold: int
    cooldown_seconds: float
    _last_event_at: datetime | None = field(default=None, init=False)

    @property
    def rule_name(self) -> str:
        return "crowd_detection"

    def evaluate(self, context: RuleContext) -> list[EventCandidate]:
        people = [
            item
            for item in context.tracked_detections
            if item.object_class == "person"
        ]
        count = len(people)
        if count < self.people_threshold:
            return []

        if self._last_event_at is not None:
            elapsed = (context.occurred_at - self._last_event_at).total_seconds()
            if elapsed < self.cooldown_seconds:
                return []

        self._last_event_at = context.occurred_at
        return [
            EventCandidate(
                event_type="crowd_detected",
                severity=_crowd_severity(count, self.people_threshold),
                occurred_at=context.occurred_at,
                metadata={
                    "people_count": count,
                    "threshold": self.people_threshold,
                },
            )
        ]

    def reset(self) -> None:
        self._last_event_at = None
