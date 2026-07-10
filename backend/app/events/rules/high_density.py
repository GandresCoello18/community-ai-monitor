from dataclasses import dataclass, field
from datetime import datetime

from app.events.base import EventCandidate, RuleContext


@dataclass(slots=True)
class HighDensityRule:
    """Emit when people occupy a large fraction of the frame (aglomeración)."""

    min_people: int
    density_threshold: float
    cooldown_seconds: float
    _last_event_at: datetime | None = field(default=None, init=False)

    @property
    def rule_name(self) -> str:
        return "high_density"

    def evaluate(self, context: RuleContext) -> list[EventCandidate]:
        people = [
            item
            for item in context.tracked_detections
            if item.object_class == "person"
        ]
        if len(people) < self.min_people:
            return []

        frame_area = context.frame_width * context.frame_height
        if frame_area <= 0:
            return []

        occupied_area = sum(
            item.bbox.width * item.bbox.height for item in people
        )
        density_ratio = round(occupied_area / frame_area, 4)
        if density_ratio < self.density_threshold:
            return []

        if self._last_event_at is not None:
            elapsed = (context.occurred_at - self._last_event_at).total_seconds()
            if elapsed < self.cooldown_seconds:
                return []

        severity = (
            "medium"
            if density_ratio < self.density_threshold * 1.5
            else "high"
        )
        self._last_event_at = context.occurred_at
        return [
            EventCandidate(
                event_type="high_density",
                severity=severity,
                occurred_at=context.occurred_at,
                metadata={
                    "people_count": len(people),
                    "density_ratio": density_ratio,
                    "threshold": self.density_threshold,
                },
            )
        ]

    def reset(self) -> None:
        self._last_event_at = None
