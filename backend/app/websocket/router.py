import logging
from uuid import UUID

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.websocket.manager import WebSocketManager
from app.websocket.schemas import build_connection_established_message

logger = logging.getLogger(__name__)

router = APIRouter(tags=["websocket"])


def _get_manager(websocket: WebSocket) -> WebSocketManager:
    manager = getattr(websocket.app.state, "ws_manager", None)
    if manager is None:
        msg = "WebSocket manager is not initialized"
        raise RuntimeError(msg)
    return manager


@router.websocket("/events")
async def websocket_events(
    websocket: WebSocket,
    camera_id: UUID | None = Query(default=None),
) -> None:
    """Real-time event stream.

    Subscribe to all events (dashboard) or filter by ``camera_id``:

    - ``/api/v1/ws/events`` → room ``dashboard:global``
    - ``/api/v1/ws/events?camera_id={uuid}`` → room ``camera:{uuid}``
    """
    manager = _get_manager(websocket)
    connection_id = await manager.connect(websocket, camera_id=camera_id)

    rooms = (
        [f"camera:{camera_id}"]
        if camera_id is not None
        else ["dashboard:global"]
    )
    await websocket.send_json(build_connection_established_message(rooms))

    try:
        while True:
            # Keep the connection alive; clients may send ping messages.
            await websocket.receive_text()
    except WebSocketDisconnect:
        logger.debug("WebSocket client disconnected id=%s", connection_id)
    finally:
        await manager.disconnect(connection_id)
