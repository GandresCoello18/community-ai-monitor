import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from app.capture.base import FrameSource

logger = logging.getLogger(__name__)


@dataclass
class StreamStatus:
    camera_id: UUID
    status: str
    source_type: str
    frames_processed: int = 0
    fps_target: float = 0.0
    last_frame_at: datetime | None = None
    error_message: str | None = None


@dataclass
class CameraSimulatorWorker:
    """Background worker that reads frames from a source at a target FPS."""

    camera_id: UUID
    source: FrameSource
    fps: float
    _running: bool = field(default=False, init=False)
    _task: asyncio.Task[None] | None = field(default=None, init=False)
    _frames_processed: int = field(default=0, init=False)
    _last_frame_at: datetime | None = field(default=None, init=False)
    _error_message: str | None = field(default=None, init=False)

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._error_message = None
        self._task = asyncio.create_task(self._run_loop())
        logger.info(
            "Camera simulator started camera_id=%s source=%s fps=%.2f",
            self.camera_id,
            self.source.source_type,
            self.fps,
        )

    async def stop(self) -> None:
        self._running = False
        if self._task is not None:
            await self._task
            self._task = None
        self.source.release()
        logger.info("Camera simulator stopped camera_id=%s", self.camera_id)

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
            error_message=self._error_message,
        )

    async def _run_loop(self) -> None:
        interval = 1.0 / self.fps if self.fps > 0 else 0.5
        try:
            while self._running:
                frame = await asyncio.to_thread(self.source.read)
                if frame is None:
                    await asyncio.sleep(interval)
                    continue

                self._frames_processed += 1
                self._last_frame_at = frame.captured_at

                if self._frames_processed % 10 == 0:
                    logger.debug(
                        "Frame captured camera_id=%s frame=%s size=%sx%s",
                        frame.camera_id,
                        frame.frame_number,
                        frame.width,
                        frame.height,
                    )

                await asyncio.sleep(interval)
        except Exception as exc:
            self._error_message = str(exc)
            self._running = False
            logger.exception(
                "Camera simulator error camera_id=%s",
                self.camera_id,
            )
        finally:
            self.source.release()
