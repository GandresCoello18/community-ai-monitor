from datetime import datetime

from pydantic import BaseModel


class EventSummaryItem(BaseModel):
    """One event as exposed to the LLM (structured metadata only, no video)."""

    event_type: str
    severity: str
    occurred_at: datetime
    camera_name: str
    metadata: dict | None = None


class SummaryContext(BaseModel):
    """Structured input for summary generation.

    This is the ONLY data the LLM receives: aggregated events and counts.
    Never frames, images or personal identifiers (privacy by design).
    """

    period_start: datetime
    period_end: datetime
    total_events: int
    events_by_type: dict[str, int]
    events_by_severity: dict[str, int]
    events: list[EventSummaryItem]
