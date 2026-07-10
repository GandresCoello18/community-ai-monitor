from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PaginationMeta(BaseModel):
    page: int
    limit: int
    total: int


class PaginatedResponse[T](BaseModel):
    data: list[T]
    meta: PaginationMeta


class CameraResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    location: str
    stream_url: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class EventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    camera_id: UUID
    event_type: str
    severity: str
    occurred_at: datetime
    started_at: datetime | None
    ended_at: datetime | None
    metadata: dict | None = Field(validation_alias="metadata_")
    created_at: datetime
    updated_at: datetime


class DetectionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    camera_id: UUID
    object_class: str
    confidence: float
    bbox: dict
    detected_at: datetime
    metadata: dict | None = Field(validation_alias="metadata_")
    created_at: datetime
