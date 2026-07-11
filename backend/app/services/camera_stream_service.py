import asyncio
import logging
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.capture.base import Frame
from app.capture.factory import create_frame_source
from app.capture.preview import PreviewFrameStore
from app.core.config import Settings
from app.core.exceptions import NotFoundError
from app.detection.base import ObjectDetector
from app.detection.factory import create_detector
from app.detection.pipeline import DetectionPipeline
from app.models import Detection
from app.repositories.camera_repository import CameraRepository
from app.repositories.detection_repository import DetectionRepository
from app.schemas.common import ApiResponse
from app.schemas.stream import StreamStatusData, StreamStatusListData
from app.notifications.factory import create_notification_service
from app.services.event_ingestion_service import EventIngestionService
from app.tracking.base import TrackedDetection
from app.tracking.factory import create_tracker
from app.websocket.manager import WebSocketManager
from app.workers.camera_simulator import CameraSimulatorWorker, StreamStatus

logger = logging.getLogger(__name__)


class CameraStreamService:
    """Manages background camera workers (capture + CV + events, FASE 5–6)."""

    def __init__(
        self,
        settings: Settings,
        ws_manager: WebSocketManager | None = None,
        preview_store: PreviewFrameStore | None = None,
    ) -> None:
        self._settings = settings
        self._workers: dict[UUID, CameraSimulatorWorker] = {}
        self._detector: ObjectDetector | None = None
        notification_service = create_notification_service(settings)
        self._event_ingestion = EventIngestionService(
            settings,
            ws_manager=ws_manager,
            notification_service=notification_service,
        )
        self._preview_store = preview_store

    def _get_detector(self) -> ObjectDetector:
        if self._detector is None:
            self._detector = create_detector(self._settings)
        return self._detector

    async def auto_start_active_cameras(self, session: AsyncSession) -> None:
        if not self._settings.camera_simulator_enabled:
            return
        if not self._settings.camera_simulator_auto_start:
            return

        repository = CameraRepository(session)
        cameras = await repository.list_active(offset=0, limit=1000)
        await asyncio.gather(
            *(self.start_camera(camera.id, camera.stream_url) for camera in cameras)
        )

    async def start_camera(
        self,
        camera_id: UUID,
        stream_url: str | None,
    ) -> StreamStatus:
        if camera_id in self._workers:
            return self._workers[camera_id].get_status()

        source = create_frame_source(camera_id, stream_url, self._settings)

        pipeline: DetectionPipeline | None = None
        if self._settings.detection_enabled:
            pipeline = DetectionPipeline(
                detector=self._get_detector(),
                tracker=create_tracker(self._settings),
            )

        if self._settings.event_engine_enabled:
            self._event_ingestion.register_camera(camera_id)

        worker = CameraSimulatorWorker(
            camera_id=camera_id,
            source=source,
            fps=self._settings.camera_simulator_fps,
            pipeline=pipeline,
            on_detections=self._on_detections,
            inference_interval=self._settings.detection_interval_seconds,
            preview_store=self._preview_store,
            preview_settings=self._settings,
        )
        await worker.start()
        self._workers[camera_id] = worker
        return worker.get_status()

    async def stop_camera(self, camera_id: UUID) -> StreamStatus:
        worker = self._workers.get(camera_id)
        if worker is None:
            raise NotFoundError("STREAM_NOT_FOUND", "Camera stream is not running")
        status = worker.get_status()
        await self.stop_camera_if_running(camera_id)
        return status

    async def stop_camera_if_running(self, camera_id: UUID) -> None:
        worker = self._workers.pop(camera_id, None)
        if worker is None:
            return
        self._event_ingestion.unregister_camera(camera_id)
        await worker.stop()
        if self._preview_store is not None:
            self._preview_store.clear(camera_id)

    async def stop_all(self) -> None:
        camera_ids = list(self._workers.keys())
        if not camera_ids:
            return
        await asyncio.gather(
            *(self.stop_camera_if_running(camera_id) for camera_id in camera_ids)
        )

    async def _on_detections(
        self,
        camera_id: UUID,
        tracked: list[TrackedDetection],
        frame: Frame,
    ) -> None:
        await self._persist_detections(camera_id, tracked, frame)
        await self._event_ingestion.process_detections(camera_id, tracked, frame)

    async def _persist_detections(
        self,
        camera_id: UUID,
        tracked: list[TrackedDetection],
        frame: Frame,
    ) -> None:
        if not tracked or not self._settings.detection_persist_enabled:
            return

        from app.database.session import get_session_factory  # noqa: PLC0415

        session_factory = get_session_factory(self._settings)
        now = datetime.now(UTC)
        try:
            async with session_factory() as session:
                repository = DetectionRepository(session)
                repository.add_many(
                    [
                        Detection(
                            camera_id=camera_id,
                            object_class=item.object_class,
                            confidence=item.confidence,
                            bbox=item.bbox.as_dict(),
                            detected_at=frame.captured_at,
                            metadata_={
                                "track_id": item.track_id,
                                "frame_number": frame.frame_number,
                            },
                            created_at=now,
                        )
                        for item in tracked
                    ]
                )
                await session.commit()
        except Exception:
            logger.exception(
                "Failed to persist detections camera_id=%s count=%d",
                camera_id,
                len(tracked),
            )

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
                    detection_enabled=self._settings.detection_enabled,
                    detections_processed=0,
                    last_detection_at=None,
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
        detection_enabled=status.detection_enabled,
        detections_processed=status.detections_processed,
        last_detection_at=status.last_detection_at,
        error_message=status.error_message,
    )
