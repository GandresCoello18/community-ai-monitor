from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID

from app.tracking.base import TrackedDetection


@dataclass(frozen=True, slots=True)
class EventCandidate:
    """Structured event produced by a rule, before persistence.

    This is the contract between event rules and the ingestion service. Rules
    never touch the database directly.
    """

    event_type: str
    severity: str
    occurred_at: datetime
    started_at: datetime | None = None
    ended_at: datetime | None = None
    metadata: dict | None = None


@dataclass(frozen=True, slots=True)
class RuleContext:
    """Input snapshot for a single evaluation tick."""

    camera_id: UUID
    occurred_at: datetime
    tracked_detections: list[TrackedDetection]
    frame_width: int = 640
    frame_height: int = 480


class EventRule(Protocol):
    """Interface for independent, stateful event rules."""

    @property
    def rule_name(self) -> str: ...

    def evaluate(self, context: RuleContext) -> list[EventCandidate]: ...

    def reset(self) -> None: ...
