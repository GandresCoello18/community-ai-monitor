from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.repositories.event_repository import EventRepository
from app.schemas.camera import EventResponse, PaginatedResponse, PaginationMeta


class EventService:
    def __init__(self, session: AsyncSession, settings: Settings) -> None:
        self._repository = EventRepository(session)
        self._settings = settings

    async def list_events(
        self,
        *,
        page: int,
        limit: int,
        camera_id: UUID | None = None,
    ) -> PaginatedResponse[EventResponse]:
        safe_limit = min(limit, self._settings.max_page_size)
        offset = (page - 1) * safe_limit
        total = await self._repository.count_all(camera_id=camera_id)
        events = await self._repository.list_paginated(
            offset=offset,
            limit=safe_limit,
            camera_id=camera_id,
        )

        return PaginatedResponse(
            data=[EventResponse.model_validate(event) for event in events],
            meta=PaginationMeta(page=page, limit=safe_limit, total=total),
        )
