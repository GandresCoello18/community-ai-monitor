from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import numpy as np
import pytest

from app.capture.base import Frame
from app.core.config import Settings
from app.detection.base import BoundingBox
from app.models import Event
from app.notifications.filters import NotificationFilter
from app.notifications.service import NotificationService
from app.tracking.base import TrackedDetection


class FakeProvider:
    provider_name = "fake"

    def __init__(self) -> None:
        self.messages: list[str] = []
        self.photos: list[tuple[bytes, str]] = []

    async def send_message(self, text: str) -> None:
        self.messages.append(text)

    async def send_photo(self, photo: bytes, *, caption: str) -> None:
        self.photos.append((photo, caption))


def _event(severity: str = "high") -> Event:
    now = datetime(2026, 7, 11, 14, 30, tzinfo=UTC)
    return Event(
        id=uuid4(),
        camera_id=uuid4(),
        event_type="crowd_detected",
        severity=severity,
        occurred_at=now,
        started_at=None,
        ended_at=None,
        metadata_=None,
        created_at=now,
        updated_at=now,
    )


@pytest.mark.asyncio
async def test_notification_service_sends_text_for_medium_severity() -> None:
    settings = Settings(
        app_env="testing",
        notifications_enabled=True,
        notify_min_severity="medium",
        notify_photo_min_severity="high",
        notify_cooldown_seconds=0,
    )
    provider = FakeProvider()
    service = NotificationService(settings, provider, NotificationFilter(settings))

    sent = await service.notify_events(
        [_event(severity="medium")],
        camera_name="Entrada Norte",
        camera_location="Parque Central",
    )

    assert sent == 1
    assert len(provider.messages) == 1
    assert "Parque Central" in provider.messages[0]
    assert "Posible aglomeración" in provider.messages[0]
    assert provider.photos == []


@pytest.mark.asyncio
async def test_notification_service_sends_photo_for_high_severity() -> None:
    settings = Settings(
        app_env="testing",
        notifications_enabled=True,
        notify_min_severity="medium",
        notify_photo_min_severity="high",
        notify_cooldown_seconds=0,
        notify_alert_jpeg_max_width=320,
        notify_alert_jpeg_quality=80,
    )
    provider = FakeProvider()
    service = NotificationService(settings, provider, NotificationFilter(settings))

    camera_id = uuid4()
    frame = Frame(
        camera_id=camera_id,
        frame_number=1,
        captured_at=datetime.now(UTC),
        width=640,
        height=480,
        image=np.zeros((480, 640, 3), dtype=np.uint8),
    )
    tracked = [
        TrackedDetection(
            track_id=1,
            object_class="person",
            confidence=0.9,
            bbox=BoundingBox(x=10, y=10, width=40, height=80),
        )
    ]

    sent = await service.notify_events(
        [_event(severity="high")],
        camera_name="Entrada Norte",
        camera_location="Parque Central",
        frame=frame,
        tracked=tracked,
    )

    assert sent == 1
    assert provider.messages == []
    assert len(provider.photos) == 1
    assert provider.photos[0][1].startswith("⚠️ Alerta")


@pytest.mark.asyncio
async def test_notification_service_skips_when_filter_rejects() -> None:
    settings = Settings(
        app_env="testing",
        notifications_enabled=True,
        notify_min_severity="high",
    )
    provider = FakeProvider()
    service = NotificationService(settings, provider, NotificationFilter(settings))

    sent = await service.notify_events(
        [_event(severity="low")],
        camera_name="Cam",
        camera_location="Loc",
    )

    assert sent == 0
    assert provider.messages == []


@pytest.mark.asyncio
async def test_notification_service_continues_after_provider_error() -> None:
    settings = Settings(
        app_env="testing",
        notifications_enabled=True,
        notify_min_severity="medium",
        notify_cooldown_seconds=0,
    )
    provider = FakeProvider()
    provider.send_message = AsyncMock(side_effect=RuntimeError("network down"))
    service = NotificationService(settings, provider, NotificationFilter(settings))

    sent = await service.notify_events(
        [_event(severity="medium")],
        camera_name="Cam",
        camera_location="Loc",
    )

    assert sent == 0
