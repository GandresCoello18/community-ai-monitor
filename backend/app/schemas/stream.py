from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class StreamStatusData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    camera_id: UUID
    status: str = Field(examples=["running"])
    source_type: str = Field(examples=["synthetic"])
    frames_processed: int
    fps_target: float
    last_frame_at: datetime | None
    detection_enabled: bool = False
    detections_processed: int = 0
    last_detection_at: datetime | None = None
    error_message: str | None = None


class StreamStatusListData(BaseModel):
    streams: list[StreamStatusData]
