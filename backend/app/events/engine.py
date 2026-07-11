import logging
from datetime import datetime
from uuid import UUID

from app.events.base import EventCandidate, EventRule, RuleContext
from app.rules.engine import RuleEngine as _RuleEngine
from app.tracking.base import TrackedDetection

logger = logging.getLogger(__name__)


class EventEngine:
    """Backward-compatible wrapper around the community RuleEngine."""

    def __init__(self, camera_id: UUID, rules: list[EventRule]) -> None:
        self._inner = _RuleEngine(camera_id, rules)

    @property
    def camera_id(self) -> UUID:
        return self._inner.camera_id

    @property
    def rule_names(self) -> list[str]:
        return self._inner.rule_names

    def process(
        self,
        tracked: list[TrackedDetection],
        occurred_at: datetime,
        *,
        frame_width: int = 640,
        frame_height: int = 480,
    ) -> list[EventCandidate]:
        result = self._inner.process(
            tracked,
            occurred_at,
            frame_width=frame_width,
            frame_height=frame_height,
        )
        return result.events

    def reset(self) -> None:
        self._inner.reset()
