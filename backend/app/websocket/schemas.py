from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


class WebSocketMessage(BaseModel):
    """Standard WebSocket envelope (entity.action + timestamp + data)."""

    event: str = Field(examples=["event.created"])
    timestamp: datetime
    data: dict[str, Any]


def build_connection_established_message(rooms: list[str]) -> dict[str, Any]:
    return WebSocketMessage(
        event="connection.established",
        timestamp=datetime.now(UTC),
        data={"rooms": rooms},
    ).model_dump(mode="json")


def build_event_created_message(event: Any) -> dict[str, Any]:
    """Build event.created payload from a persisted Event model."""
    return WebSocketMessage(
        event="event.created",
        timestamp=datetime.now(UTC),
        data={
            "id": str(event.id),
            "camera_id": str(event.camera_id),
            "event_type": event.event_type,
            "severity": event.severity,
            "occurred_at": event.occurred_at.isoformat(),
            "started_at": event.started_at.isoformat() if event.started_at else None,
            "ended_at": event.ended_at.isoformat() if event.ended_at else None,
            "metadata": event.metadata_,
        },
    ).model_dump(mode="json")
