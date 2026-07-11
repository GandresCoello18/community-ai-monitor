from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID

from app.tracking.base import TrackedDetection


@dataclass(frozen=True, slots=True)
class EventCandidate:
    """Structured event produced by a rule, before persistence."""

    event_type: str
    severity: str
    occurred_at: datetime
    started_at: datetime | None = None
    ended_at: datetime | None = None
    metadata: dict | None = None
    rule_name: str | None = None


@dataclass(frozen=True, slots=True)
class RuleContext:
    """Input snapshot for a single evaluation tick."""

    camera_id: UUID
    occurred_at: datetime
    tracked_detections: list[TrackedDetection]
    frame_width: int = 640
    frame_height: int = 480
    scene_type: str = "general"


class RuleProtocol(Protocol):
    """Interface for independent, stateful community rules."""

    @property
    def rule_name(self) -> str: ...

    @property
    def is_placeholder(self) -> bool: ...

    def evaluate(self, context: RuleContext) -> list[EventCandidate]: ...

    def collect_metrics(self, context: RuleContext) -> list["MetricSample"]: ...

    def reset(self) -> None: ...


@dataclass(frozen=True, slots=True)
class MetricSample:
    """Point-in-time or bucketed metric emitted by the rule engine."""

    metric_type: str
    value: float
    bucket_start: datetime
    metadata: dict | None = None
