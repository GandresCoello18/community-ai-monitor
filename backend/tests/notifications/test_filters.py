from datetime import UTC, datetime, time
from uuid import uuid4

from app.core.config import Settings
from app.models import Event
from app.notifications.filters import (
    NotificationFilter,
    is_within_quiet_hours,
    meets_min_severity,
    parse_hh_mm,
)


def _event(severity: str = "medium", event_type: str = "crowd_detected") -> Event:
    now = datetime.now(UTC)
    return Event(
        id=uuid4(),
        camera_id=uuid4(),
        event_type=event_type,
        severity=severity,
        occurred_at=now,
        started_at=None,
        ended_at=None,
        metadata_=None,
        created_at=now,
        updated_at=now,
    )


def test_meets_min_severity() -> None:
    assert meets_min_severity("high", "medium") is True
    assert meets_min_severity("low", "medium") is False
    assert meets_min_severity("critical", "high") is True


def test_parse_hh_mm() -> None:
    assert parse_hh_mm("22:00") == time(22, 0)
    assert parse_hh_mm("invalid") is None


def test_quiet_hours_same_day() -> None:
    moment = datetime(2026, 7, 11, 23, 0, tzinfo=UTC)
    assert is_within_quiet_hours(
        moment,
        quiet_start=time(22, 0),
        quiet_end=time(6, 0),
    ) is True


def test_quiet_hours_outside_window() -> None:
    moment = datetime(2026, 7, 11, 12, 0, tzinfo=UTC)
    assert is_within_quiet_hours(
        moment,
        quiet_start=time(22, 0),
        quiet_end=time(6, 0),
    ) is False


def test_notification_filter_respects_severity_and_cooldown() -> None:
    settings = Settings(
        app_env="testing",
        notifications_enabled=True,
        notify_min_severity="medium",
        notify_cooldown_seconds=300,
    )
    notification_filter = NotificationFilter(settings)
    low_event = _event(severity="low")
    medium_event = _event(severity="medium")

    assert notification_filter.should_notify(low_event) is False
    assert notification_filter.should_notify(medium_event) is True

    notification_filter.record_sent(medium_event)
    assert notification_filter.should_notify(medium_event) is False


def test_notification_filter_event_type_whitelist() -> None:
    settings = Settings(
        app_env="testing",
        notifications_enabled=True,
        notify_event_types="crowd_detected",
    )
    notification_filter = NotificationFilter(settings)

    assert notification_filter.should_notify(_event(event_type="crowd_detected")) is True
    assert notification_filter.should_notify(_event(event_type="animal_detected")) is False


def test_notification_filter_photo_threshold() -> None:
    settings = Settings(
        app_env="testing",
        notifications_enabled=True,
        notify_photo_min_severity="high",
    )
    notification_filter = NotificationFilter(settings)

    assert notification_filter.should_include_photo(_event(severity="medium")) is False
    assert notification_filter.should_include_photo(_event(severity="high")) is True
