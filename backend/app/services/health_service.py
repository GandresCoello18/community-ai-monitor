from app.schemas.common import ApiResponse, HealthData


class HealthService:
    """Application health checks."""

    async def get_health(self) -> ApiResponse[HealthData]:
        return ApiResponse(data=HealthData(status="ok"))
