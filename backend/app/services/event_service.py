from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.repositories.event_repository import EventRepository
from app.schemas.camera import EventResponse, PaginatedResponse, PaginationMeta
from app.schemas.event import (
    EventStatisticsData,
    EventStatisticsMeta,
    EventStatisticsResponse,
)


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
        event_type: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> PaginatedResponse[EventResponse]:
        safe_limit = min(limit, self._settings.max_page_size)
        offset = (page - 1) * safe_limit
        total = await self._repository.count_all(
            camera_id=camera_id,
            event_type=event_type,
            start_date=start_date,
            end_date=end_date,
        )
        events = await self._repository.list_paginated(
            offset=offset,
            limit=safe_limit,
            camera_id=camera_id,
            event_type=event_type,
            start_date=start_date,
            end_date=end_date,
        )

        return PaginatedResponse(
            data=[EventResponse.model_validate(event) for event in events],
            meta=PaginationMeta(page=page, limit=safe_limit, total=total),
        )

    async def get_statistics(
        self,
        *,
        camera_id: UUID | None = None,
        event_type: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> EventStatisticsResponse:
        stats = await self._repository.get_statistics(
            camera_id=camera_id,
            event_type=event_type,
            start_date=start_date,
            end_date=end_date,
        )
        return EventStatisticsResponse(
            data=EventStatisticsData(
                total=stats.total,
                by_type=stats.by_type,
                by_severity=stats.by_severity,
                by_camera=stats.by_camera,
                by_day=stats.by_day,
            ),
            meta=EventStatisticsMeta(
                period_start=start_date,
                period_end=end_date,
                camera_id=str(camera_id) if camera_id else None,
                event_type=event_type,
            ),
        )
