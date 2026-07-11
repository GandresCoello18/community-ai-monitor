from app.core.config import Settings
from app.notifications.factory import create_notification_provider, create_notification_service


def test_create_notification_provider_disabled() -> None:
    settings = Settings(app_env="testing", notifications_enabled=False)
    assert create_notification_provider(settings) is None
    assert create_notification_service(settings) is None


def test_create_notification_provider_requires_credentials() -> None:
    settings = Settings(
        app_env="testing",
        notifications_enabled=True,
        telegram_bot_token="",
        telegram_chat_id="",
    )
    assert create_notification_provider(settings) is None


def test_create_notification_service_with_credentials() -> None:
    settings = Settings(
        app_env="testing",
        notifications_enabled=True,
        telegram_bot_token="123:abc",
        telegram_chat_id="-100999",
    )
    service = create_notification_service(settings)
    assert service is not None
    assert service.provider_name == "telegram"
