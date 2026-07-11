"""RTSP capture via ffmpeg subprocess (fallback when OpenCV read fails)."""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import time
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
        probe_timeout_seconds: float = 8.0,
        output_max_width: int = 640,
        read_timeout_seconds: float = 15.0,
    ) -> None:
        if shutil.which("ffmpeg") is None:
            msg = "ffmpeg is not installed or not on PATH"
            raise RuntimeError(msg)

        self._camera_id = camera_id
        self._rtsp_url = rtsp_url
        self._safe_url = mask_stream_url(rtsp_url) or rtsp_url
        self._transport = transport
        self._probe_timeout_seconds = probe_timeout_seconds
        self._output_max_width = output_max_width
        self._read_timeout_seconds = read_timeout_seconds
        self._frame_number = 0
        self._width = 0
        self._height = 0
        self._frame_size = 0
        self._process: subprocess.Popen[bytes] | None = None
        self._closed = False
        self._nonblocking_stdout = False
        self._partial_buffer = b""
        self._read_failures = 0

        self._probe_stream()
        if not self._closed:
            self._start_process()

    def read(self) -> Frame | None:
        if self._closed:
            return None

        if self._process is None or self._process.poll() is not None:
            self._start_process()
            if self._process is None or self._process.poll() is not None:
                return None

        raw = self._read_frame_bytes()
        if len(raw) != self._frame_size:
            if len(raw) == 0 and self._process is not None and self._process.poll() is None:
                return None

            self._read_failures += 1
            logger.warning(
                "Incomplete ffmpeg frame camera_id=%s bytes=%d expected=%d failures=%d",
                self._camera_id,
                len(raw),
                self._frame_size,
                self._read_failures,
            )
            if self._read_failures >= 3 or (
                self._process is not None and self._process.poll() is not None
            ):
                self._partial_buffer = b""
                self._read_failures = 0
                self._restart_process()
            return None

        self._partial_buffer = b""
        self._read_failures = 0
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
        if self._closed:
            return
        self._closed = True
        self._terminate_process()

    def _terminate_process(self) -> None:
        """Stop the ffmpeg subprocess without marking the reader as closed."""
        if self._process is None:
            return
        self._process.terminate()
        try:
            self._process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            self._process.kill()
        self._process = None
        self._nonblocking_stdout = False
        self._partial_buffer = b""

    def _probe_stream(self) -> None:
        if self._closed:
            return

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
            "-timeout",
            str(int(self._probe_timeout_seconds * 1_000_000)),
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height",
            "-of",
            "csv=s=x:p=0",
            self._rtsp_url,
        ]
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self._probe_timeout_seconds + 2,
                check=False,
            )
        except subprocess.TimeoutExpired:
            logger.warning(
                "ffprobe timed out camera_id=%s url=%s transport=%s timeout=%ss",
                self._camera_id,
                self._safe_url,
                self._transport,
                self._probe_timeout_seconds,
            )
            self._width, self._height = 640, 480
            self._frame_size = self._width * self._height * 3
            return
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

        self._apply_output_size()
        self._frame_size = self._width * self._height * 3
        logger.info(
            "ffmpeg stream probed camera_id=%s url=%s output_size=%dx%d transport=%s",
            self._camera_id,
            self._safe_url,
            self._width,
            self._height,
            self._transport,
        )

    def _apply_output_size(self) -> None:
        if self._output_max_width <= 0 or self._width <= self._output_max_width:
            return

        scale = self._output_max_width / self._width
        self._height = max(2, int(self._height * scale) // 2 * 2)
        self._width = self._output_max_width

    def _start_process(self) -> None:
        if self._closed:
            return
        self._terminate_process()
        cmd = [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-rtsp_transport",
            self._transport,
            "-timeout",
            str(int(self._probe_timeout_seconds * 1_000_000)),
            "-max_delay",
            "500000",
            "-i",
            self._rtsp_url,
            "-map",
            "0:v:0",
            "-an",
            "-sn",
            "-vf",
            (
                f"scale={self._width}:{self._height}:"
                "force_original_aspect_ratio=decrease,"
                f"pad={self._width}:{self._height}:(ow-iw)/2:(oh-ih)/2"
            ),
            "-f",
            "rawvideo",
            "-pix_fmt",
            "bgr24",
            "-",
        ]
        self._process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        self._configure_stdout()
        logger.info(
            "ffmpeg RTSP process started camera_id=%s url=%s transport=%s",
            self._camera_id,
            self._safe_url,
            self._transport,
        )

    def _configure_stdout(self) -> None:
        self._nonblocking_stdout = False
        if self._process is None or self._process.stdout is None:
            return

        try:
            os.set_blocking(self._process.stdout.fileno(), False)
        except (AttributeError, OSError, TypeError, ValueError):
            # Keep the blocking fallback for platforms or test doubles that do not
            # support non-blocking pipes.
            return
        self._nonblocking_stdout = True

    def _read_frame_bytes(self) -> bytes:
        if self._process is None or self._process.stdout is None:
            return b""

        if self._partial_buffer:
            if len(self._partial_buffer) >= self._frame_size:
                frame = self._partial_buffer[: self._frame_size]
                self._partial_buffer = self._partial_buffer[self._frame_size :]
                return frame
            remaining = self._frame_size - len(self._partial_buffer)
        else:
            remaining = self._frame_size

        if not self._nonblocking_stdout:
            chunk = self._process.stdout.read(remaining)
            if not chunk:
                return b""
            self._partial_buffer += chunk
            if len(self._partial_buffer) >= self._frame_size:
                frame = self._partial_buffer[: self._frame_size]
                self._partial_buffer = self._partial_buffer[self._frame_size :]
                return frame
            return b""

        deadline = time.monotonic() + self._read_timeout_seconds
        fd = self._process.stdout.fileno()

        while remaining > 0 and time.monotonic() < deadline:
            if self._closed:
                return b""
            if self._process.poll() is not None:
                break

            try:
                chunk = os.read(fd, min(remaining, 64 * 1024))
            except BlockingIOError:
                time.sleep(0.02)
                continue

            if not chunk:
                time.sleep(0.02)
                continue

            self._partial_buffer += chunk
            remaining -= len(chunk)

        if len(self._partial_buffer) >= self._frame_size:
            frame = self._partial_buffer[: self._frame_size]
            self._partial_buffer = self._partial_buffer[self._frame_size :]
            return frame

        return b""

    def _restart_process(self) -> None:
        logger.warning(
            "Restarting ffmpeg RTSP process camera_id=%s url=%s",
            self._camera_id,
            self._safe_url,
        )
        self._start_process()
