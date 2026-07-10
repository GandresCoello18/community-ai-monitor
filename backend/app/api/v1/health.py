from fastapi import APIRouter

from app.api.deps import HealthServiceDep
from app.schemas.common import ApiResponse, HealthData

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=ApiResponse[HealthData],
    response_model_exclude_none=True,
    summary="Health check",
    description="Returns API and database connectivity status.",
)
async def health_check(service: HealthServiceDep) -> ApiResponse[HealthData]:
    return await service.get_health()
