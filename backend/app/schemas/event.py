from datetime import datetime

from pydantic import BaseModel, Field


class EventStatisticsData(BaseModel):
    total: int
    by_type: dict[str, int] = Field(default_factory=dict)
    by_severity: dict[str, int] = Field(default_factory=dict)
    by_camera: dict[str, int] = Field(default_factory=dict)


class EventStatisticsMeta(BaseModel):
    period_start: datetime | None = None
    period_end: datetime | None = None
    camera_id: str | None = None
    event_type: str | None = None


class EventStatisticsResponse(BaseModel):
    data: EventStatisticsData
    meta: EventStatisticsMeta
