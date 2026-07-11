from dataclasses import dataclass, field
from datetime import datetime

from app.rules.base_rule import EventCandidate, MetricSample, RuleContext
from app.rules.config import RulesConfig
from app.rules.utils import CooldownState, bbox_center, distance, filter_persons


def _crowd_severity(count: int, threshold: int) -> str:
    ratio = count / threshold if threshold > 0 else 1.0
    if ratio >= 2.0:
        return "high"
    if ratio >= 1.5:
        return "medium"
    return "low"


@dataclass(slots=True)
class PersonLongStayRule:
    duration_seconds: float
    emit_legacy: bool = True
    _tracks: dict[int, datetime] = field(default_factory=dict, init=False)
    _emitted: set[int] = field(default_factory=set, init=False)

    @property
    def rule_name(self) -> str:
        return "person_long_stay"

    @property
    def is_placeholder(self) -> bool:
        return False

    def evaluate(self, context: RuleContext) -> list[EventCandidate]:
        active: set[int] = set()
        candidates: list[EventCandidate] = []

        for detection in filter_persons(context.tracked_detections):
            active.add(detection.track_id)
            first_seen = self._tracks.get(detection.track_id)
            if first_seen is None:
                self._tracks[detection.track_id] = context.occurred_at
                continue
            duration = (context.occurred_at - first_seen).total_seconds()
            if duration < self.duration_seconds or detection.track_id in self._emitted:
                continue
            self._emitted.add(detection.track_id)
            meta = {
                "duration_seconds": int(duration),
                "track_id": detection.track_id,
                "object_class": "person",
            }
            candidates.append(
                EventCandidate(
                    event_type="person_long_stay",
                    severity="medium",
                    occurred_at=context.occurred_at,
                    started_at=first_seen,
                    metadata=meta,
                    rule_name=self.rule_name,
                )
            )
            if self.emit_legacy:
                candidates.append(
                    EventCandidate(
                        event_type="long_presence",
                        severity="medium",
                        occurred_at=context.occurred_at,
                        started_at=first_seen,
                        metadata=meta,
                        rule_name=self.rule_name,
                    )
                )

        for track_id in list(self._tracks):
            if track_id not in active:
                del self._tracks[track_id]
                self._emitted.discard(track_id)
        return candidates

    def collect_metrics(self, context: RuleContext) -> list[MetricSample]:
        return []

    def reset(self) -> None:
        self._tracks.clear()
        self._emitted.clear()


@dataclass(slots=True)
class PersonRepeatedActivityRule:
    window_seconds: float
    min_visits: int
    zone_radius: float
    _visits: dict[int, list[tuple[datetime, tuple[float, float]]]] = field(
        default_factory=dict,
        init=False,
    )
    _emitted: set[int] = field(default_factory=set, init=False)

    @property
    def rule_name(self) -> str:
        return "person_repeated_activity"

    @property
    def is_placeholder(self) -> bool:
        return False

    def evaluate(self, context: RuleContext) -> list[EventCandidate]:
        candidates: list[EventCandidate] = []
        active: set[int] = set()

        for detection in filter_persons(context.tracked_detections):
            active.add(detection.track_id)
            center = bbox_center(detection.bbox)
            history = self._visits.setdefault(detection.track_id, [])
            if not history or distance(history[-1][1], center) > self.zone_radius:
                history.append((context.occurred_at, center))
            cutoff = context.occurred_at.timestamp() - self.window_seconds
            history[:] = [
                (ts, pos) for ts, pos in history if ts.timestamp() >= cutoff
            ]
            if (
                len(history) >= self.min_visits
                and detection.track_id not in self._emitted
            ):
                self._emitted.add(detection.track_id)
                candidates.append(
                    EventCandidate(
                        event_type="person_repeated_activity",
                        severity="medium",
                        occurred_at=context.occurred_at,
                        metadata={
                            "track_id": detection.track_id,
                            "visit_count": len(history),
                            "window_seconds": int(self.window_seconds),
                            "note": "heuristic_pattern_detected",
                        },
                        rule_name=self.rule_name,
                    )
                )

        for track_id in list(self._visits):
            if track_id not in active:
                del self._visits[track_id]
                self._emitted.discard(track_id)
        return candidates

    def collect_metrics(self, context: RuleContext) -> list[MetricSample]:
        return []

    def reset(self) -> None:
        self._visits.clear()
        self._emitted.clear()


