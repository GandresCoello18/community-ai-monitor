from typing import Annotated

from fastapi import Depends

from app.core.config import Settings, get_settings
from app.services.health_service import HealthService


def get_health_service() -> HealthService:
    return HealthService()


SettingsDep = Annotated[Settings, Depends(get_settings)]
HealthServiceDep = Annotated[HealthService, Depends(get_health_service)]
