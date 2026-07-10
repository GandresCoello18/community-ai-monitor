from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.common import ApiResponse, HealthData


class HealthService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_health(self) -> ApiResponse[HealthData]:
        database_status = "connected"
        try:
            await self._session.execute(text("SELECT 1"))
        except Exception:
            database_status = "disconnected"

        status = "ok" if database_status == "connected" else "degraded"
        return ApiResponse(
            data=HealthData(status=status, database=database_status),
        )
