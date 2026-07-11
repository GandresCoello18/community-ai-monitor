from unittest.mock import MagicMock, patch
from uuid import uuid4

import numpy as np
import subprocess

from app.capture.factory import create_frame_source
from app.capture.ffmpeg_rtsp import FfmpegRtspReader
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


@patch("app.capture.factory.HttpMjpegFrameSource")
def test_ip_webcam_rtsp_uses_http_mjpeg_by_default(
    mock_http_source: MagicMock,
) -> None:
    settings = Settings(app_env="testing")
    camera_id = uuid4()

    create_frame_source(
        camera_id,
        "rtsp://192.168.3.216:8080/h264_pcm.sdp",
        settings,
    )

    mock_http_source.assert_called_once_with(
        camera_id,
        "http://192.168.3.216:8080/video",
        buffer_size=settings.rtsp_buffer_size,
        output_max_width=settings.rtsp_ffmpeg_output_max_width,
    )


@patch("app.capture.rtsp.time.monotonic", return_value=10.0)
@patch("app.capture.rtsp.RTSPFrameSource._warmup_capture", return_value=True)
@patch("app.capture.rtsp.shutil.which", return_value=None)
@patch("app.capture.rtsp.cv2.VideoCapture")
def test_rtsp_reconnects_after_read_failures(
    mock_capture_cls: MagicMock,
    _mock_which: MagicMock,
    _mock_warmup: MagicMock,
    _mock_monotonic: MagicMock,
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


@patch("app.capture.ffmpeg_rtsp.subprocess.run")
@patch("app.capture.ffmpeg_rtsp.shutil.which")
def test_ffprobe_timeout_uses_default_resolution(
    mock_which: MagicMock,
    mock_run: MagicMock,
) -> None:
    mock_which.side_effect = lambda name: "/usr/bin/ffmpeg" if name == "ffmpeg" else "/usr/bin/ffprobe"
    mock_run.side_effect = subprocess.TimeoutExpired(cmd=["ffprobe"], timeout=8)

    with patch.object(FfmpegRtspReader, "_start_process"):
        reader = FfmpegRtspReader(uuid4(), "rtsp://192.168.1.50/stream1")

    assert reader._width == 640
    assert reader._height == 480


@patch("app.capture.ffmpeg_rtsp.subprocess.Popen")
@patch("app.capture.ffmpeg_rtsp.subprocess.run")
@patch("app.capture.ffmpeg_rtsp.shutil.which")
def test_ffmpeg_start_process_keeps_reader_open(
    mock_which: MagicMock,
    mock_run: MagicMock,
    mock_popen: MagicMock,
) -> None:
    mock_which.side_effect = (
        lambda name: f"/usr/bin/{name}" if name in ("ffmpeg", "ffprobe") else None
    )
    mock_run.return_value = MagicMock(returncode=0, stdout="640x480\n", stderr="")

    process = MagicMock()
    process.poll.return_value = None
    process.stdout.read.return_value = b"\x00" * (640 * 480 * 3)
    mock_popen.return_value = process

    reader = FfmpegRtspReader(uuid4(), "rtsp://192.168.1.50/stream1")

    assert reader._closed is False
    frame = reader.read()

    assert frame is not None
    assert frame.width == 640
    assert frame.height == 480


@patch("app.capture.rtsp.time.monotonic", return_value=10.0)
@patch("app.capture.rtsp.FfmpegRtspReader")
def test_rtsp_ffmpeg_waits_before_reconnect_on_read_failures(
    mock_ffmpeg_cls: MagicMock,
    _mock_monotonic: MagicMock,
) -> None:
    camera_id = uuid4()
    ffmpeg_instance = MagicMock()
    ffmpeg_instance.read.return_value = None
    mock_ffmpeg_cls.return_value = ffmpeg_instance

    source = RTSPFrameSource(
        camera_id,
        "rtsp://192.168.1.50/stream1",
        reconnect_delay_seconds=5.0,
        read_failures_before_reconnect=3,
        use_ffmpeg_first=True,
    )
    source._ffmpeg_reader = ffmpeg_instance
    source._backend = "ffmpeg"
    source._last_connection_attempt_at = 0.0

    assert source.read() is None
    assert source.read() is None
    assert source._consecutive_failures == 2
    assert ffmpeg_instance.release.call_count == 0


@patch("app.capture.rtsp.time.monotonic", side_effect=[0.0, 0.0, 0.0, 1.0])
@patch("app.capture.rtsp.RTSPFrameSource._open_capture", return_value=False)
@patch("app.capture.rtsp.RTSPFrameSource._try_ffmpeg_fallback")
def test_rtsp_waits_before_retrying_failed_connection(
    mock_fallback: MagicMock,
    _mock_open: MagicMock,
    _mock_monotonic: MagicMock,
) -> None:
    source = RTSPFrameSource(
        uuid4(),
        "rtsp://192.168.1.50/stream1",
        reconnect_delay_seconds=5.0,
    )

    assert source.read() is None
    assert mock_fallback.call_count == 1

    assert source.read() is None
    assert mock_fallback.call_count == 1


def test_rtsp_release_interrupts_further_reads() -> None:
    source = RTSPFrameSource(
        uuid4(),
        "rtsp://192.168.1.50/stream1",
        reconnect_delay_seconds=5.0,
    )

    source.release()

    assert source.read() is None
    assert source.read() is None
