import logging
from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Camera, Configuration, Detection, Event
from app.repositories.seed_repository import SeedRepository

logger = logging.getLogger(__name__)


async def seed_demo_data(session: AsyncSession) -> None:
    """Insert simulated data when the database is empty."""
    repository = SeedRepository(session)

    if await repository.has_cameras():
        logger.info("Demo data already present, skipping seed")
        return

    now = datetime.now(UTC)

    camera_entrance = Camera(
        name="Camera Entrada Principal",
        location="Parque Central - Entrada Norte",
        stream_url="rtsp://demo/camera-01",
        is_active=True,
    )
    camera_park = Camera(
        name="Camera Zona Recreativa",
        location="Parque Central - Área de juegos",
        stream_url="rtsp://demo/camera-02",
        is_active=True,
    )

    await repository.add_camera(camera_entrance)
    await repository.add_camera(camera_park)
    await session.flush()

    await repository.add_detection(
        Detection(
            camera_id=camera_entrance.id,
            object_class="person",
            confidence=0.91,
            bbox={"x": 120, "y": 80, "width": 60, "height": 140},
            detected_at=now - timedelta(minutes=5),
            metadata_={"zone": "entry"},
            created_at=now - timedelta(minutes=5),
        )
    )
    await repository.add_detection(
        Detection(
            camera_id=camera_park.id,
            object_class="person",
            confidence=0.87,
            bbox={"x": 300, "y": 150, "width": 55, "height": 130},
            detected_at=now - timedelta(minutes=2),
            metadata_={"zone": "playground"},
            created_at=now - timedelta(minutes=2),
        )
    )

    await repository.add_event(
        Event(
            camera_id=camera_entrance.id,
            event_type="long_presence",
            severity="medium",
            occurred_at=now - timedelta(minutes=10),
            started_at=now - timedelta(minutes=40),
            ended_at=now - timedelta(minutes=10),
            metadata_={"duration_seconds": 1800, "object_class": "person"},
        )
    )
    await repository.add_event(
        Event(
            camera_id=camera_park.id,
            event_type="crowd_detected",
            severity="low",
            occurred_at=now - timedelta(minutes=3),
            metadata_={"people_count": 8, "threshold": 5},
        )
    )

    await repository.add_configuration(
        Configuration(
            key="detection.confidence_threshold",
            value={"min_confidence": 0.75},
            description="Minimum confidence for object detection",
        )
    )
    await repository.add_configuration(
        Configuration(
            key="events.crowd_threshold",
            value={"people_count": 5},
            description="People count threshold for crowd events",
        )
    )

    await session.commit()
    logger.info("Demo data seeded successfully")
