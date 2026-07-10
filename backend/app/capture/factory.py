import logging
from pathlib import Path
from uuid import UUID

from app.capture.base import FrameSource
from app.capture.opencv_sources import VideoFileFrameSource, WebcamFrameSource
from app.capture.synthetic import SyntheticFrameSource
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

    if url.startswith("rtsp://"):
        logger.warning(
            "RTSP source not supported in FASE 4, using synthetic fallback: %s",
            url,
        )
        return SyntheticFrameSource(camera_id)

    path = Path(url)
    if path.is_file():
        return VideoFileFrameSource(camera_id, str(path))

    logger.warning("Unknown stream URL, using synthetic fallback: %s", url)
    return SyntheticFrameSource(camera_id)
