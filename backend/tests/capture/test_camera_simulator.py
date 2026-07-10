import asyncio
from uuid import uuid4

import pytest

from app.capture.factory import create_frame_source
from app.capture.synthetic import SyntheticFrameSource
from app.core.config import Settings
from app.workers.camera_simulator import CameraSimulatorWorker


@pytest.fixture
def capture_settings() -> Settings:
    return Settings(
        app_env="testing",
        camera_simulator_video_path=None,
    )


def test_demo_rtsp_url_uses_synthetic_source(capture_settings: Settings) -> None:
    camera_id = uuid4()
    source = create_frame_source(camera_id, "rtsp://demo/camera-01", capture_settings)

    assert isinstance(source, SyntheticFrameSource)
    assert source.source_type == "synthetic"


def test_synthetic_source_produces_frames() -> None:
    camera_id = uuid4()
    source = SyntheticFrameSource(camera_id)

    frame = source.read()

    assert frame is not None
    assert frame.camera_id == camera_id
    assert frame.frame_number == 1
    assert frame.width == 640
    assert frame.height == 480


@pytest.mark.asyncio
async def test_camera_simulator_worker_processes_frames() -> None:
    camera_id = uuid4()
    source = SyntheticFrameSource(camera_id)
    worker = CameraSimulatorWorker(camera_id=camera_id, source=source, fps=20)

    await worker.start()
    await asyncio.sleep(0.25)
    status = worker.get_status()

    assert status.status == "running"
    assert status.frames_processed >= 1

    await worker.stop()
    assert worker.get_status().status == "stopped"
