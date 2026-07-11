from dataclasses import dataclass, field

from app.rules.base_rule import EventCandidate, MetricSample, RuleContext
from app.rules.config import RulesConfig
from app.rules.utils import CooldownState, filter_class


@dataclass(slots=True)
class AnimalDetectedRule:
    target_classes: frozenset[str]
    cooldown: CooldownState
    _seen: set[int] = field(default_factory=set, init=False)

    @property
    def rule_name(self) -> str:
        return "animal_detected"

    @property
    def is_placeholder(self) -> bool:
        return False

    def evaluate(self, context: RuleContext) -> list[EventCandidate]:
        candidates: list[EventCandidate] = []
        for detection in filter_class(context.tracked_detections, self.target_classes):
            if detection.track_id in self._seen:
                continue
            key = f"animal_{detection.track_id}"
            if not self.cooldown.ready(key, context.occurred_at):
                continue
            self.cooldown.mark(key, context.occurred_at)
            self._seen.add(detection.track_id)
            candidates.append(
                EventCandidate(
                    event_type="animal_detected",
                    severity="low",
                    occurred_at=context.occurred_at,
                    metadata={
                        "object_class": detection.object_class,
                        "track_id": detection.track_id,
                        "confidence": round(detection.confidence, 2),
                    },
                    rule_name=self.rule_name,
                )
            )
        return candidates

    def collect_metrics(self, context: RuleContext) -> list[MetricSample]:
        animals = filter_class(context.tracked_detections, self.target_classes)
        bucket = context.occurred_at.replace(minute=0, second=0, microsecond=0)
        return [
            MetricSample(
                metric_type="animal_count",
                value=float(len(animals)),
                bucket_start=bucket,
            )
        ]

    def reset(self) -> None:
        self._seen.clear()
        self.cooldown.reset()


def build_animal_rules(config: RulesConfig) -> list[object]:
    if not config.animal_enabled:
        return []
    return [
        AnimalDetectedRule(
            target_classes=config.animal_classes,
            cooldown=CooldownState(config.animal_cooldown_seconds),
        )
    ]
