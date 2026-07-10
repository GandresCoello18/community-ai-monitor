import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.capture.factory import create_frame_source
from app.core.config import Settings
from app.core.exceptions import NotFoundError
from app.repositories.camera_repository import CameraRepository
from app.schemas.common import ApiResponse
from app.schemas.stream import StreamStatusData, StreamStatusListData
from app.workers.camera_simulator import CameraSimulatorWorker, StreamStatus

logger = logging.getLogger(__name__)


class CameraStreamService:
    """Manages background camera simulators (FASE 4 — capture only)."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._workers: dict[UUID, CameraSimulatorWorker] = {}

    async def auto_start_active_cameras(self, session: AsyncSession) -> None:
        if not self._settings.camera_simulator_enabled:
            return
        if not self._settings.camera_simulator_auto_start:
            return

        repository = CameraRepository(session)
        cameras = await repository.list_active(offset=0, limit=1000)
        for camera in cameras:
            await self.start_camera(camera.id, camera.stream_url)

    async def start_camera(
        self,
        camera_id: UUID,
        stream_url: str | None,
    ) -> StreamStatus:
        if camera_id in self._workers:
            return self._workers[camera_id].get_status()

        source = create_frame_source(camera_id, stream_url, self._settings)
        worker = CameraSimulatorWorker(
            camera_id=camera_id,
            source=source,
            fps=self._settings.camera_simulator_fps,
        )
        await worker.start()
        self._workers[camera_id] = worker
        return worker.get_status()

    async def stop_camera(self, camera_id: UUID) -> StreamStatus:
        worker = self._workers.pop(camera_id, None)
        if worker is None:
            raise NotFoundError("STREAM_NOT_FOUND", "Camera stream is not running")
        await worker.stop()
        return worker.get_status()

    async def stop_all(self) -> None:
        for camera_id in list(self._workers.keys()):
            await self.stop_camera(camera_id)

    def get_status(self, camera_id: UUID) -> StreamStatus:
        worker = self._workers.get(camera_id)
        if worker is None:
            raise NotFoundError("STREAM_NOT_FOUND", "Camera stream is not running")
        return worker.get_status()

    def list_statuses(self) -> list[StreamStatus]:
        return [worker.get_status() for worker in self._workers.values()]

    async def get_camera_status(
        self,
        session: AsyncSession,
        camera_id: UUID,
    ) -> ApiResponse[StreamStatusData]:
        repository = CameraRepository(session)
        camera = await repository.get_by_id(camera_id)
        if camera is None:
            raise NotFoundError("CAMERA_NOT_FOUND", "Camera does not exist")

        worker = self._workers.get(camera_id)
        if worker is None:
            return ApiResponse(
                data=StreamStatusData(
                    camera_id=camera_id,
                    status="stopped",
                    source_type="none",
                    frames_processed=0,
                    fps_target=self._settings.camera_simulator_fps,
                    last_frame_at=None,
                    error_message=None,
                ),
            )

        status = worker.get_status()
        return ApiResponse(data=to_stream_status_data(status))

    def list_status_response(self) -> ApiResponse[StreamStatusListData]:
        statuses = [to_stream_status_data(item) for item in self.list_statuses()]
        return ApiResponse(data=StreamStatusListData(streams=statuses))


def to_stream_status_data(status: StreamStatus) -> StreamStatusData:
    return StreamStatusData(
        camera_id=status.camera_id,
        status=status.status,
        source_type=status.source_type,
        frames_processed=status.frames_processed,
        fps_target=status.fps_target,
        last_frame_at=status.last_frame_at,
        error_message=status.error_message,
    )
