import asyncio
from datetime import UTC, datetime
from uuid import UUID, uuid4

import numpy as np
import pytest

from app.capture.base import Frame
from app.detection.base import BoundingBox, RawDetection
from app.detection.pipeline import DetectionPipeline
from app.tracking.base import TrackedDetection
from app.tracking.iou_tracker import IoUTracker
from app.workers.camera_simulator import CameraSimulatorWorker


class FakeImageSource:
    source_type = "fake"

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
            image=np.zeros((480, 640, 3), dtype=np.uint8),
        )

    def release(self) -> None:
        return None


class FakeDetector:
    model_name = "fake"

    def detect(self, image: np.ndarray) -> list[RawDetection]:
        return [RawDetection("person", 0.95, BoundingBox(10, 10, 40, 80))]


@pytest.mark.asyncio
async def test_worker_runs_pipeline_and_invokes_callback() -> None:
    camera_id = uuid4()
    received: list[TrackedDetection] = []

    async def on_detections(
        cam_id: UUID,
        tracked: list[TrackedDetection],
        frame: Frame,
    ) -> None:
        received.extend(tracked)

    worker = CameraSimulatorWorker(
        camera_id=camera_id,
        source=FakeImageSource(camera_id),
        fps=20,
        pipeline=DetectionPipeline(detector=FakeDetector(), tracker=IoUTracker()),
        on_detections=on_detections,
        inference_interval=0.0,
    )

    await worker.start()
    await asyncio.sleep(0.2)
    await worker.stop()

    status = worker.get_status()
    assert status.detection_enabled is True
    assert status.detections_processed >= 1
    assert len(received) >= 1
    assert received[0].object_class == "person"
