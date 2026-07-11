from uuid import UUID

from fastapi import APIRouter, Depends, Request
from fastapi.responses import Response, StreamingResponse

from app.api.deps import CameraServiceDep, SessionDep, SettingsDep, pagination_params
from app.capture.preview import PreviewFrameStore
from app.core.config import Settings
from app.core.exceptions import AppException, NotFoundError
from app.database.session import get_session_factory
from app.repositories.camera_repository import CameraRepository
from app.schemas.camera import CameraCreate, CameraResponse, CameraUpdate, PaginatedResponse
from app.schemas.common import ApiResponse
from app.schemas.stream import StreamStatusData
from app.services.camera_preview_service import MJPEG_BOUNDARY, CameraPreviewService
from app.services.camera_stream_service import (
    CameraStreamService,
    to_stream_status_data,
)

router = APIRouter(prefix="/cameras", tags=["cameras"])


def _get_preview_store(request: Request) -> PreviewFrameStore:
    store = getattr(request.app.state, "preview_store", None)
    if store is None:
        store = PreviewFrameStore()
        request.app.state.preview_store = store
    return store


def _get_stream_service(request: Request, settings: Settings) -> CameraStreamService:
    service = getattr(request.app.state, "camera_stream_service", None)
    if service is None:
        service = CameraStreamService(
            settings,
            preview_store=_get_preview_store(request),
        )
        request.app.state.camera_stream_service = service
    return service


def _get_preview_service(
    request: Request,
    settings: Settings,
) -> CameraPreviewService:
    return CameraPreviewService(settings, _get_preview_store(request))


async def _ensure_camera_exists(session: SessionDep, camera_id: UUID) -> None:
    repository = CameraRepository(session)
    camera = await repository.get_by_id(camera_id)
    if camera is None:
        raise NotFoundError("CAMERA_NOT_FOUND", "Camera does not exist")


@router.get(
    "",
    response_model=PaginatedResponse[CameraResponse],
    summary="List cameras",
)
async def list_cameras(
    service: CameraServiceDep,
    pagination: tuple[int, int] = Depends(pagination_params),
) -> PaginatedResponse[CameraResponse]:
    page, limit = pagination
    return await service.list_cameras(page=page, limit=limit)


@router.post(
    "",
    response_model=ApiResponse[CameraResponse],
    response_model_exclude_none=True,
    status_code=201,
    summary="Create a camera",
)
async def create_camera(
    payload: CameraCreate,
    service: CameraServiceDep,
) -> ApiResponse[CameraResponse]:
    return await service.create_camera(payload)


@router.get(
    "/{camera_id}",
    response_model=ApiResponse[CameraResponse],
    response_model_exclude_none=True,
    summary="Get camera by ID",
)
async def get_camera(
    camera_id: UUID,
    service: CameraServiceDep,
) -> ApiResponse[CameraResponse]:
    return await service.get_camera(camera_id)


@router.patch(
    "/{camera_id}",
    response_model=ApiResponse[CameraResponse],
    response_model_exclude_none=True,
    summary="Update a camera",
    description=(
        "Partially updates camera fields. If stream_url changes, any active "
        "stream worker is stopped so the new URL takes effect on next start."
    ),
)
async def update_camera(
    camera_id: UUID,
    payload: CameraUpdate,
    request: Request,
    service: CameraServiceDep,
    settings: SettingsDep,
) -> ApiResponse[CameraResponse]:
    if "stream_url" in payload.model_fields_set:
        stream_service = _get_stream_service(request, settings)
        await stream_service.stop_camera_if_running(camera_id)
    return await service.update_camera(camera_id, payload)


@router.delete(
    "/{camera_id}",
    response_model=ApiResponse[CameraResponse],
    response_model_exclude_none=True,
    summary="Delete a camera",
    description=(
        "Soft-deletes a camera. Historical detections and events are preserved. "
        "Any active stream worker is stopped before deletion."
    ),
)
async def delete_camera(
    camera_id: UUID,
    request: Request,
    service: CameraServiceDep,
    settings: SettingsDep,
) -> ApiResponse[CameraResponse]:
    stream_service = _get_stream_service(request, settings)
    await stream_service.stop_camera_if_running(camera_id)
    return await service.delete_camera(camera_id)


