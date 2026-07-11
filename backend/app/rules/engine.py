from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

import logging

from app.rules.base_rule import EventCandidate, MetricSample, RuleContext, RuleProtocol
from app.tracking.base import TrackedDetection

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class RuleEngineResult:
    events: list[EventCandidate]
    metrics: list[MetricSample]


class RuleEngine:
    """Evaluates community behavior rules for one camera stream."""

    def __init__(self, camera_id: UUID, rules: list[RuleProtocol]) -> None:
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
        scene_type: str = "general",
    ) -> RuleEngineResult:
        if not self._rules:
            return RuleEngineResult(events=[], metrics=[])

        context = RuleContext(
            camera_id=self._camera_id,
            occurred_at=occurred_at,
            tracked_detections=tracked,
            frame_width=frame_width,
            frame_height=frame_height,
            scene_type=scene_type,
        )

        events: list[EventCandidate] = []
        metrics: list[MetricSample] = []

        for rule in self._rules:
            try:
                if tracked:
                    events.extend(rule.evaluate(context))
                metrics.extend(rule.collect_metrics(context))
            except Exception:
                logger.exception(
                    "Rule failed camera_id=%s rule=%s",
                    self._camera_id,
                    rule.rule_name,
                )

        return RuleEngineResult(events=events, metrics=metrics)

    def reset(self) -> None:
        for rule in self._rules:
            rule.reset()
