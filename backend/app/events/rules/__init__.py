"""Independent event rules (FASE 6)."""

from app.events.rules.abandoned_object import AbandonedObjectRule
from app.events.rules.crowd_detection import CrowdDetectionRule
from app.events.rules.high_density import HighDensityRule
from app.events.rules.long_presence import LongPresenceRule

__all__ = [
    "AbandonedObjectRule",
    "CrowdDetectionRule",
    "HighDensityRule",
    "LongPresenceRule",
]
