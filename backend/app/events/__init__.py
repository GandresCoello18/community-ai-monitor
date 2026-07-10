"""Event processing layer (FASE 6).

Flow: tracked detections → rules → EventCandidate → persistence (service).
"""

from app.events.base import EventCandidate, EventRule, RuleContext
from app.events.engine import EventEngine
from app.events.factory import create_event_engine

__all__ = [
    "EventCandidate",
    "EventEngine",
    "EventRule",
    "RuleContext",
    "create_event_engine",
]
