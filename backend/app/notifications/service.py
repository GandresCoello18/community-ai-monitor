"""Notification orchestration for persisted events."""

from __future__ import annotations

import logging

from app.capture.base import Frame
from app.capture.preview import encode_preview_jpeg
from app.core.config import Settings
from app.models import Event
from app.notifications.base import NotificationProvider
from app.notifications.filters import NotificationFilter
from app.notifications.messages import format_event_alert_message
from app.tracking.base import TrackedDetection

logger = logging.getLogger(__name__)


class NotificationService:
    """Evaluates filters and delivers alerts through the configured provider."""

    def __init__(
        self,
        settings: Settings,
        provider: NotificationProvider,
        notification_filter: NotificationFilter,
    ) -> None:
        self._settings = settings
        self._provider = provider
        self._filter = notification_filter

    @property
    def provider_name(self) -> str:
        return self._provider.provider_name

    async def notify_events(
        self,
        events: list[Event],
        *,
        camera_name: str,
        camera_location: str,
        frame: Frame | None = None,
        tracked: list[TrackedDetection] | None = None,
    ) -> int:
        if not events or not self._settings.notifications_enabled:
            return 0

        sent_count = 0
        for event in events:
            if not self._filter.should_notify(event):
                continue

            message = format_event_alert_message(
                event,
                camera_name=camera_name,
                camera_location=camera_location,
            )

            try:
                if self._should_send_photo(event, frame):
                    jpeg = self._encode_alert_photo(frame, tracked)
                    if jpeg is not None:
                        await self._provider.send_photo(jpeg, caption=message)
                    else:
                        await self._provider.send_message(message)
                else:
                    await self._provider.send_message(message)

                self._filter.record_sent(event)
                sent_count += 1
                logger.info(
                    "Notification sent provider=%s camera_id=%s event_type=%s severity=%s",
                    self._provider.provider_name,
                    event.camera_id,
                    event.event_type,
                    event.severity,
                )
            except Exception:
                logger.exception(
                    "Failed to send notification camera_id=%s event_type=%s",
                    event.camera_id,
                    event.event_type,
                )

        return sent_count

    def _should_send_photo(
        self,
        event: Event,
        frame: Frame | None,
    ) -> bool:
        if frame is None or frame.image is None:
            return False
        return self._filter.should_include_photo(event)

    def _encode_alert_photo(
        self,
        frame: Frame | None,
        tracked: list[TrackedDetection] | None,
    ) -> bytes | None:
        if frame is None or frame.image is None:
            return None
        return encode_preview_jpeg(
            frame.image,
            max_width=self._settings.notify_alert_jpeg_max_width,
            jpeg_quality=self._settings.notify_alert_jpeg_quality,
            tracked=tracked,
            draw_detections=True,
        )
