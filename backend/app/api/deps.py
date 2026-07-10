from typing import Annotated

from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.database.session import get_db_session
from app.services.camera_service import CameraService
from app.services.event_service import EventService
from app.services.health_service import HealthService

SettingsDep = Annotated[Settings, Depends(get_settings)]


async def get_session(settings: SettingsDep) -> AsyncSession:
    async for session in get_db_session(settings):
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_health_service(session: SessionDep) -> HealthService:
    return HealthService(session)


def get_camera_service(
    session: SessionDep,
    settings: SettingsDep,
) -> CameraService:
    return CameraService(session, settings)


def get_event_service(
    session: SessionDep,
    settings: SettingsDep,
) -> EventService:
    return EventService(session, settings)


HealthServiceDep = Annotated[HealthService, Depends(get_health_service)]
CameraServiceDep = Annotated[CameraService, Depends(get_camera_service)]
EventServiceDep = Annotated[EventService, Depends(get_event_service)]


def pagination_params(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> tuple[int, int]:
    return page, limit
