import asyncio
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from uuid import UUID, uuid4

from fastapi import WebSocket

from app.core.config import Settings
from app.models import Event
from app.websocket.schemas import build_event_created_message

logger = logging.getLogger(__name__)

DASHBOARD_ROOM = "dashboard:global"


@dataclass
class ClientConnection:
    websocket: WebSocket
    rooms: set[str] = field(default_factory=set)


class WebSocketManager:
    """Manages WebSocket connections and room-based broadcasting.

    Rooms follow the ``entity:context`` convention from the API contract:
    - ``dashboard:global`` — all events (admin dashboard).
    - ``camera:{uuid}`` — events for one camera only.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._connections: dict[str, ClientConnection] = {}
        self._rooms: dict[str, set[str]] = defaultdict(set)
        self._lock = asyncio.Lock()

    @property
    def active_connections(self) -> int:
        return len(self._connections)

    def _resolve_rooms(self, camera_id: UUID | None) -> set[str]:
        if camera_id is not None:
            return {f"camera:{camera_id}"}
        return {DASHBOARD_ROOM}

    async def connect(
        self,
        websocket: WebSocket,
        *,
        camera_id: UUID | None = None,
    ) -> str:
        await websocket.accept()
        connection_id = str(uuid4())
        rooms = self._resolve_rooms(camera_id)

        async with self._lock:
            self._connections[connection_id] = ClientConnection(
                websocket=websocket,
                rooms=rooms,
            )
            for room in rooms:
                self._rooms[room].add(connection_id)

        logger.info(
            "WebSocket connected id=%s rooms=%s total=%d",
            connection_id,
            sorted(rooms),
            len(self._connections),
        )
        return connection_id

    async def disconnect(self, connection_id: str) -> None:
        async with self._lock:
            connection = self._connections.pop(connection_id, None)
            if connection is None:
                return
            for room in connection.rooms:
                self._rooms[room].discard(connection_id)
                if not self._rooms[room]:
                    del self._rooms[room]

        logger.info(
            "WebSocket disconnected id=%s total=%d",
            connection_id,
            len(self._connections),
        )

    async def publish_event_created(self, event: Event) -> None:
        if not self._settings.websocket_enabled:
            return
        if not self._connections:
            return

        message = build_event_created_message(event)
        camera_room = f"camera:{event.camera_id}"
        await self._broadcast_to_room(camera_room, message)
        if camera_room != DASHBOARD_ROOM:
            await self._broadcast_to_room(DASHBOARD_ROOM, message)

    async def _broadcast_to_room(self, room: str, message: dict) -> None:
        async with self._lock:
            connection_ids = list(self._rooms.get(room, set()))

        stale: list[str] = []
        for connection_id in connection_ids:
            connection = self._connections.get(connection_id)
            if connection is None:
                stale.append(connection_id)
                continue
            try:
                await connection.websocket.send_json(message)
            except Exception:
                logger.warning(
                    "WebSocket send failed id=%s room=%s",
                    connection_id,
                    room,
                )
                stale.append(connection_id)

        for connection_id in stale:
            await self.disconnect(connection_id)
