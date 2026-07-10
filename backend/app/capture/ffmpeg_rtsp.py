"""RTSP capture via ffmpeg subprocess (fallback when OpenCV read fails)."""

from __future__ import annotations

import logging
import shutil
import subprocess
from datetime import UTC, datetime
from uuid import UUID

import numpy as np

from app.capture.base import Frame
from app.capture.url_utils import mask_stream_url

logger = logging.getLogger(__name__)


class FfmpegRtspReader:
    """Reads raw BGR frames from an RTSP URL using the ffmpeg CLI."""

    source_type = "rtsp"

    def __init__(
        self,
        camera_id: UUID,
        rtsp_url: str,
        *,
        transport: str = "tcp",
    ) -> None:
        if shutil.which("ffmpeg") is None:
            msg = "ffmpeg is not installed or not on PATH"
            raise RuntimeError(msg)

        self._camera_id = camera_id
        self._rtsp_url = rtsp_url
        self._safe_url = mask_stream_url(rtsp_url) or rtsp_url
        self._transport = transport
        self._frame_number = 0
        self._width = 0
        self._height = 0
        self._frame_size = 0
        self._process: subprocess.Popen[bytes] | None = None

        self._probe_stream()
        self._start_process()

    def read(self) -> Frame | None:
        if self._process is None or self._process.poll() is not None:
            self._start_process()
            if self._process is None or self._process.poll() is not None:
                return None

        assert self._process.stdout is not None
        raw = self._process.stdout.read(self._frame_size)
        if len(raw) != self._frame_size:
            logger.warning(
                "Incomplete ffmpeg frame camera_id=%s bytes=%d expected=%d",
                self._camera_id,
                len(raw),
                self._frame_size,
            )
            self._restart_process()
            return None

        image = np.frombuffer(raw, dtype=np.uint8).reshape(
            (self._height, self._width, 3)
        )
        self._frame_number += 1
        return Frame(
            camera_id=self._camera_id,
            frame_number=self._frame_number,
            captured_at=datetime.now(UTC),
            width=self._width,
            height=self._height,
            image=image.copy(),
        )

    def release(self) -> None:
        if self._process is not None:
            self._process.terminate()
            try:
                self._process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self._process.kill()
            self._process = None

    def _probe_stream(self) -> None:
        ffprobe = shutil.which("ffprobe")
        if ffprobe is None:
            self._width, self._height = 640, 480
            self._frame_size = self._width * self._height * 3
            logger.warning(
                "ffprobe not found, using default resolution 640x480 camera_id=%s",
                self._camera_id,
            )
            return

        cmd = [
            ffprobe,
            "-v",
            "error",
            "-rtsp_transport",
            self._transport,
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height",
            "-of",
            "csv=s=x:p=0",
            self._rtsp_url,
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        if result.returncode != 0:
            logger.warning(
                "ffprobe failed camera_id=%s url=%s stderr=%s",
                self._camera_id,
                self._safe_url,
                result.stderr.strip(),
            )
            self._width, self._height = 640, 480
        else:
            parts = result.stdout.strip().split("x")
            self._width, self._height = int(parts[0]), int(parts[1])

        self._frame_size = self._width * self._height * 3
        logger.info(
            "ffmpeg stream probed camera_id=%s url=%s size=%dx%d transport=%s",
            self._camera_id,
            self._safe_url,
            self._width,
            self._height,
            self._transport,
        )

    def _start_process(self) -> None:
        self.release()
        cmd = [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-rtsp_transport",
            self._transport,
            "-i",
            self._rtsp_url,
            "-an",
            "-sn",
            "-f",
            "rawvideo",
            "-pix_fmt",
            "bgr24",
            "-",
        ]
        self._process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        logger.info(
            "ffmpeg RTSP process started camera_id=%s url=%s transport=%s",
            self._camera_id,
            self._safe_url,
            self._transport,
        )

    def _restart_process(self) -> None:
        logger.warning(
            "Restarting ffmpeg RTSP process camera_id=%s url=%s",
            self._camera_id,
            self._safe_url,
        )
        self._start_process()
