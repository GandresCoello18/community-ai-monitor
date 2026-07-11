from dataclasses import dataclass, field
from datetime import datetime

from app.rules.base_rule import EventCandidate, MetricSample, RuleContext
from app.rules.config import RulesConfig
from app.rules.utils import CooldownState, filter_persons, in_normalized_zone


@dataclass(slots=True)
class ParkOccupancyRule:
    change_threshold: int
    cooldown: CooldownState
    config: RulesConfig
    _last_count: int | None = None

    @property
    def rule_name(self) -> str:
        return "park_occupancy"

    @property
    def is_placeholder(self) -> bool:
        return False

    def evaluate(self, context: RuleContext) -> list[EventCandidate]:
        count = len(filter_persons(context.tracked_detections))
        if self._last_count is None:
            self._last_count = count
            return []
        delta = abs(count - self._last_count)
        previous = self._last_count
        self._last_count = count
        if delta < self.change_threshold:
            return []
        if not self.cooldown.ready("occupancy", context.occurred_at):
            return []
        self.cooldown.mark("occupancy", context.occurred_at)
        return [
            EventCandidate(
                event_type="park_occupancy_changed",
                severity="low",
                occurred_at=context.occurred_at,
                metadata={
                    "previous_count": previous,
                    "current_count": count,
                    "delta": delta,
                },
                rule_name=self.rule_name,
            )
        ]

    def collect_metrics(self, context: RuleContext) -> list[MetricSample]:
        return _park_zone_metrics(context, self.config)

    def reset(self) -> None:
        self._last_count = None
        self.cooldown.reset()


@dataclass(slots=True)
class ParkEmptyRule:
    empty_seconds: float
    _empty_since: datetime | None = field(default=None, init=False)
    _emitted: bool = False

    @property
    def rule_name(self) -> str:
        return "park_empty"

    @property
    def is_placeholder(self) -> bool:
        return False

    def evaluate(self, context: RuleContext) -> list[EventCandidate]:
        count = len(filter_persons(context.tracked_detections))
        if count > 0:
            self._empty_since = None
            self._emitted = False
            return []

        if self._empty_since is None:
            self._empty_since = context.occurred_at
            return []

        duration = (context.occurred_at - self._empty_since).total_seconds()
        if duration < self.empty_seconds or self._emitted:
            return []

        self._emitted = True
        return [
            EventCandidate(
                event_type="park_empty",
                severity="low",
                occurred_at=context.occurred_at,
                started_at=self._empty_since,
                metadata={"duration_seconds": int(duration)},
                rule_name=self.rule_name,
            )
        ]

    def collect_metrics(self, context: RuleContext) -> list[MetricSample]:
        people = filter_persons(context.tracked_detections)
        bucket = context.occurred_at.replace(minute=0, second=0, microsecond=0)
        return [
            MetricSample(
                metric_type="park_occupancy",
                value=float(len(people)),
                bucket_start=bucket,
            )
        ]

    def reset(self) -> None:
        self._empty_since = None
        self._emitted = False


def _park_zone_metrics(context: RuleContext, config: RulesConfig) -> list[MetricSample]:
    people = filter_persons(context.tracked_detections)
    bucket = context.occurred_at.replace(minute=0, second=0, microsecond=0)
    zones = {
        "playground": config.park_zones.playground,
        "sports": config.park_zones.sports,
        "green": config.park_zones.green,
    }
    zone_counts = {
        name: sum(
            1
            for person in people
            if in_normalized_zone(
                person,
                zone,
                context.frame_width,
                context.frame_height,
            )
        )
        for name, zone in zones.items()
    }
    return [
        MetricSample(
            metric_type="park_zone_usage",
            value=float(sum(zone_counts.values())),
            bucket_start=bucket,
            metadata={"zones": zone_counts},
        )
    ]


@dataclass(slots=True)
class ParkDwellMetricsRule:
    _dwell_total: float = 0.0
    _dwell_samples: int = 0
    _tracks: dict[int, datetime] = field(default_factory=dict, init=False)

    @property
    def rule_name(self) -> str:
        return "park_dwell_metrics"

    @property
    def is_placeholder(self) -> bool:
        return False

    def evaluate(self, context: RuleContext) -> list[EventCandidate]:
        return []

    def collect_metrics(self, context: RuleContext) -> list[MetricSample]:
        from datetime import datetime

        active: set[int] = set()
        for person in filter_persons(context.tracked_detections):
            active.add(person.track_id)
            if person.track_id not in self._tracks:
                self._tracks[person.track_id] = context.occurred_at

        for track_id in list(self._tracks):
            if track_id not in active:
                dwell = (context.occurred_at - self._tracks[track_id]).total_seconds()
                self._dwell_total += dwell
                self._dwell_samples += 1
                del self._tracks[track_id]

        if not self._dwell_samples:
            return []

        bucket = context.occurred_at.replace(minute=0, second=0, microsecond=0)
        return [
            MetricSample(
                metric_type="avg_dwell_seconds",
                value=self._dwell_total / self._dwell_samples,
                bucket_start=bucket,
                metadata={"completed_visits": self._dwell_samples},
            )
        ]

    def reset(self) -> None:
        self._tracks.clear()
        self._dwell_total = 0.0
        self._dwell_samples = 0


def build_park_rules(config: RulesConfig) -> list[object]:
    rules: list[object] = []
    cooldown = CooldownState(config.cooldown_seconds)
    if config.park_occupancy_enabled:
        rules.append(
            ParkOccupancyRule(
                change_threshold=config.park_occupancy_change_threshold,
                cooldown=cooldown,
                config=config,
            )
        )
    if config.park_empty_enabled:
        rules.append(ParkEmptyRule(empty_seconds=config.park_empty_seconds))
    rules.append(ParkDwellMetricsRule())
    return rules
