from datetime import UTC, datetime
from uuid import uuid4

from app.models import Event
from app.websocket.schemas import build_event_created_message


def test_event_created_message_follows_contract() -> None:
    event_id = uuid4()
    camera_id = uuid4()
    occurred = datetime(2026, 7, 10, 15, 30, 0, tzinfo=UTC)

    event = Event(
        id=event_id,
        camera_id=camera_id,
        event_type="crowd_detected",
        severity="low",
        occurred_at=occurred,
        metadata_={"people_count": 8},
        created_at=occurred,
        updated_at=occurred,
    )

    message = build_event_created_message(event)

    assert message["event"] == "event.created"
    assert "timestamp" in message
    assert message["data"]["id"] == str(event_id)
    assert message["data"]["camera_id"] == str(camera_id)
    assert message["data"]["event_type"] == "crowd_detected"
    assert message["data"]["metadata"]["people_count"] == 8
