from dataclasses import dataclass, field
from datetime import datetime

from app.rules.base_rule import EventCandidate, MetricSample, RuleContext
from app.rules.config import RulesConfig
from app.rules.utils import (
    VEHICLE_CLASSES,
    CooldownState,
    bbox_center,
    distance,
    filter_vehicles,
    normalized_center,
)


@dataclass(slots=True)
class _VehicleTrack:
    first_seen: datetime
    stationary_since: datetime
    last_center: tuple[float, float]
    object_class: str
    event_emitted: bool = False
    parking_event_emitted: bool = False


@dataclass(slots=True)
class VehicleLongParkingRule:
    duration_seconds: float
    movement_threshold: float

    _tracks: dict[int, _VehicleTrack] = field(default_factory=dict, init=False)
    _total_parking_seconds: float = 0.0
    _parking_samples: int = 0

    @property
    def rule_name(self) -> str:
        return "vehicle_long_parking"

    @property
    def is_placeholder(self) -> bool:
        return False

    def evaluate(self, context: RuleContext) -> list[EventCandidate]:
        return self._evaluate_vehicle_events(context, parking=True, double=False)

    def _evaluate_vehicle_events(
        self,
        context: RuleContext,
        *,
        parking: bool,
        double: bool,
        street_y_start: float = 0.55,
    ) -> list[EventCandidate]:
        active: set[int] = set()
        candidates: list[EventCandidate] = []

        for detection in filter_vehicles(context.tracked_detections):
            if detection.object_class == "bicycle" and parking:
                continue
            center = bbox_center(detection.bbox)
            active.add(detection.track_id)
            track = self._tracks.get(detection.track_id)

            if track is None:
                self._tracks[detection.track_id] = _VehicleTrack(
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
                track.parking_event_emitted = False

            stationary = (
                context.occurred_at - track.stationary_since
            ).total_seconds()

            if parking and not track.parking_event_emitted:
                if stationary >= self.duration_seconds:
                    track.parking_event_emitted = True
                    self._total_parking_seconds += stationary
                    self._parking_samples += 1
                    candidates.append(
                        EventCandidate(
                            event_type="vehicle_long_parking",
                            severity="medium",
                            occurred_at=context.occurred_at,
                            started_at=track.stationary_since,
                            metadata={
                                "duration_seconds": int(stationary),
                                "track_id": detection.track_id,
                                "object_class": detection.object_class,
                            },
                            rule_name=self.rule_name,
                        )
                    )

            if double and not track.event_emitted:
                _, ny = normalized_center(
                    detection,
                    context.frame_width,
                    context.frame_height,
                )
                if ny >= street_y_start and stationary >= self.duration_seconds:
                    track.event_emitted = True
                    candidates.append(
                        EventCandidate(
                            event_type="double_parking",
                            severity="medium",
                            occurred_at=context.occurred_at,
                            started_at=track.stationary_since,
                            metadata={
                                "duration_seconds": int(stationary),
                                "track_id": detection.track_id,
                                "zone": "street",
                            },
                            rule_name="double_parking",
                        )
                    )

        for track_id in list(self._tracks):
            if track_id not in active:
                del self._tracks[track_id]
        return candidates

    def collect_metrics(self, context: RuleContext) -> list[MetricSample]:
        vehicles = filter_vehicles(context.tracked_detections)
        by_class: dict[str, int] = {}
        for item in vehicles:
            by_class[item.object_class] = by_class.get(item.object_class, 0) + 1
        bucket = context.occurred_at.replace(minute=0, second=0, microsecond=0)
        samples = [
            MetricSample(
                metric_type="vehicle_count",
                value=float(len(vehicles)),
                bucket_start=bucket,
                metadata={"by_class": by_class},
            )
        ]
        if self._parking_samples:
            samples.append(
                MetricSample(
                    metric_type="avg_parking_duration_seconds",
                    value=self._total_parking_seconds / self._parking_samples,
                    bucket_start=bucket,
                    metadata={"samples": self._parking_samples},
                )
            )
        return samples

    def reset(self) -> None:
        self._tracks.clear()
        self._total_parking_seconds = 0.0
        self._parking_samples = 0


@dataclass(slots=True)
class DoubleParkingRule:
    duration_seconds: float
    movement_threshold: float
    street_zone_y_start: float
    _delegate: VehicleLongParkingRule = field(init=False)

    def __post_init__(self) -> None:
        self._delegate = VehicleLongParkingRule(
            duration_seconds=self.duration_seconds,
            movement_threshold=self.movement_threshold,
        )

    @property
    def rule_name(self) -> str:
        return "double_parking"

    @property
    def is_placeholder(self) -> bool:
        return False

    def evaluate(self, context: RuleContext) -> list[EventCandidate]:
        return self._delegate._evaluate_vehicle_events(
            context,
            parking=False,
            double=True,
            street_y_start=self.street_zone_y_start,
        )

    def collect_metrics(self, context: RuleContext) -> list[MetricSample]:
        return []

    def reset(self) -> None:
        self._delegate.reset()


@dataclass(slots=True)
class WrongDirectionRule:
    min_displacement: float
    expected_direction: str
    cooldown: CooldownState
    _last_center: dict[int, tuple[float, float]] = field(default_factory=dict, init=False)

    @property
    def rule_name(self) -> str:
        return "wrong_direction"

    @property
    def is_placeholder(self) -> bool:
        return False

    def evaluate(self, context: RuleContext) -> list[EventCandidate]:
        candidates: list[EventCandidate] = []
        active: set[int] = set()

        for detection in filter_vehicles(context.tracked_detections):
            if detection.object_class not in {"car", "motorcycle", "bus", "truck"}:
                continue
            active.add(detection.track_id)
            center = bbox_center(detection.bbox)
            prev = self._last_center.get(detection.track_id)
            self._last_center[detection.track_id] = center
            if prev is None:
                continue
            dx = center[0] - prev[0]
            if abs(dx) < self.min_displacement:
                continue
            moving_ltr = dx > 0
            expected_ltr = self.expected_direction == "ltr"
            if moving_ltr == expected_ltr:
                continue
            if not self.cooldown.ready(f"wrong_{detection.track_id}", context.occurred_at):
                continue
            self.cooldown.mark(f"wrong_{detection.track_id}", context.occurred_at)
            candidates.append(
                EventCandidate(
                    event_type="wrong_direction",
                    severity="high",
                    occurred_at=context.occurred_at,
                    metadata={
                        "track_id": detection.track_id,
                        "object_class": detection.object_class,
                        "displacement_x": round(dx, 1),
                        "note": "heuristic_direction_estimate",
                    },
                    rule_name=self.rule_name,
                )
            )

        for track_id in list(self._last_center):
            if track_id not in active:
                del self._last_center[track_id]
        return candidates

    def collect_metrics(self, context: RuleContext) -> list[MetricSample]:
        bucket = context.occurred_at.replace(minute=0, second=0, microsecond=0)
        flow = len(
            [
                d
                for d in filter_vehicles(context.tracked_detections)
                if d.object_class in VEHICLE_CLASSES
            ]
        )
        return [
            MetricSample(
                metric_type="traffic_flow_count",
                value=float(flow),
                bucket_start=bucket,
            )
        ]

    def reset(self) -> None:
        self._last_center.clear()
        self.cooldown.reset()


def build_vehicle_rules(config: RulesConfig) -> list[object]:
    rules: list[object] = []
    cooldown = CooldownState(config.cooldown_seconds)
    if config.vehicle_long_parking_enabled:
        rules.append(
            VehicleLongParkingRule(
                duration_seconds=config.vehicle_parking_seconds,
                movement_threshold=config.vehicle_parking_movement_threshold,
            )
        )
    if config.double_parking_enabled:
        rules.append(
            DoubleParkingRule(
                duration_seconds=config.double_parking_seconds,
                movement_threshold=config.vehicle_parking_movement_threshold,
                street_zone_y_start=config.street_zone_y_start,
            )
        )
    if config.wrong_direction_enabled:
        rules.append(
            WrongDirectionRule(
                min_displacement=config.wrong_direction_min_displacement,
                expected_direction=config.expected_traffic_direction,
                cooldown=cooldown,
            )
        )
    return rules
