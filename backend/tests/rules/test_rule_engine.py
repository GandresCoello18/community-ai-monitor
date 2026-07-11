from datetime import UTC, datetime, timedelta
from uuid import uuid4

from app.detection.base import BoundingBox
from app.rules.base_rule import RuleContext
from app.rules.config import RulesConfig
from app.rules.engine import RuleEngine
from app.rules.factory import build_rules
from app.rules.rules.person_rules import (
    CrowdDetectedRule,
    PersonLongStayRule,
    PersonRepeatedActivityRule,
)
from app.rules.rules.vehicle_rules import VehicleLongParkingRule
from app.rules.utils import CooldownState
from app.tracking.base import TrackedDetection
from app.core.config import Settings

CAMERA_ID = uuid4()
BASE_TIME = datetime(2026, 7, 10, 15, 0, 0, tzinfo=UTC)


def _person(track_id: int, x: int = 10, y: int = 10) -> TrackedDetection:
    return TrackedDetection(
        track_id=track_id,
        object_class="person",
        confidence=0.9,
        bbox=BoundingBox(x=x, y=y, width=50, height=100),
    )


def _car(track_id: int, x: int = 100, y: int = 400) -> TrackedDetection:
    return TrackedDetection(
        track_id=track_id,
        object_class="car",
        confidence=0.9,
        bbox=BoundingBox(x=x, y=y, width=120, height=60),
    )


def _context(
    detections: list[TrackedDetection],
    *,
    occurred_at: datetime | None = None,
) -> RuleContext:
    return RuleContext(
        camera_id=CAMERA_ID,
        occurred_at=occurred_at or BASE_TIME,
        tracked_detections=detections,
        frame_width=640,
        frame_height=480,
        scene_type="general",
    )


def test_person_long_stay_emits_new_event_type() -> None:
    rule = PersonLongStayRule(duration_seconds=60, emit_legacy=False)
    person = _person(42)

    assert rule.evaluate(_context([person])) == []

    later = BASE_TIME + timedelta(seconds=61)
    events = rule.evaluate(_context([person], occurred_at=later))

    assert len(events) == 1
    assert events[0].event_type == "person_long_stay"
    assert events[0].rule_name == "person_long_stay"


def test_person_repeated_activity_emits_after_visits() -> None:
    rule = PersonRepeatedActivityRule(
        window_seconds=1800,
        min_visits=3,
        zone_radius=80.0,
    )
    person = _person(7, x=100, y=100)

    rule.evaluate(_context([person], occurred_at=BASE_TIME))
    rule.evaluate(
        _context([_person(7, x=300, y=100)], occurred_at=BASE_TIME + timedelta(minutes=5))
    )
    events = rule.evaluate(
        _context([_person(7, x=110, y=100)], occurred_at=BASE_TIME + timedelta(minutes=10))
    )

    assert len(events) == 1
    assert events[0].event_type == "person_repeated_activity"
    assert events[0].metadata["visit_count"] >= 3


def test_vehicle_long_parking_emits_after_stationary_period() -> None:
    rule = VehicleLongParkingRule(duration_seconds=30, movement_threshold=5.0)
    car = _car(25)

    assert rule.evaluate(_context([car])) == []

    later = BASE_TIME + timedelta(seconds=31)
    events = rule.evaluate(_context([car], occurred_at=later))

    assert len(events) == 1
    assert events[0].event_type == "vehicle_long_parking"
    assert events[0].metadata["track_id"] == 25


def test_crowd_rule_collects_metrics() -> None:
    rule = CrowdDetectedRule(threshold=2, cooldown=CooldownState(0))
    people = [_person(1), _person(2), _person(3)]

    rule.evaluate(_context(people))
    metrics = rule.collect_metrics(_context(people))

    assert len(metrics) == 1
    assert metrics[0].metric_type == "people_count"
    assert metrics[0].value == 3.0


def test_rules_config_from_settings_honors_legacy_flags() -> None:
    settings = Settings(
        app_env="testing",
        event_long_presence_enabled=False,
        rule_person_long_stay_enabled=True,
    )
    config = RulesConfig.from_settings(settings)

    assert config.person_long_stay_enabled is False


def test_rule_engine_runs_street_scene_rules() -> None:
    settings = Settings(
        app_env="testing",
        rule_scene_type="street",
        rule_crowd_threshold=10,
        rule_park_occupancy_enabled=False,
        rule_park_empty_enabled=False,
    )
    rules = build_rules(settings)
    names = {getattr(rule, "rule_name") for rule in rules}

    assert "vehicle_long_parking" in names
    assert "park_occupancy_changed" not in names


def test_rule_engine_process_returns_events_and_metrics() -> None:
    engine = RuleEngine(
        CAMERA_ID,
        [CrowdDetectedRule(threshold=2, cooldown=CooldownState(0))],
    )
    tracked = [_person(1), _person(2)]

    result = engine.process(tracked, BASE_TIME)

    assert len(result.events) == 1
    assert result.events[0].event_type == "crowd_detected"
    assert len(result.metrics) == 1
