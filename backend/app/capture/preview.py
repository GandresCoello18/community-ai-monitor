"""In-memory live preview for camera streams (not persisted)."""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

import cv2
import numpy as np

logger = logging.getLogger(__name__)

_PREVIEW_COLORS: dict[str, tuple[int, int, int]] = {
    "person": (0, 200, 0),
    "car": (255, 140, 0),
    "motorcycle": (255, 140, 0),
    "bicycle": (0, 200, 200),
    "dog": (200, 100, 255),
    "cat": (200, 100, 255),
}
_DEFAULT_BOX_COLOR = (0, 255, 255)


@dataclass(frozen=True, slots=True)
class PreviewSnapshot:
    jpeg: bytes
    captured_at: datetime
    width: int
    height: int


class PreviewFrameStore:
    """Thread-safe cache of the latest JPEG preview per camera."""

    def __init__(self) -> None:
        self._frames: dict[UUID, PreviewSnapshot] = {}
        self._lock = threading.Lock()

    def update(
        self,
        camera_id: UUID,
        jpeg: bytes,
        *,
        captured_at: datetime,
        width: int,
        height: int,
    ) -> None:
        snapshot = PreviewSnapshot(
            jpeg=jpeg,
            captured_at=captured_at,
            width=width,
            height=height,
        )
        with self._lock:
            self._frames[camera_id] = snapshot

    def get(self, camera_id: UUID) -> PreviewSnapshot | None:
        with self._lock:
            return self._frames.get(camera_id)

    def clear(self, camera_id: UUID) -> None:
        with self._lock:
            self._frames.pop(camera_id, None)


def encode_preview_jpeg(
    image: np.ndarray,
    *,
    max_width: int,
    jpeg_quality: int,
    tracked: list[object] | None = None,
    draw_detections: bool = True,
) -> bytes | None:
    """Resize, optionally annotate detections, and encode as JPEG."""
    if image.size == 0:
        return None

    frame = image
    if draw_detections and tracked:
        frame = _draw_tracked_detections(image.copy(), tracked)

    height, width = frame.shape[:2]
    if max_width > 0 and width > max_width:
        scale = max_width / width
        frame = cv2.resize(
            frame,
            (max_width, max(1, int(height * scale))),
            interpolation=cv2.INTER_AREA,
        )

    quality = max(1, min(jpeg_quality, 100))
    success, encoded = cv2.imencode(
        ".jpg",
        frame,
        [int(cv2.IMWRITE_JPEG_QUALITY), quality],
    )
    if not success:
        logger.warning("Failed to encode preview JPEG")
        return None
    return encoded.tobytes()


def _draw_tracked_detections(
    image: np.ndarray,
    tracked: list[object],
) -> np.ndarray:
    for item in tracked:
        bbox = item.bbox
        color = _PREVIEW_COLORS.get(item.object_class, _DEFAULT_BOX_COLOR)
        x1, y1 = bbox.x, bbox.y
        x2, y2 = bbox.x + bbox.width, bbox.y + bbox.height
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
        label = f"{item.object_class} {item.confidence:.0%}"
        cv2.putText(
            image,
            label,
            (x1, max(y1 - 6, 12)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            color,
            1,
            cv2.LINE_AA,
        )
    return image
