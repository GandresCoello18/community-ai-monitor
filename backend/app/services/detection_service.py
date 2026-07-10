from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.repositories.detection_repository import DetectionRepository
from app.schemas.camera import DetectionResponse, PaginatedResponse, PaginationMeta


class DetectionService:
    def __init__(self, session: AsyncSession, settings: Settings) -> None:
        self._repository = DetectionRepository(session)
        self._settings = settings

    async def list_detections(
        self,
        *,
        page: int,
        limit: int,
        camera_id: UUID | None = None,
    ) -> PaginatedResponse[DetectionResponse]:
        safe_limit = min(limit, self._settings.max_page_size)
        offset = (page - 1) * safe_limit
        total = await self._repository.count_all(camera_id=camera_id)
        detections = await self._repository.list_paginated(
            offset=offset,
            limit=safe_limit,
            camera_id=camera_id,
        )

        return PaginatedResponse(
            data=[
                DetectionResponse.model_validate(detection)
                for detection in detections
            ],
            meta=PaginationMeta(page=page, limit=safe_limit, total=total),
        )
