from uuid import UUID

from fastapi import APIRouter, Depends, Request

from app.api.deps import CameraServiceDep, SessionDep, SettingsDep, pagination_params
from app.core.config import Settings
from app.core.exceptions import AppException, NotFoundError
from app.repositories.camera_repository import CameraRepository
from app.schemas.camera import CameraResponse, PaginatedResponse
from app.schemas.common import ApiResponse
from app.schemas.stream import StreamStatusData
from app.services.camera_stream_service import (
    CameraStreamService,
    to_stream_status_data,
)

router = APIRouter(prefix="/cameras", tags=["cameras"])


def _get_stream_service(request: Request, settings: Settings) -> CameraStreamService:
    service = getattr(request.app.state, "camera_stream_service", None)
    if service is None:
        service = CameraStreamService(settings)
        request.app.state.camera_stream_service = service
    return service


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
