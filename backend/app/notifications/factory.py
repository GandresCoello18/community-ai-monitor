"""Factory for notification providers and services."""

from __future__ import annotations

import logging

from app.core.config import Settings
from app.notifications.filters import NotificationFilter
from app.notifications.service import NotificationService
from app.notifications.telegram import TelegramProvider

logger = logging.getLogger(__name__)


def create_notification_provider(settings: Settings) -> TelegramProvider | None:
    if not settings.notifications_enabled:
        return None

    provider_name = settings.notification_provider.strip().lower()
    if provider_name != "telegram":
        logger.warning(
            "Unsupported notification provider=%s; notifications disabled",
            provider_name,
        )
        return None

    token = settings.telegram_bot_token.strip()
    chat_id = settings.telegram_chat_id.strip()
    if not token or not chat_id:
        logger.warning(
            "Notifications enabled but TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID missing",
        )
        return None

    return TelegramProvider(
        token,
        chat_id,
        timeout_seconds=settings.notify_http_timeout_seconds,
    )


def create_notification_service(settings: Settings) -> NotificationService | None:
    provider = create_notification_provider(settings)
    if provider is None:
        return None

    return NotificationService(
        settings,
        provider,
        NotificationFilter(settings),
    )