@router.get(
    "/{camera_id}/preview",
    summary="Get latest camera preview frame (JPEG)",
    description=(
        "Returns the most recent in-memory preview frame. "
        "Frames are not persisted to the database."
    ),
    responses={
        200: {"content": {"image/jpeg": {}}},
        404: {"description": "Preview disabled or stream not running"},
    },
)
async def get_camera_preview(
    camera_id: UUID,
    request: Request,
    session: SessionDep,
    settings: SettingsDep,
) -> Response:
    await _ensure_camera_exists(session, camera_id)
    preview_service = _get_preview_service(request, settings)
    snapshot = preview_service.get_snapshot(camera_id)
    return Response(
        content=snapshot.jpeg,
        media_type="image/jpeg",
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate",
            "X-Preview-Captured-At": snapshot.captured_at.isoformat(),
            "X-Preview-Width": str(snapshot.width),
            "X-Preview-Height": str(snapshot.height),
        },
    )


@router.get(
    "/{camera_id}/preview/stream",
    summary="Live MJPEG preview stream",
    description=(
        "Multipart MJPEG stream of the latest in-memory frames. "
        "Suitable for embedding in an HTML img element."
    ),
    responses={404: {"description": "Preview disabled"}},
)
async def stream_camera_preview(
    camera_id: UUID,
    request: Request,
    settings: SettingsDep,
) -> StreamingResponse:
    session_factory = get_session_factory(settings)
    async with session_factory() as session:
        await _ensure_camera_exists(session, camera_id)

    preview_service = _get_preview_service(request, settings)
    preview_service.ensure_enabled()
    return StreamingResponse(
        preview_service.mjpeg_stream(camera_id),
        media_type=f"multipart/x-mixed-replace; boundary={MJPEG_BOUNDARY}",
        headers={"Cache-Control": "no-store"},
    )


@router.get(
    "/{camera_id}/stream/status",
    response_model=ApiResponse[StreamStatusData],
    response_model_exclude_none=True,
    summary="Get camera stream simulator status",
)
async def get_camera_stream_status(
    camera_id: UUID,
    request: Request,
    session: SessionDep,
    settings: SettingsDep,
) -> ApiResponse[StreamStatusData]:
    stream_service = _get_stream_service(request, settings)
    return await stream_service.get_camera_status(session, camera_id)


@router.post(
    "/{camera_id}/stream/start",
    response_model=ApiResponse[StreamStatusData],
    response_model_exclude_none=True,
    summary="Start camera stream simulator (development)",
)
async def start_camera_stream(
    camera_id: UUID,
    request: Request,
    session: SessionDep,
    settings: SettingsDep,
) -> ApiResponse[StreamStatusData]:
    _ensure_development(settings)
    stream_service = _get_stream_service(request, settings)

    repository = CameraRepository(session)
    camera = await repository.get_by_id(camera_id)
    if camera is None:
        raise NotFoundError("CAMERA_NOT_FOUND", "Camera does not exist")

    status = await stream_service.start_camera(camera.id, camera.stream_url)
    return ApiResponse(data=to_stream_status_data(status))


@router.post(
    "/{camera_id}/stream/stop",
    response_model=ApiResponse[StreamStatusData],
    response_model_exclude_none=True,
    summary="Stop camera stream simulator (development)",
)
async def stop_camera_stream(
    camera_id: UUID,
    request: Request,
    settings: SettingsDep,
) -> ApiResponse[StreamStatusData]:
    _ensure_development(settings)
    stream_service = _get_stream_service(request, settings)
    status = await stream_service.stop_camera(camera_id)
    return ApiResponse(data=to_stream_status_data(status))


def _ensure_development(settings: Settings) -> None:
    if not settings.is_development:
        raise AppException(
            code="FORBIDDEN",
            message="Stream control is only available in development",
            status_code=403,
        )
