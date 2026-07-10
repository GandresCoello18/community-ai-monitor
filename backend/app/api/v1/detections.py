from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.deps import DetectionServiceDep, pagination_params
from app.schemas.camera import DetectionResponse, PaginatedResponse

router = APIRouter(prefix="/detections", tags=["detections"])


@router.get(
    "",
    response_model=PaginatedResponse[DetectionResponse],
    summary="List detections",
)
async def list_detections(
    service: DetectionServiceDep,
    pagination: tuple[int, int] = Depends(pagination_params),
    camera_id: UUID | None = Query(default=None),
) -> PaginatedResponse[DetectionResponse]:
    page, limit = pagination
    return await service.list_detections(page=page, limit=limit, camera_id=camera_id)
