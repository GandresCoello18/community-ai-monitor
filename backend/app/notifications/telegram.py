"""Telegram Bot API provider (sendMessage / sendPhoto)."""

from __future__ import annotations

import logging

import httpx

logger = logging.getLogger(__name__)


class TelegramNotificationError(Exception):
    """Raised when Telegram Bot API delivery fails."""


class TelegramProvider:
    """Async Telegram Bot API client using httpx."""

    def __init__(
        self,
        bot_token: str,
        chat_id: str,
        *,
        timeout_seconds: float = 30.0,
    ) -> None:
        if not bot_token.strip():
            msg = "Telegram bot token is required"
            raise ValueError(msg)
        if not chat_id.strip():
            msg = "Telegram chat id is required"
            raise ValueError(msg)
        self._chat_id = chat_id.strip()
        self._timeout = timeout_seconds
        self._api_base = f"https://api.telegram.org/bot{bot_token.strip()}"

    @property
    def provider_name(self) -> str:
        return "telegram"

    async def send_message(self, text: str) -> None:
        await self._post_json(
            "sendMessage",
            {"chat_id": self._chat_id, "text": text},
        )

    async def send_photo(self, photo: bytes, *, caption: str) -> None:
        await self._post_multipart(
            "sendPhoto",
            data={"chat_id": self._chat_id, "caption": caption},
            files={"photo": ("alert.jpg", photo, "image/jpeg")},
        )

    async def _post_json(self, method: str, payload: dict[str, str]) -> None:
        url = f"{self._api_base}/{method}"
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            logger.error(
                "Telegram %s failed with HTTP %s",
                method,
                exc.response.status_code,
            )
            raise TelegramNotificationError(
                f"Telegram {method} returned HTTP {exc.response.status_code}",
            ) from exc
        except httpx.HTTPError as exc:
            logger.error("Telegram %s request failed: %s", method, type(exc).__name__)
            raise TelegramNotificationError(
                f"Telegram {method} request failed",
            ) from exc

    async def _post_multipart(
        self,
        method: str,
        *,
        data: dict[str, str],
        files: dict[str, tuple[str, bytes, str]],
    ) -> None:
        url = f"{self._api_base}/{method}"
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(url, data=data, files=files)
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            logger.error(
                "Telegram %s failed with HTTP %s",
                method,
                exc.response.status_code,
            )
            raise TelegramNotificationError(
                f"Telegram {method} returned HTTP {exc.response.status_code}",
            ) from exc
        except httpx.HTTPError as exc:
            logger.error("Telegram %s request failed: %s", method, type(exc).__name__)
            raise TelegramNotificationError(
                f"Telegram {method} request failed",
            ) from exc
