from datetime import UTC, datetime
from uuid import UUID

from app.capture.base import Frame


class SyntheticFrameSource:
    """Generates frames without hardware or video files (demo / tests)."""

    source_type = "synthetic"

    def __init__(self, camera_id: UUID) -> None:
        self._camera_id = camera_id
        self._frame_number = 0

    def read(self) -> Frame:
        self._frame_number += 1
        return Frame(
            camera_id=self._camera_id,
            frame_number=self._frame_number,
            captured_at=datetime.now(UTC),
            width=640,
            height=480,
        )

    def release(self) -> None:
        return None
