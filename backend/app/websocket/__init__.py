"""Real-time WebSocket layer (FASE 9)."""

from app.websocket.manager import DASHBOARD_ROOM, WebSocketManager
from app.websocket.schemas import WebSocketMessage, build_event_created_message

__all__ = [
    "DASHBOARD_ROOM",
    "WebSocketManager",
    "WebSocketMessage",
    "build_event_created_message",
]
