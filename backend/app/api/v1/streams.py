from fastapi import APIRouter, Request

from app.api.deps import SettingsDep
from app.capture.preview import PreviewFrameStore
from app.schemas.common import ApiResponse
from app.schemas.stream import StreamStatusListData
from app.services.camera_stream_service import CameraStreamService

router = APIRouter(prefix="/streams", tags=["streams"])


def _get_stream_service(request: Request, settings: SettingsDep) -> CameraStreamService:
    service = getattr(request.app.state, "camera_stream_service", None)
    if service is None:
        preview_store = getattr(request.app.state, "preview_store", None)
        if preview_store is None:
            preview_store = PreviewFrameStore()
            request.app.state.preview_store = preview_store
        service = CameraStreamService(settings, preview_store=preview_store)
        request.app.state.camera_stream_service = service
    return service


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
    service = _get_stream_service(request, settings)
    return service.list_status_response()
