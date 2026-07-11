import numpy as np

from app.capture.preview import PreviewFrameStore, encode_preview_jpeg
from app.detection.base import BoundingBox
from app.tracking.base import TrackedDetection


def test_encode_preview_jpeg_resizes_and_returns_bytes() -> None:
    image = np.zeros((480, 1280, 3), dtype=np.uint8)

    jpeg = encode_preview_jpeg(image, max_width=640, jpeg_quality=80)

    assert jpeg is not None
    assert jpeg.startswith(b"\xff\xd8")


def test_encode_preview_jpeg_draws_detection_boxes() -> None:
    image = np.zeros((240, 320, 3), dtype=np.uint8)
    tracked = [
        TrackedDetection(
            track_id=1,
            object_class="person",
            confidence=0.9,
            bbox=BoundingBox(x=10, y=10, width=40, height=80),
        )
    ]

    jpeg = encode_preview_jpeg(
        image,
        max_width=320,
        jpeg_quality=80,
        tracked=tracked,
        draw_detections=True,
    )

    assert jpeg is not None
    assert len(jpeg) > 100


def test_preview_frame_store_update_and_get() -> None:
    from datetime import UTC, datetime
    from uuid import uuid4

    store = PreviewFrameStore()
    camera_id = uuid4()
    captured_at = datetime.now(UTC)

    store.update(
        camera_id,
        b"jpeg-bytes",
        captured_at=captured_at,
        width=640,
        height=480,
    )

    snapshot = store.get(camera_id)

    assert snapshot is not None
    assert snapshot.jpeg == b"jpeg-bytes"
    assert snapshot.width == 640

    store.clear(camera_id)
    assert store.get(camera_id) is None
