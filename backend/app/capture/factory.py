import logging
from pathlib import Path
from uuid import UUID

from app.capture.base import FrameSource
from app.capture.opencv_sources import (
    HttpMjpegFrameSource,
    VideoFileFrameSource,
    WebcamFrameSource,
)
from app.capture.rtsp import RTSPFrameSource
from app.capture.synthetic import SyntheticFrameSource
from app.capture.url_utils import ip_webcam_http_url, is_ip_webcam_rtsp
from app.core.config import Settings

logger = logging.getLogger(__name__)


def create_frame_source(
    camera_id: UUID,
    stream_url: str | None,
    settings: Settings,
) -> FrameSource:
    """Resolve a camera stream URL into a concrete frame source."""
    url = (stream_url or "").strip()

    if url.startswith("webcam://"):
        device_index = int(url.removeprefix("webcam://") or "0")
        return WebcamFrameSource(camera_id, device_index=device_index)

    if url.startswith("file://"):
        file_path = url.removeprefix("file://")
        return VideoFileFrameSource(camera_id, file_path)

    if url.endswith((".mp4", ".avi", ".mov", ".mkv")):
        return VideoFileFrameSource(camera_id, url)

    if settings.camera_simulator_video_path:
        return VideoFileFrameSource(camera_id, settings.camera_simulator_video_path)

    if url.startswith("rtsp://demo") or url == "" or url.startswith("synthetic://"):
        return SyntheticFrameSource(camera_id)

    if url.startswith(("http://", "https://")):
        return HttpMjpegFrameSource(
            camera_id,
            url,
            buffer_size=settings.rtsp_buffer_size,
            output_max_width=settings.rtsp_ffmpeg_output_max_width,
        )

    if url.startswith(("rtsp://", "rtsps://")):
        if settings.ip_webcam_prefer_http and is_ip_webcam_rtsp(url):
            http_url = ip_webcam_http_url(url)
            if http_url is not None:
                logger.info(
                    "Using IP Webcam HTTP MJPEG for camera_id=%s url=%s",
                    camera_id,
                    http_url,
                )
                return HttpMjpegFrameSource(
                    camera_id,
                    http_url,
                    buffer_size=settings.rtsp_buffer_size,
                    output_max_width=settings.rtsp_ffmpeg_output_max_width,
                )

        return RTSPFrameSource(
            camera_id,
            url,
            transport=settings.rtsp_transport,
            buffer_size=settings.rtsp_buffer_size,
            reconnect_delay_seconds=settings.rtsp_reconnect_delay_seconds,
            read_failures_before_reconnect=settings.rtsp_read_failures_before_reconnect,
            warmup_seconds=settings.rtsp_warmup_seconds,
            transport_fallback=settings.rtsp_transport_fallback,
            probe_timeout_seconds=settings.rtsp_probe_timeout_seconds,
            use_ffmpeg_first=settings.rtsp_use_ffmpeg_first,
            ffmpeg_output_max_width=settings.rtsp_ffmpeg_output_max_width,
            ffmpeg_read_timeout_seconds=settings.rtsp_ffmpeg_read_timeout_seconds,
        )

    path = Path(url)
    if path.is_file():
        return VideoFileFrameSource(camera_id, str(path))

    logger.warning("Unknown stream URL, using synthetic fallback: %s", url)
    return SyntheticFrameSource(camera_id)
