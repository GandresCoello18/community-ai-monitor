from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.capture.url_utils import mask_stream_url
from app.core.config import Settings
from app.core.exceptions import NotFoundError
from app.models import Camera
from app.repositories.camera_repository import CameraRepository
from app.schemas.camera import (
    CameraCreate,
    CameraResponse,
    PaginatedResponse,
    PaginationMeta,
)
from app.schemas.common import ApiResponse


class CameraService:
    def __init__(self, session: AsyncSession, settings: Settings) -> None:
        self._session = session
        self._repository = CameraRepository(session)
        self._settings = settings

    async def list_cameras(
        self,
        *,
        page: int,
        limit: int,
    ) -> PaginatedResponse[CameraResponse]:
        safe_limit = min(limit, self._settings.max_page_size)
        offset = (page - 1) * safe_limit
        total = await self._repository.count_active()
        cameras = await self._repository.list_active(offset=offset, limit=safe_limit)

        return PaginatedResponse(
            data=[to_camera_response(camera) for camera in cameras],
            meta=PaginationMeta(page=page, limit=safe_limit, total=total),
        )

    async def get_camera(self, camera_id: UUID) -> ApiResponse[CameraResponse]:
        camera = await self._repository.get_by_id(camera_id)
        if camera is None:
            raise NotFoundError("CAMERA_NOT_FOUND", "Camera does not exist")
        return ApiResponse(data=to_camera_response(camera))

    async def create_camera(self, payload: CameraCreate) -> ApiResponse[CameraResponse]:
        camera = Camera(
            name=payload.name,
            location=payload.location,
            stream_url=payload.stream_url,
            is_active=payload.is_active,
        )
        self._repository.add(camera)
        await self._session.flush()
        return ApiResponse(data=to_camera_response(camera))


def to_camera_response(camera: Camera) -> CameraResponse:
    """Map DB camera to API response with credentials masked in stream_url."""
    response = CameraResponse.model_validate(camera)
    return response.model_copy(
        update={"stream_url": mask_stream_url(response.stream_url)},
    )
