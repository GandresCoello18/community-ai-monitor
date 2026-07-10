import logging
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

import cv2

from app.capture.base import Frame

logger = logging.getLogger(__name__)


class VideoFileFrameSource:
    """Reads frames from a local video file (MP4, AVI, etc.)."""

    source_type = "file"

    def __init__(self, camera_id: UUID, file_path: str) -> None:
        path = Path(file_path)
        if not path.is_file():
            msg = f"Video file not found: {file_path}"
            raise FileNotFoundError(msg)

        self._camera_id = camera_id
        self._file_path = str(path)
        self._capture = cv2.VideoCapture(self._file_path)
        self._frame_number = 0

        if not self._capture.isOpened():
            msg = f"Unable to open video file: {file_path}"
            raise RuntimeError(msg)

    def read(self) -> Frame | None:
        success, image = self._capture.read()
        if not success:
            self._capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
            success, image = self._capture.read()
            if not success:
                logger.warning("Failed to read frame from %s", self._file_path)
                return None

        height, width = image.shape[:2]
        self._frame_number += 1
        return Frame(
            camera_id=self._camera_id,
            frame_number=self._frame_number,
            captured_at=datetime.now(UTC),
            width=width,
            height=height,
        )

    def release(self) -> None:
        if self._capture is not None:
            self._capture.release()


class WebcamFrameSource:
    """Reads frames from a local webcam device index."""

    source_type = "webcam"

    def __init__(self, camera_id: UUID, device_index: int = 0) -> None:
        self._camera_id = camera_id
        self._device_index = device_index
        self._capture = cv2.VideoCapture(device_index)
        self._frame_number = 0

        if not self._capture.isOpened():
            msg = f"Unable to open webcam device {device_index}"
            raise RuntimeError(msg)

    def read(self) -> Frame | None:
        success, image = self._capture.read()
        if not success:
            return None

        height, width = image.shape[:2]
        self._frame_number += 1
        return Frame(
            camera_id=self._camera_id,
            frame_number=self._frame_number,
            captured_at=datetime.now(UTC),
            width=width,
            height=height,
        )

    def release(self) -> None:
        if self._capture is not None:
            self._capture.release()
