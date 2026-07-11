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


class CameraCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120, examples=["Camera Entrada"])
    location: str = Field(
        min_length=1,
        max_length=255,
        examples=["Parque Central - Entrada Norte"],
    )
    stream_url: str | None = Field(
        default=None,
        examples=["rtsp://user:pass@192.168.1.50:554/stream1", "webcam://0"],
    )
    is_active: bool = True


class CameraUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    location: str | None = Field(default=None, min_length=1, max_length=255)
    stream_url: str | None = None
    is_active: bool | None = None


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
