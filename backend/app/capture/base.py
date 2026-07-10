from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol
from uuid import UUID

import numpy as np


@dataclass(frozen=True, slots=True)
class Frame:
    """Structured frame metadata plus in-memory pixels for the CV pipeline.

    `image` holds the raw BGR pixels only in memory so the detection pipeline
    can run. It is never persisted to the database (privacy by design) and is
    excluded from equality/repr. It is `None` for sources without real pixels
    (e.g. the synthetic source).
    """

    camera_id: UUID
    frame_number: int
    captured_at: datetime
    width: int
    height: int
    image: np.ndarray | None = field(default=None, compare=False, repr=False)


class FrameSource(Protocol):
    """Adapter interface for video capture sources."""

    @property
    def source_type(self) -> str: ...

    def read(self) -> Frame | None: ...

    def release(self) -> None: ...
