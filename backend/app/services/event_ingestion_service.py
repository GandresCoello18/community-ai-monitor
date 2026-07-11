import logging
from datetime import UTC, datetime
from uuid import UUID

from app.capture.base import Frame
from app.core.config import Settings
from app.models import Event
from app.repositories.event_repository import EventRepository
from app.rules.engine import RuleEngine
from app.rules.factory import create_rule_engine
from app.tracking.base import TrackedDetection
from app.websocket.manager import WebSocketManager

logger = logging.getLogger(__name__)


class EventIngestionService:
    """Evaluates community rules, persists events/metrics and broadcasts via WS."""

    def __init__(
        self,
        settings: Settings,
        ws_manager: WebSocketManager | None = None,
    ) -> None:
        self._settings = settings
        self._ws_manager = ws_manager
        self._engines: dict[UUID, RuleEngine] = {}

    def register_camera(self, camera_id: UUID) -> None:
        if camera_id in self._engines:
            return
        self._engines[camera_id] = create_rule_engine(camera_id, self._settings)
        logger.info(
            "Rule engine registered camera_id=%s rules=%s",
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
        if (
            not self._settings.rule_engine_enabled
            or not self._settings.event_engine_enabled
            or not tracked
        ):
            return 0

        engine = self._engines.get(camera_id)
        if engine is None:
            self.register_camera(camera_id)
            engine = self._engines[camera_id]

        result = engine.process(
            tracked,
            frame.captured_at,
            frame_width=frame.width,
            frame_height=frame.height,
            scene_type=self._settings.rule_scene_type,
        )

        if self._settings.rule_metrics_enabled and result.metrics:
            await self._persist_metrics(camera_id, result.metrics)

        if not result.events:
            return 0

        if not self._settings.event_persist_enabled:
            return len(result.events)

        await self._persist_events(camera_id, result.events)
        return len(result.events)

    async def _persist_events(
        self,
        camera_id: UUID,
        candidates: list,
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
                        metadata_={
                            **(candidate.metadata or {}),
                            **(
                                {"rule_name": candidate.rule_name}
                                if getattr(candidate, "rule_name", None)
                                else {}
                            ),
                        },
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

    async def _persist_metrics(self, camera_id: UUID, samples: list) -> None:
        from app.database.session import get_session_factory  # noqa: PLC0415
        from app.models import CommunityMetric  # noqa: PLC0415
        from app.repositories.metrics_repository import MetricsRepository  # noqa: PLC0415

        session_factory = get_session_factory(self._settings)
        now = datetime.now(UTC)
        try:
            async with session_factory() as session:
                repository = MetricsRepository(session)
                await repository.upsert_many(
                    [
                        CommunityMetric(
                            camera_id=camera_id,
                            metric_type=sample.metric_type,
                            bucket_start=sample.bucket_start,
                            value=sample.value,
                            metadata_=sample.metadata,
                            created_at=now,
                            updated_at=now,
                        )
                        for sample in samples
                    ]
                )
                await session.commit()
        except Exception:
            logger.exception(
                "Failed to persist metrics camera_id=%s count=%d",
                camera_id,
                len(samples),
            )