@dataclass(slots=True)
class PersonHiddenActivityRule:
    duration_seconds: float
    max_movement: float
    _tracks: dict[int, tuple[datetime, tuple[float, float]]] = field(
        default_factory=dict,
        init=False,
    )
    _emitted: set[int] = field(default_factory=set, init=False)

    @property
    def rule_name(self) -> str:
        return "person_hidden_activity"

    @property
    def is_placeholder(self) -> bool:
        return False

    def evaluate(self, context: RuleContext) -> list[EventCandidate]:
        candidates: list[EventCandidate] = []
        active: set[int] = set()

        for detection in filter_persons(context.tracked_detections):
            active.add(detection.track_id)
            center = bbox_center(detection.bbox)
            nx = center[0] / context.frame_width
            ny = center[1] / context.frame_height
            near_edge = nx < 0.12 or nx > 0.88 or ny < 0.12 or ny > 0.88
            small = detection.bbox.height < context.frame_height * 0.25

            state = self._tracks.get(detection.track_id)
            if state is None:
                self._tracks[detection.track_id] = (context.occurred_at, center)
                continue

            first_seen, anchor = state
            moved = distance(anchor, center)
            duration = (context.occurred_at - first_seen).total_seconds()
            if moved > self.max_movement:
                self._tracks[detection.track_id] = (context.occurred_at, center)
                self._emitted.discard(detection.track_id)
                continue

            if (
                duration >= self.duration_seconds
                and (near_edge or small)
                and detection.track_id not in self._emitted
            ):
                self._emitted.add(detection.track_id)
                candidates.append(
                    EventCandidate(
                        event_type="person_hidden_activity",
                        severity="low",
                        occurred_at=context.occurred_at,
                        started_at=first_seen,
                        metadata={
                            "track_id": detection.track_id,
                            "duration_seconds": int(duration),
                            "note": "possible_limited_visibility_heuristic",
                        },
                        rule_name=self.rule_name,
                    )
                )

        for track_id in list(self._tracks):
            if track_id not in active:
                del self._tracks[track_id]
                self._emitted.discard(track_id)
        return candidates

    def collect_metrics(self, context: RuleContext) -> list[MetricSample]:
        return []

    def reset(self) -> None:
        self._tracks.clear()
        self._emitted.clear()


@dataclass(slots=True)
class CrowdDetectedRule:
    threshold: int
    cooldown: CooldownState
    _peak: int = 0

    @property
    def rule_name(self) -> str:
        return "crowd_detected"

    @property
    def is_placeholder(self) -> bool:
        return False

    def evaluate(self, context: RuleContext) -> list[EventCandidate]:
        people = filter_persons(context.tracked_detections)
        count = len(people)
        self._peak = max(self._peak, count)
        if count < self.threshold:
            return []
        if not self.cooldown.ready("crowd", context.occurred_at):
            return []
        self.cooldown.mark("crowd", context.occurred_at)
        return [
            EventCandidate(
                event_type="crowd_detected",
                severity=_crowd_severity(count, self.threshold),
                occurred_at=context.occurred_at,
                metadata={
                    "people_count": count,
                    "threshold": self.threshold,
                },
                rule_name=self.rule_name,
            )
        ]

    def collect_metrics(self, context: RuleContext) -> list[MetricSample]:
        people = filter_persons(context.tracked_detections)
        bucket = context.occurred_at.replace(minute=0, second=0, microsecond=0)
        return [
            MetricSample(
                metric_type="people_count",
                value=float(len(people)),
                bucket_start=bucket,
                metadata={"peak_session": self._peak},
            )
        ]

    def reset(self) -> None:
        self.cooldown.reset()
        self._peak = 0


def build_person_rules(config: RulesConfig) -> list[object]:
    rules: list[object] = []
    cooldown = CooldownState(config.cooldown_seconds)
    if config.person_long_stay_enabled:
        rules.append(
            PersonLongStayRule(
                duration_seconds=config.person_long_stay_seconds,
                emit_legacy=config.emit_legacy_event_types,
            )
        )
    if config.person_repeated_activity_enabled:
        rules.append(
            PersonRepeatedActivityRule(
                window_seconds=config.person_repeated_activity_window_seconds,
                min_visits=config.person_repeated_activity_min_visits,
                zone_radius=config.person_repeated_activity_zone_radius,
            )
        )
    if config.person_hidden_activity_enabled:
        rules.append(
            PersonHiddenActivityRule(
                duration_seconds=config.person_hidden_stay_seconds,
                max_movement=config.person_hidden_max_movement,
            )
        )
    if config.crowd_enabled:
        rules.append(
            CrowdDetectedRule(threshold=config.crowd_threshold, cooldown=cooldown)
        )
    return rules
