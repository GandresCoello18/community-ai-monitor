import asyncio
from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.core.config import Settings
from app.models import Event
from app.websocket.manager import WebSocketManager


class FakeWebSocket:
    def __init__(self) -> None:
        self.accepted = False
        self.messages: list[dict] = []

    async def accept(self) -> None:
        self.accepted = True

    async def send_json(self, data: dict) -> None:
        self.messages.append(data)


@pytest.fixture
def ws_settings() -> Settings:
    return Settings(app_env="testing", websocket_enabled=True)


@pytest.mark.asyncio
async def test_manager_broadcasts_event_to_dashboard_room(
    ws_settings: Settings,
) -> None:
    manager = WebSocketManager(ws_settings)
    fake_ws = FakeWebSocket()
    connection_id = await manager.connect(
        fake_ws,  # type: ignore[arg-type]
        camera_id=None,
    )

    event = Event(
        id=uuid4(),
        camera_id=uuid4(),
        event_type="crowd_detected",
        severity="low",
        occurred_at=datetime.now(UTC),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    await manager.publish_event_created(event)

    assert len(fake_ws.messages) == 1
    assert fake_ws.messages[0]["event"] == "event.created"
    await manager.disconnect(connection_id)


@pytest.mark.asyncio
async def test_manager_skips_broadcast_when_disabled(
    ws_settings: Settings,
) -> None:
    settings = ws_settings.model_copy(update={"websocket_enabled": False})
    manager = WebSocketManager(settings)
    fake_ws = FakeWebSocket()
    await manager.connect(fake_ws, camera_id=None)  # type: ignore[arg-type]

    event = Event(
        id=uuid4(),
        camera_id=uuid4(),
        event_type="long_presence",
        severity="medium",
        occurred_at=datetime.now(UTC),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    await manager.publish_event_created(event)

    assert fake_ws.messages == []


@pytest.mark.asyncio
async def test_camera_room_only_receives_matching_events(
    ws_settings: Settings,
) -> None:
    manager = WebSocketManager(ws_settings)
    camera_a = uuid4()
    camera_b = uuid4()

    ws_a = FakeWebSocket()
    ws_b = FakeWebSocket()
    await manager.connect(ws_a, camera_id=camera_a)  # type: ignore[arg-type]
    await manager.connect(ws_b, camera_id=camera_b)  # type: ignore[arg-type]

    event_a = Event(
        id=uuid4(),
        camera_id=camera_a,
        event_type="crowd_detected",
        severity="low",
        occurred_at=datetime.now(UTC),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    await manager.publish_event_created(event_a)
    await asyncio.sleep(0)

    assert len(ws_a.messages) == 1
    assert ws_b.messages == []
