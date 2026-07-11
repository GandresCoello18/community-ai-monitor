"""Notification eligibility filters (severity, types, cooldown, quiet hours)."""

from __future__ import annotations

from datetime import UTC, datetime, time
from uuid import UUID

from app.core.config import Settings
from app.models import Event

SEVERITY_RANK: dict[str, int] = {
    "low": 0,
    "medium": 1,
    "high": 2,
    "critical": 3,
}


def severity_rank(severity: str) -> int:
    return SEVERITY_RANK.get(severity.strip().lower(), -1)


def meets_min_severity(severity: str, minimum: str) -> bool:
    return severity_rank(severity) >= severity_rank(minimum)


def parse_hh_mm(value: str) -> time | None:
    normalized = value.strip()
    if not normalized:
        return None
    parts = normalized.split(":")
    if len(parts) != 2:
        return None
    try:
        hour = int(parts[0])
        minute = int(parts[1])
    except ValueError:
        return None
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        return None
    return time(hour=hour, minute=minute)


def is_within_quiet_hours(
    moment: datetime,
    *,
    quiet_start: time | None,
    quiet_end: time | None,
) -> bool:
    """Return True when notifications should be suppressed."""
    if quiet_start is None or quiet_end is None:
        return False

    current = moment.astimezone(UTC).time()
    if quiet_start <= quiet_end:
        return quiet_start <= current <= quiet_end
    return current >= quiet_start or current <= quiet_end


class NotificationFilter:
    """In-memory filter with cooldown tracking per camera and event type."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._last_sent: dict[tuple[UUID, str], datetime] = {}
        self._quiet_start = parse_hh_mm(settings.notify_quiet_hours_start)
        self._quiet_end = parse_hh_mm(settings.notify_quiet_hours_end)

    def should_notify(self, event: Event, *, now: datetime | None = None) -> bool:
        if not self._settings.notifications_enabled:
            return False

        if not meets_min_severity(event.severity, self._settings.notify_min_severity):
            return False

        allowed_types = self._settings.notify_event_type_set
        if allowed_types and event.event_type not in allowed_types:
            return False

        moment = now or datetime.now(UTC)
        if is_within_quiet_hours(
            moment,
            quiet_start=self._quiet_start,
            quiet_end=self._quiet_end,
        ):
            return False

        key = (event.camera_id, event.event_type)
        last_sent = self._last_sent.get(key)
        if last_sent is not None:
            elapsed = (moment - last_sent).total_seconds()
            if elapsed < self._settings.notify_cooldown_seconds:
                return False

        return True

    def should_include_photo(self, event: Event) -> bool:
        return meets_min_severity(
            event.severity,
            self._settings.notify_photo_min_severity,
        )

    def record_sent(
        self,
        event: Event,
        *,
        now: datetime | None = None,
    ) -> None:
        moment = now or datetime.now(UTC)
        self._last_sent[(event.camera_id, event.event_type)] = moment

    def clear(self) -> None:
        self._last_sent.clear()
