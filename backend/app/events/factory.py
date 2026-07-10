from uuid import UUID

from app.core.config import Settings
from app.events.engine import EventEngine
from app.events.rules.abandoned_object import AbandonedObjectRule
from app.events.rules.crowd_detection import CrowdDetectionRule
from app.events.rules.high_density import HighDensityRule
from app.events.rules.long_presence import LongPresenceRule


def create_event_engine(camera_id: UUID, settings: Settings) -> EventEngine:
    """Build a per-camera event engine from application settings."""
    rules = []

    if settings.event_crowd_enabled:
        rules.append(
            CrowdDetectionRule(
                people_threshold=settings.event_crowd_people_threshold,
                cooldown_seconds=settings.event_cooldown_seconds,
            )
        )

    if settings.event_high_density_enabled:
        rules.append(
            HighDensityRule(
                min_people=settings.event_high_density_min_people,
                density_threshold=settings.event_high_density_threshold,
                cooldown_seconds=settings.event_cooldown_seconds,
            )
        )

    if settings.event_long_presence_enabled:
        rules.append(
            LongPresenceRule(
                duration_seconds=settings.event_long_presence_seconds,
                target_classes=settings.event_long_presence_class_set,
            )
        )

    if settings.event_abandoned_object_enabled:
        rules.append(
            AbandonedObjectRule(
                duration_seconds=settings.event_abandoned_duration_seconds,
                movement_threshold=settings.event_abandoned_movement_threshold,
                target_classes=settings.event_abandoned_class_set,
            )
        )

    return EventEngine(camera_id, rules)
