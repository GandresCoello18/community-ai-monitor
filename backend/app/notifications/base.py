"""Notification channel adapters."""

from typing import Protocol


class NotificationProvider(Protocol):
    """Adapter interface for outbound alert channels (Telegram, etc.)."""

    @property
    def provider_name(self) -> str: ...

    async def send_message(self, text: str) -> None: ...

    async def send_photo(self, photo: bytes, *, caption: str) -> None: ...
