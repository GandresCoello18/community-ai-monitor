import asyncio
from datetime import UTC, datetime
from uuid import uuid4

from starlette.testclient import TestClient

from app.core.config import Settings
from app.main import create_app
from app.models import Event


def test_websocket_endpoint_receives_event_created() -> None:
    settings = Settings(app_env="testing", websocket_enabled=True)
    app = create_app(settings)

    event = Event(
        id=uuid4(),
        camera_id=uuid4(),
        event_type="crowd_detected",
        severity="low",
        occurred_at=datetime.now(UTC),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    with (
        TestClient(app) as client,
        client.websocket_connect("/api/v1/ws/events") as ws,
    ):
        hello = ws.receive_json()
        assert hello["event"] == "connection.established"
        assert hello["data"]["rooms"] == ["dashboard:global"]

        asyncio.run(app.state.ws_manager.publish_event_created(event))

        payload = ws.receive_json()
        assert payload["event"] == "event.created"
        assert payload["data"]["event_type"] == "crowd_detected"

        ws.send_text("ping")
