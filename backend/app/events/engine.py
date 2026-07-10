import logging
from datetime import datetime
from uuid import UUID

from app.events.base import EventCandidate, EventRule, RuleContext
from app.tracking.base import TrackedDetection

logger = logging.getLogger(__name__)


class EventEngine:
    """Evaluates all configured rules for one camera stream.

    Holds per-camera rule state. Pure business logic: no database or HTTP.
    """

    def __init__(self, camera_id: UUID, rules: list[EventRule]) -> None:
        self._camera_id = camera_id
        self._rules = rules

    @property
    def camera_id(self) -> UUID:
        return self._camera_id

    @property
    def rule_names(self) -> list[str]:
        return [rule.rule_name for rule in self._rules]

    def process(
        self,
        tracked: list[TrackedDetection],
        occurred_at: datetime,
        *,
        frame_width: int = 640,
        frame_height: int = 480,
    ) -> list[EventCandidate]:
        if not self._rules or not tracked:
            return []

        context = RuleContext(
            camera_id=self._camera_id,
            occurred_at=occurred_at,
            tracked_detections=tracked,
            frame_width=frame_width,
            frame_height=frame_height,
        )

        candidates: list[EventCandidate] = []
        for rule in self._rules:
            try:
                candidates.extend(rule.evaluate(context))
            except Exception:
                logger.exception(
                    "Event rule failed camera_id=%s rule=%s",
                    self._camera_id,
                    rule.rule_name,
                )
        return candidates

    def reset(self) -> None:
        for rule in self._rules:
            rule.reset()
