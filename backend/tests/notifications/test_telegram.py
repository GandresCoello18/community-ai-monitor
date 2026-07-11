from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.notifications.telegram import TelegramProvider


@pytest.mark.asyncio
async def test_telegram_send_message_calls_bot_api() -> None:
    provider = TelegramProvider("test-token", "-100123456")

    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    with patch("app.notifications.telegram.httpx.AsyncClient", return_value=mock_client):
        await provider.send_message("Alerta de prueba")

    mock_client.post.assert_called_once()
    url, kwargs = mock_client.post.call_args[0][0], mock_client.post.call_args[1]
    assert url.endswith("/sendMessage")
    assert kwargs["json"]["chat_id"] == "-100123456"
    assert kwargs["json"]["text"] == "Alerta de prueba"


@pytest.mark.asyncio
async def test_telegram_send_photo_uses_multipart() -> None:
    provider = TelegramProvider("test-token", "-100123456")

    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    with patch("app.notifications.telegram.httpx.AsyncClient", return_value=mock_client):
        await provider.send_photo(b"jpeg-bytes", caption="Foto de alerta")

    mock_client.post.assert_called_once()
    url, kwargs = mock_client.post.call_args[0][0], mock_client.post.call_args[1]
    assert url.endswith("/sendPhoto")
    assert kwargs["data"]["chat_id"] == "-100123456"
    assert kwargs["data"]["caption"] == "Foto de alerta"
    assert kwargs["files"]["photo"][0] == "alert.jpg"
