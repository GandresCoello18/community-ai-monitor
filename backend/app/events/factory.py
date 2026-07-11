from uuid import UUID

from app.core.config import Settings
from app.events.engine import EventEngine
from app.rules.factory import build_rules


def create_event_engine(camera_id: UUID, settings: Settings) -> EventEngine:
    return EventEngine(camera_id, build_rules(settings))  # type: ignore[arg-type]
