from fastapi import APIRouter, Request

from app.api.deps import SettingsDep
from app.schemas.common import ApiResponse
from app.schemas.stream import StreamStatusListData
from app.services.camera_stream_service import CameraStreamService

router = APIRouter(prefix="/streams", tags=["streams"])


@router.get(
    "/status",
    response_model=ApiResponse[StreamStatusListData],
    response_model_exclude_none=True,
    summary="List all active stream simulators",
)
async def list_stream_statuses(
    request: Request,
    settings: SettingsDep,
) -> ApiResponse[StreamStatusListData]:
    service = getattr(request.app.state, "camera_stream_service", None)
    if service is None:
        service = CameraStreamService(settings)
        request.app.state.camera_stream_service = service
    return service.list_status_response()
