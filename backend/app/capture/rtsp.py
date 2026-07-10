import logging
import os
import shutil
import time
from datetime import UTC, datetime
from uuid import UUID

import cv2

from app.capture.base import Frame
from app.capture.ffmpeg_rtsp import FfmpegRtspReader
from app.capture.url_utils import (
    apply_rtsp_transport,
    build_rtsp_ffmpeg_options,
    mask_stream_url,
)

logger = logging.getLogger(__name__)


class RTSPFrameSource:
    """Reads frames from an IP camera RTSP stream (FASE 11).

    Tries OpenCV first (with warmup and transport fallback). If OpenCV opens
    the stream but cannot read frames — common with IP Webcam on Windows —
    falls back to an ffmpeg subprocess pipe when ffmpeg is available.
    """

    source_type = "rtsp"

    def __init__(
        self,
        camera_id: UUID,
        rtsp_url: str,
        *,
        transport: str = "tcp",
        buffer_size: int = 1,
        reconnect_delay_seconds: float = 5.0,
        read_failures_before_reconnect: int = 3,
        warmup_seconds: float = 10.0,
        transport_fallback: bool = True,
    ) -> None:
        self._camera_id = camera_id
        self._rtsp_url = rtsp_url
        self._safe_url = mask_stream_url(rtsp_url) or rtsp_url
        self._transport = transport
        self._buffer_size = buffer_size
        self._reconnect_delay = reconnect_delay_seconds
        self._failures_before_reconnect = read_failures_before_reconnect
        self._warmup_seconds = warmup_seconds
        self._transport_fallback = transport_fallback
        self._frame_number = 0
        self._consecutive_failures = 0
        self._capture: cv2.VideoCapture | None = None
        self._last_reconnect_at: float = 0.0
        self._ffmpeg_reader: FfmpegRtspReader | None = None
        self._backend: str = "opencv"
        self._connect_attempted = False

    def read(self) -> Frame | None:
        if self._ffmpeg_reader is not None:
            return self._ffmpeg_reader.read()

        if not self._connect_attempted:
            self._connect_attempted = True
            if not self._open_capture():
                self._try_ffmpeg_fallback()
            if self._ffmpeg_reader is not None:
                return self._ffmpeg_reader.read()

        if self._capture is None or not self._capture.isOpened():
            if not self._open_capture():
                self._try_ffmpeg_fallback()
            if self._ffmpeg_reader is not None:
                return self._ffmpeg_reader.read()
            if self._capture is None or not self._capture.isOpened():
                return None

        success, image = self._capture.read()
        if not success or image is None:
            self._consecutive_failures += 1
            if self._consecutive_failures >= self._failures_before_reconnect:
                if self._consecutive_failures == self._failures_before_reconnect:
                    logger.warning(
                        "OpenCV RTSP read failing, trying ffmpeg fallback "
                        "camera_id=%s url=%s",
                        self._camera_id,
                        self._safe_url,
                    )
                    self._try_ffmpeg_fallback()
                    if self._ffmpeg_reader is not None:
                        return self._ffmpeg_reader.read()
                self._reconnect()
            return None

        self._consecutive_failures = 0
        height, width = image.shape[:2]
        self._frame_number += 1
        return Frame(
            camera_id=self._camera_id,
            frame_number=self._frame_number,
            captured_at=datetime.now(UTC),
            width=width,
            height=height,
            image=image,
        )

    def release(self) -> None:
        if self._ffmpeg_reader is not None:
            self._ffmpeg_reader.release()
            self._ffmpeg_reader = None
        if self._capture is not None:
            self._capture.release()
            self._capture = None

    def _transports_to_try(self) -> list[str]:
        primary = self._transport.lower()
        if not self._transport_fallback:
            return [primary]
        alternate = "udp" if primary == "tcp" else "tcp"
        return [primary] if primary == alternate else [primary, alternate]

    def _open_capture(self) -> bool:
        if self._capture is not None:
            self._capture.release()
            self._capture = None

        for transport in self._transports_to_try():
            capture = self._create_opencv_capture(transport)
            if capture is None:
                continue
            if self._warmup_capture(capture):
                self._transport = transport
                self._capture = capture
                self._backend = "opencv"
                logger.info(
                    "RTSP stream opened camera_id=%s url=%s transport=%s "
                    "backend=opencv",
                    self._camera_id,
                    self._safe_url,
                    transport,
                )
                return True
            capture.release()
            logger.warning(
                "RTSP warmup failed camera_id=%s url=%s transport=%s",
                self._camera_id,
                self._safe_url,
                transport,
            )

        return False

    def _create_opencv_capture(self, transport: str) -> cv2.VideoCapture | None:
        capture_url = apply_rtsp_transport(self._rtsp_url, transport)
        os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = build_rtsp_ffmpeg_options(
            transport
        )

        capture = cv2.VideoCapture(capture_url, cv2.CAP_FFMPEG)
        if not capture.isOpened():
            logger.warning(
                "Unable to open RTSP stream camera_id=%s url=%s transport=%s",
                self._camera_id,
                self._safe_url,
                transport,
            )
            capture.release()
            return None

        capture.set(cv2.CAP_PROP_BUFFERSIZE, self._buffer_size)
        if hasattr(cv2, "CAP_PROP_OPEN_TIMEOUT_MSEC"):
            capture.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 10000)
        if hasattr(cv2, "CAP_PROP_READ_TIMEOUT_MSEC"):
            capture.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, 10000)
        return capture

    def _warmup_capture(self, capture: cv2.VideoCapture) -> bool:
        deadline = time.monotonic() + self._warmup_seconds
        while time.monotonic() < deadline:
            success, image = capture.read()
            if success and image is not None:
                return True
            time.sleep(0.2)
        return False

    def _try_ffmpeg_fallback(self) -> None:
        if self._ffmpeg_reader is not None:
            return
        if shutil.which("ffmpeg") is None:
            logger.warning(
                "ffmpeg not on PATH, cannot fallback camera_id=%s url=%s",
                self._camera_id,
                self._safe_url,
            )
            return

        if self._capture is not None:
            self._capture.release()
            self._capture = None

        for transport in self._transports_to_try():
            try:
                reader = FfmpegRtspReader(
                    self._camera_id,
                    self._rtsp_url,
                    transport=transport,
                )
            except Exception:
                logger.exception(
                    "ffmpeg fallback failed camera_id=%s url=%s transport=%s",
                    self._camera_id,
                    self._safe_url,
                    transport,
                )
                continue

            frame = reader.read()
            if frame is not None:
                self._ffmpeg_reader = reader
                self._transport = transport
                self._backend = "ffmpeg"
                logger.info(
                    "RTSP using ffmpeg fallback camera_id=%s url=%s transport=%s",
                    self._camera_id,
                    self._safe_url,
                    transport,
                )
                return
            reader.release()

    def _reconnect(self) -> None:
        now = time.monotonic()
        if now - self._last_reconnect_at < self._reconnect_delay:
            return

        self._last_reconnect_at = now
        self._consecutive_failures = 0
        logger.warning(
            "RTSP reconnecting camera_id=%s url=%s backend=%s",
            self._camera_id,
            self._safe_url,
            self._backend,
        )
        time.sleep(self._reconnect_delay)

        if self._ffmpeg_reader is not None:
            self._ffmpeg_reader.release()
            self._ffmpeg_reader = None
            self._try_ffmpeg_fallback()
            return

        self._open_capture()
