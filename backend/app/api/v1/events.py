from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.deps import EventServiceDep, pagination_params
from app.schemas.camera import EventResponse, PaginatedResponse
from app.schemas.event import EventStatisticsResponse

router = APIRouter(prefix="/events", tags=["events"])


@router.get(
    "/statistics",
    response_model=EventStatisticsResponse,
    summary="Get aggregated event statistics",
)
async def get_event_statistics(
    service: EventServiceDep,
    camera_id: UUID | None = Query(default=None),
    event_type: str | None = Query(default=None),
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
) -> EventStatisticsResponse:
    return await service.get_statistics(
        camera_id=camera_id,
        event_type=event_type,
        start_date=start_date,
        end_date=end_date,
    )


@router.get(
    "",
    response_model=PaginatedResponse[EventResponse],
    summary="List events",
)
async def list_events(
    service: EventServiceDep,
    pagination: tuple[int, int] = Depends(pagination_params),
    camera_id: UUID | None = Query(default=None),
    event_type: str | None = Query(default=None),
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
) -> PaginatedResponse[EventResponse]:
    page, limit = pagination
    return await service.list_events(
        page=page,
        limit=limit,
        camera_id=camera_id,
        event_type=event_type,
        start_date=start_date,
        end_date=end_date,
    )
