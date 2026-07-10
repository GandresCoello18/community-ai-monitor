from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.deps import EventServiceDep, pagination_params
from app.schemas.camera import EventResponse, PaginatedResponse

router = APIRouter(prefix="/events", tags=["events"])


@router.get(
    "",
    response_model=PaginatedResponse[EventResponse],
    summary="List events",
)
async def list_events(
    service: EventServiceDep,
    pagination: tuple[int, int] = Depends(pagination_params),
    camera_id: UUID | None = Query(default=None),
) -> PaginatedResponse[EventResponse]:
    page, limit = pagination
    return await service.list_events(page=page, limit=limit, camera_id=camera_id)
