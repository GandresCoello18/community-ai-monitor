from datetime import UTC, datetime
from uuid import uuid4

import pytest
from sqlalchemy import func, select

from app.capture.base import Frame
from app.core.config import Settings
from app.database.session import get_session_factory
from app.detection.base import BoundingBox
from app.events.engine import EventEngine
from app.events.factory import create_event_engine
from app.events.rules.crowd_detection import CrowdDetectionRule
from app.models import Event
from app.services.event_ingestion_service import EventIngestionService
from app.tracking.base import TrackedDetection

CAMERA_ID = uuid4()
BASE_TIME = datetime(2026, 7, 10, 16, 0, 0, tzinfo=UTC)


def _person(track_id: int) -> TrackedDetection:
    return TrackedDetection(
        track_id=track_id,
        object_class="person",
        confidence=0.9,
        bbox=BoundingBox(x=10, y=10, width=50, height=100),
    )


def test_event_engine_runs_multiple_rules() -> None:
    engine = EventEngine(
        CAMERA_ID,
        [
            CrowdDetectionRule(people_threshold=2, cooldown_seconds=0),
        ],
    )
    tracked = [_person(1), _person(2), _person(3)]

    events = engine.process(tracked, BASE_TIME)

    assert len(events) == 1
    assert events[0].event_type == "crowd_detected"


def test_create_event_engine_respects_disabled_rules() -> None:
    settings = Settings(
        app_env="testing",
        rule_engine_enabled=False,
    )

    engine = create_event_engine(CAMERA_ID, settings)

    assert engine.rule_names == []


@pytest.mark.asyncio
async def test_event_ingestion_service_persists_events(
    test_settings: Settings,
    app,
) -> None:
    settings = test_settings.model_copy(
        update={
            "rule_engine_enabled": True,
            "event_persist_enabled": True,
            "rule_crowd_threshold": 2,
            "event_cooldown_seconds": 0,
            "event_crowd_enabled": True,
            "event_high_density_enabled": False,
            "event_long_presence_enabled": False,
            "event_abandoned_object_enabled": False,
            "rule_person_repeated_activity_enabled": False,
            "rule_person_hidden_activity_enabled": False,
            "rule_vehicle_long_parking_enabled": False,
            "rule_double_parking_enabled": False,
            "rule_park_occupancy_enabled": False,
            "rule_park_empty_enabled": False,
            "rule_animal_enabled": False,
            "rule_metrics_enabled": False,
        }
    )
    session_factory = get_session_factory(settings)
    async with session_factory() as session:
        from app.models import Camera

        session.add(
            Camera(
                id=CAMERA_ID,
                name="Test Camera",
                location="Test",
                stream_url="webcam://0",
                is_active=True,
            )
        )
        await session.commit()

    service = EventIngestionService(settings)
    service.register_camera(CAMERA_ID)

    frame = Frame(
        camera_id=CAMERA_ID,
        frame_number=1,
        captured_at=BASE_TIME,
        width=640,
        height=480,
        image=None,
    )
    tracked = [_person(1), _person(2)]

    created = await service.process_detections(CAMERA_ID, tracked, frame)

    assert created == 1

    async with session_factory() as session:
        count = await session.scalar(select(func.count()).select_from(Event))
        assert int(count or 0) == 1
