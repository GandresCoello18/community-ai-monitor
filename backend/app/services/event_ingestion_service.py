import logging
from datetime import UTC, datetime
from uuid import UUID

from app.capture.base import Frame
from app.core.config import Settings
from app.events.base import EventCandidate
from app.events.engine import EventEngine
from app.events.factory import create_event_engine
from app.models import Event
from app.repositories.event_repository import EventRepository
from app.tracking.base import TrackedDetection
from app.websocket.manager import WebSocketManager

logger = logging.getLogger(__name__)


class EventIngestionService:
    """Evaluates event rules, persists events and broadcasts via WebSocket."""

    def __init__(
        self,
        settings: Settings,
        ws_manager: WebSocketManager | None = None,
    ) -> None:
        self._settings = settings
        self._ws_manager = ws_manager
        self._engines: dict[UUID, EventEngine] = {}

    def register_camera(self, camera_id: UUID) -> None:
        if camera_id in self._engines:
            return
        self._engines[camera_id] = create_event_engine(camera_id, self._settings)
        logger.info(
            "Event engine registered camera_id=%s rules=%s",
            camera_id,
            self._engines[camera_id].rule_names,
        )

    def unregister_camera(self, camera_id: UUID) -> None:
        engine = self._engines.pop(camera_id, None)
        if engine is not None:
            engine.reset()

    async def process_detections(
        self,
        camera_id: UUID,
        tracked: list[TrackedDetection],
        frame: Frame,
    ) -> int:
        if not self._settings.event_engine_enabled or not tracked:
            return 0

        engine = self._engines.get(camera_id)
        if engine is None:
            self.register_camera(camera_id)
            engine = self._engines[camera_id]

        candidates = engine.process(
            tracked,
            frame.captured_at,
            frame_width=frame.width,
            frame_height=frame.height,
        )
        if not candidates:
            return 0

        if not self._settings.event_persist_enabled:
            return len(candidates)

        await self._persist_events(camera_id, candidates)
        return len(candidates)

    async def _persist_events(
        self,
        camera_id: UUID,
        candidates: list[EventCandidate],
    ) -> None:
        from app.database.session import get_session_factory  # noqa: PLC0415

        session_factory = get_session_factory(self._settings)
        now = datetime.now(UTC)
        persisted: list[Event] = []
        try:
            async with session_factory() as session:
                repository = EventRepository(session)
                persisted = [
                    Event(
                        camera_id=camera_id,
                        event_type=candidate.event_type,
                        severity=candidate.severity,
                        occurred_at=candidate.occurred_at,
                        started_at=candidate.started_at,
                        ended_at=candidate.ended_at,
                        metadata_=candidate.metadata,
                        created_at=now,
                        updated_at=now,
                    )
                    for candidate in candidates
                ]
                repository.add_many(persisted)
                await session.flush()
                await session.commit()
                for event in persisted:
                    logger.info(
                        "Event created camera_id=%s type=%s severity=%s",
                        camera_id,
                        event.event_type,
                        event.severity,
                    )
        except Exception:
            logger.exception(
                "Failed to persist events camera_id=%s count=%d",
                camera_id,
                len(candidates),
            )
            return

        if self._ws_manager is not None:
            for event in persisted:
                await self._ws_manager.publish_event_created(event)
