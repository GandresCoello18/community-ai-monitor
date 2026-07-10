from datetime import UTC, datetime, timedelta
from uuid import uuid4

from app.detection.base import BoundingBox
from app.events.base import RuleContext
from app.events.rules.abandoned_object import AbandonedObjectRule
from app.events.rules.crowd_detection import CrowdDetectionRule
from app.events.rules.high_density import HighDensityRule
from app.events.rules.long_presence import LongPresenceRule
from app.tracking.base import TrackedDetection

CAMERA_ID = uuid4()
BASE_TIME = datetime(2026, 7, 10, 15, 0, 0, tzinfo=UTC)


def _person(track_id: int, x: int = 10, y: int = 10) -> TrackedDetection:
    return TrackedDetection(
        track_id=track_id,
        object_class="person",
        confidence=0.9,
        bbox=BoundingBox(x=x, y=y, width=50, height=100),
    )


def _backpack(track_id: int, x: int = 200, y: int = 200) -> TrackedDetection:
    return TrackedDetection(
        track_id=track_id,
        object_class="backpack",
        confidence=0.85,
        bbox=BoundingBox(x=x, y=y, width=40, height=40),
    )


def _context(
    detections: list[TrackedDetection],
    *,
    occurred_at: datetime | None = None,
    frame_width: int = 640,
    frame_height: int = 480,
) -> RuleContext:
    return RuleContext(
        camera_id=CAMERA_ID,
        occurred_at=occurred_at or BASE_TIME,
        tracked_detections=detections,
        frame_width=frame_width,
        frame_height=frame_height,
    )


def test_crowd_rule_emits_when_threshold_reached() -> None:
    rule = CrowdDetectionRule(people_threshold=3, cooldown_seconds=0)
    people = [_person(i, x=i * 60) for i in range(1, 4)]

    events = rule.evaluate(_context(people))

    assert len(events) == 1
    assert events[0].event_type == "crowd_detected"
    assert events[0].metadata["people_count"] == 3


def test_crowd_rule_respects_cooldown() -> None:
    rule = CrowdDetectionRule(people_threshold=2, cooldown_seconds=60)
    people = [_person(1), _person(2)]

    assert len(rule.evaluate(_context(people))) == 1
    later = _context(people, occurred_at=BASE_TIME + timedelta(seconds=30))
    assert rule.evaluate(later) == []


def test_crowd_rule_ignores_fewer_people() -> None:
    rule = CrowdDetectionRule(people_threshold=5, cooldown_seconds=0)

    assert rule.evaluate(_context([_person(1), _person(2)])) == []


def test_high_density_rule_emits_when_area_threshold_exceeded() -> None:
    rule = HighDensityRule(
        min_people=2,
        density_threshold=0.1,
        cooldown_seconds=0,
    )
    # Two large boxes covering ~25% of a 640x480 frame.
    large_people = [
        TrackedDetection(
            track_id=1,
            object_class="person",
            confidence=0.9,
            bbox=BoundingBox(x=0, y=0, width=320, height=240),
        ),
        TrackedDetection(
            track_id=2,
            object_class="person",
            confidence=0.9,
            bbox=BoundingBox(x=320, y=0, width=320, height=240),
        ),
    ]

    events = rule.evaluate(_context(large_people))

    assert len(events) == 1
    assert events[0].event_type == "high_density"
    assert events[0].metadata["density_ratio"] >= 0.1


def test_long_presence_rule_emits_after_duration() -> None:
    rule = LongPresenceRule(
        duration_seconds=60,
        target_classes=frozenset({"person"}),
    )
    person = _person(42)

    assert rule.evaluate(_context([person], occurred_at=BASE_TIME)) == []

    later = BASE_TIME + timedelta(seconds=61)
    events = rule.evaluate(_context([person], occurred_at=later))

    assert len(events) == 1
    assert events[0].event_type == "long_presence"
    assert events[0].started_at == BASE_TIME
    assert events[0].metadata["track_id"] == 42


def test_long_presence_rule_emits_only_once_per_track() -> None:
    rule = LongPresenceRule(
        duration_seconds=10,
        target_classes=frozenset({"person"}),
    )
    person = _person(7)
    rule.evaluate(_context([person], occurred_at=BASE_TIME))
    t1 = BASE_TIME + timedelta(seconds=11)
    t2 = BASE_TIME + timedelta(seconds=20)

    assert len(rule.evaluate(_context([person], occurred_at=t1))) == 1
    assert rule.evaluate(_context([person], occurred_at=t2)) == []


def test_abandoned_object_rule_emits_when_stationary() -> None:
    rule = AbandonedObjectRule(
        duration_seconds=30,
        movement_threshold=5.0,
        target_classes=frozenset({"backpack"}),
    )
    bag = _backpack(99)

    assert rule.evaluate(_context([bag], occurred_at=BASE_TIME)) == []

    later = BASE_TIME + timedelta(seconds=31)
    events = rule.evaluate(_context([bag], occurred_at=later))

    assert len(events) == 1
    assert events[0].event_type == "abandoned_object"
    assert events[0].metadata["object_class"] == "backpack"


def test_abandoned_object_rule_resets_on_movement() -> None:
    rule = AbandonedObjectRule(
        duration_seconds=20,
        movement_threshold=5.0,
        target_classes=frozenset({"backpack"}),
    )
    t0 = BASE_TIME
    t1 = BASE_TIME + timedelta(seconds=15)
    t2 = BASE_TIME + timedelta(seconds=16)

    rule.evaluate(_context([_backpack(1, x=200)], occurred_at=t0))
    rule.evaluate(_context([_backpack(1, x=250)], occurred_at=t1))
    events = rule.evaluate(_context([_backpack(1, x=250)], occurred_at=t2))

    assert events == []
