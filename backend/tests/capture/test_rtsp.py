from unittest.mock import MagicMock, patch
from uuid import uuid4

import numpy as np

from app.capture.factory import create_frame_source
from app.capture.rtsp import RTSPFrameSource
from app.capture.synthetic import SyntheticFrameSource
from app.core.config import Settings


@patch("app.capture.rtsp.RTSPFrameSource._warmup_capture", return_value=True)
@patch("app.capture.rtsp.shutil.which", return_value=None)
def test_real_rtsp_url_uses_rtsp_source(
    _mock_which: MagicMock,
    _mock_warmup: MagicMock,
) -> None:
    settings = Settings(app_env="testing")
    camera_id = uuid4()

    with patch("app.capture.rtsp.cv2.VideoCapture") as mock_capture:
        instance = MagicMock()
        instance.isOpened.return_value = True
        mock_capture.return_value = instance

        source = create_frame_source(
            camera_id,
            "rtsp://admin:pass@192.168.1.50:554/stream1",
            settings,
        )

    assert isinstance(source, RTSPFrameSource)
    assert source.source_type == "rtsp"


def test_demo_rtsp_url_still_uses_synthetic() -> None:
    settings = Settings(app_env="testing")
    camera_id = uuid4()

    source = create_frame_source(camera_id, "rtsp://demo/camera-01", settings)

    assert isinstance(source, SyntheticFrameSource)


@patch("app.capture.rtsp.RTSPFrameSource._warmup_capture", return_value=True)
@patch("app.capture.rtsp.shutil.which", return_value=None)
@patch("app.capture.rtsp.cv2.VideoCapture")
@patch("app.capture.rtsp.time.sleep")
def test_rtsp_reconnects_after_read_failures(
    mock_sleep: MagicMock,
    mock_capture_cls: MagicMock,
    _mock_which: MagicMock,
    _mock_warmup: MagicMock,
) -> None:
    camera_id = uuid4()
    instance = MagicMock()
    instance.isOpened.return_value = True
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    instance.read.side_effect = [
        (False, None),
        (False, None),
        (False, None),
        (True, frame),
    ]
    mock_capture_cls.return_value = instance

    source = RTSPFrameSource(
        camera_id,
        "rtsp://192.168.1.50/stream1",
        reconnect_delay_seconds=0,
        read_failures_before_reconnect=3,
    )

    assert source.read() is None
    assert source.read() is None
    assert source.read() is None
    result = source.read()

    assert result is not None
    assert result.frame_number == 1
    mock_sleep.assert_called()


@patch("app.capture.rtsp.FfmpegRtspReader")
@patch("app.capture.rtsp.RTSPFrameSource._warmup_capture", return_value=False)
@patch("app.capture.rtsp.shutil.which", return_value="/usr/bin/ffmpeg")
@patch("app.capture.rtsp.cv2.VideoCapture")
def test_rtsp_falls_back_to_ffmpeg_when_opencv_warmup_fails(
    mock_capture_cls: MagicMock,
    _mock_which: MagicMock,
    _mock_warmup: MagicMock,
    mock_ffmpeg_cls: MagicMock,
) -> None:
    camera_id = uuid4()
    instance = MagicMock()
    instance.isOpened.return_value = True
    mock_capture_cls.return_value = instance

    ffmpeg_instance = MagicMock()
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    ffmpeg_frame = MagicMock()
    ffmpeg_frame.frame_number = 1
    ffmpeg_instance.read.return_value = ffmpeg_frame
    mock_ffmpeg_cls.return_value = ffmpeg_instance

    source = RTSPFrameSource(
        camera_id,
        "rtsp://192.168.1.50/stream1",
        transport_fallback=False,
    )

    result = source.read()
    assert result is ffmpeg_frame
    mock_ffmpeg_cls.assert_called()
