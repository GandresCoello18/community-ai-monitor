from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SummaryGenerateRequest(BaseModel):
    """Period to summarize. Defaults to the last 24 hours when omitted."""

    period_start: datetime | None = None
    period_end: datetime | None = None


class SummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    period_start: datetime
    period_end: datetime
    summary_text: str
    total_events: int
    llm_provider: str
    llm_model: str
    metadata: dict | None = Field(default=None, validation_alias="metadata_")
    created_at: datetime
    updated_at: datetime
