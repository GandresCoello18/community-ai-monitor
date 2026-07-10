from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True, slots=True)
class Frame:
    """Structured frame metadata. Raw pixels are not exposed outside capture."""

    camera_id: UUID
    frame_number: int
    captured_at: datetime
    width: int
    height: int


class FrameSource(Protocol):
    """Adapter interface for video capture sources."""

    @property
    def source_type(self) -> str: ...

    def read(self) -> Frame | None: ...

    def release(self) -> None: ...
