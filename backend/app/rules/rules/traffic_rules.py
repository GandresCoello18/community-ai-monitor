from dataclasses import dataclass, field

from app.rules.base_rule import EventCandidate, MetricSample, RuleContext
from app.rules.config import RulesConfig
from app.rules.utils import CooldownState, filter_persons


def _density_severity(ratio: float, threshold: float) -> str:
    if ratio >= threshold * 2:
        return "high"
    if ratio >= threshold * 1.5:
        return "medium"
    return "low"


@dataclass(slots=True)
class HighDensityRule:
    min_people: int
    density_threshold: float
    cooldown: CooldownState
    _last_event_at: object = field(default=None, init=False)

    @property
    def rule_name(self) -> str:
        return "high_density"

    @property
    def is_placeholder(self) -> bool:
        return False

    def evaluate(self, context: RuleContext) -> list[EventCandidate]:
        people = filter_persons(context.tracked_detections)
        if len(people) < self.min_people:
            return []

        frame_area = context.frame_width * context.frame_height
        occupied = sum(p.bbox.width * p.bbox.height for p in people)
        density_ratio = occupied / frame_area if frame_area else 0.0
        if density_ratio < self.density_threshold:
            return []

        from datetime import datetime

        if isinstance(self._last_event_at, datetime):
            elapsed = (context.occurred_at - self._last_event_at).total_seconds()
            if elapsed < self.cooldown.cooldown_seconds:
                return []

        self._last_event_at = context.occurred_at
        return [
            EventCandidate(
                event_type="high_density",
                severity=_density_severity(density_ratio, self.density_threshold),
                occurred_at=context.occurred_at,
                metadata={
                    "people_count": len(people),
                    "density_ratio": round(density_ratio, 3),
                    "threshold": self.density_threshold,
                },
                rule_name=self.rule_name,
            )
        ]

    def collect_metrics(self, context: RuleContext) -> list[MetricSample]:
        return []

    def reset(self) -> None:
        self._last_event_at = None
        self.cooldown.reset()


@dataclass(slots=True)
class PlaceholderRule:
    event_type: str
    rule_key: str
    enabled: bool

    @property
    def rule_name(self) -> str:
        return self.rule_key

    @property
    def is_placeholder(self) -> bool:
        return True

    def evaluate(self, context: RuleContext) -> list[EventCandidate]:
        return []

    def collect_metrics(self, context: RuleContext) -> list[MetricSample]:
        return []

    def reset(self) -> None:
        return None


def build_traffic_rules(config: RulesConfig) -> list[object]:
    rules: list[object] = []
    if config.high_density_enabled:
        rules.append(
            HighDensityRule(
                min_people=config.high_density_min_people,
                density_threshold=config.high_density_threshold,
                cooldown=CooldownState(config.cooldown_seconds),
            )
        )
    return rules


def build_maintenance_rules(config: RulesConfig) -> list[object]:
    return [
        PlaceholderRule(
            event_type="trash_detected",
            rule_key="trash_detected",
            enabled=config.trash_detected_enabled,
        ),
        PlaceholderRule(
            event_type="obstruction_detected",
            rule_key="obstruction_detected",
            enabled=config.obstruction_detected_enabled,
        ),
    ]
