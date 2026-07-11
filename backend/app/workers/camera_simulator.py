import asyncio
import logging
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from app.capture.base import Frame, FrameSource
from app.capture.preview import PreviewFrameStore, encode_preview_jpeg
from app.core.config import Settings
from app.detection.pipeline import DetectionPipeline
from app.tracking.base import TrackedDetection

logger = logging.getLogger(__name__)

DetectionCallback = Callable[[UUID, list[TrackedDetection], Frame], Awaitable[None]]


@dataclass
class StreamStatus:
    camera_id: UUID
    status: str
    source_type: str
    frames_processed: int = 0
    fps_target: float = 0.0
    last_frame_at: datetime | None = None
    detection_enabled: bool = False
    detections_processed: int = 0
    last_detection_at: datetime | None = None
    error_message: str | None = None


@dataclass
class CameraSimulatorWorker:
    """Background worker: reads frames and (optionally) runs the CV pipeline.

    Capture runs at `fps`. When a `pipeline` is provided, inference runs at most
    once every `inference_interval` seconds to keep CPU usage bounded, and the
    resulting tracked detections are handed to `on_detections` for persistence.
    """

    camera_id: UUID
    source: FrameSource
    fps: float
    pipeline: DetectionPipeline | None = None
    on_detections: DetectionCallback | None = None
    inference_interval: float = 1.0
    preview_store: PreviewFrameStore | None = None
    preview_settings: Settings | None = None
    _running: bool = field(default=False, init=False)
    _task: asyncio.Task[None] | None = field(default=None, init=False)
    _frames_processed: int = field(default=0, init=False)
    _detections_processed: int = field(default=0, init=False)
    _last_frame_at: datetime | None = field(default=None, init=False)
    _last_detection_at: datetime | None = field(default=None, init=False)
    _last_inference_at: float = field(default=0.0, init=False)
    _last_preview_at: float = field(default=0.0, init=False)
    _last_tracked: list[TrackedDetection] = field(default_factory=list, init=False)
    _error_message: str | None = field(default=None, init=False)

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._error_message = None
        self._task = asyncio.create_task(self._run_loop())
        logger.info(
            "Camera worker started camera_id=%s source=%s fps=%.2f detection=%s",
            self.camera_id,
            self.source.source_type,
            self.fps,
            self.pipeline is not None,
        )

    async def stop(self) -> None:
        """Stop the worker promptly, even if capture is blocked on RTSP I/O."""
        self._running = False
        shutdown_timeout = (
            self.preview_settings.camera_worker_shutdown_timeout_seconds
            if self.preview_settings is not None
            else 5.0
        )

        # Release capture first so a blocking read() in a worker thread can exit.
        await asyncio.to_thread(self.source.release)

        if self._task is not None:
            self._task.cancel()
            try:
                await asyncio.wait_for(self._task, timeout=shutdown_timeout)
            except asyncio.CancelledError:
                pass
            except TimeoutError:
                logger.warning(
                    "Camera worker shutdown timed out camera_id=%s timeout=%.1fs",
                    self.camera_id,
                    shutdown_timeout,
                )
            self._task = None

        await asyncio.to_thread(self.source.release)
        if self.preview_store is not None:
            self.preview_store.clear(self.camera_id)
        logger.info("Camera worker stopped camera_id=%s", self.camera_id)

    def get_status(self) -> StreamStatus:
        status = "running" if self._running else "stopped"
        if self._error_message:
            status = "error"
        return StreamStatus(
            camera_id=self.camera_id,
            status=status,
            source_type=self.source.source_type,
            frames_processed=self._frames_processed,
            fps_target=self.fps,
            last_frame_at=self._last_frame_at,
            detection_enabled=self.pipeline is not None,
            detections_processed=self._detections_processed,
            last_detection_at=self._last_detection_at,
            error_message=self._error_message,
        )

    async def _run_loop(self) -> None:
        interval = 1.0 / self.fps if self.fps > 0 else 0.5
        try:
            while self._running:
                frame = await asyncio.to_thread(self.source.read)
                if not self._running:
                    break
                if frame is None:
                    await asyncio.sleep(interval)
                    continue

                self._frames_processed += 1
                self._last_frame_at = frame.captured_at
                await self._maybe_update_preview(frame)
                await self._maybe_run_inference(frame)
                await asyncio.sleep(interval)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            self._error_message = str(exc)
            self._running = False
            logger.exception("Camera worker error camera_id=%s", self.camera_id)
        finally:
            self.source.release()

    async def _maybe_run_inference(self, frame: Frame) -> None:
        if self.pipeline is None or frame.image is None:
            return

        now = time.monotonic()
        if now - self._last_inference_at < self.inference_interval:
            return
        self._last_inference_at = now

        tracked = await asyncio.to_thread(self.pipeline.process, frame.image)
        self._last_tracked = tracked
        if not tracked:
            return

        self._detections_processed += len(tracked)
        self._last_detection_at = frame.captured_at
        if self.on_detections is not None:
            await self.on_detections(self.camera_id, tracked, frame)

    async def _maybe_update_preview(self, frame: Frame) -> None:
        settings = self.preview_settings
        store = self.preview_store
        if (
            settings is None
            or store is None
            or not settings.camera_preview_enabled
            or frame.image is None
        ):
            return

        preview_fps = settings.camera_preview_fps
        interval = 1.0 / preview_fps if preview_fps > 0 else 0.5
        now = time.monotonic()
        if now - self._last_preview_at < interval:
            return
        self._last_preview_at = now

        tracked = self._last_tracked if settings.camera_preview_show_detections else None
        jpeg = await asyncio.to_thread(
            encode_preview_jpeg,
            frame.image,
            max_width=settings.camera_preview_max_width,
            jpeg_quality=settings.camera_preview_jpeg_quality,
            tracked=tracked,
            draw_detections=settings.camera_preview_show_detections,
        )
        if jpeg is None:
            return

        store.update(
            self.camera_id,
            jpeg,
            captured_at=frame.captured_at,
            width=frame.width,
            height=frame.height,
        )
