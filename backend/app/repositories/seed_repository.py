from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Camera, Configuration, Detection, Event


class SeedRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def has_cameras(self) -> bool:
        stmt = select(func.count()).select_from(Camera)
        result = await self._session.scalar(stmt)
        return int(result or 0) > 0

    async def add_camera(self, camera: Camera) -> None:
        self._session.add(camera)

    async def add_detection(self, detection: Detection) -> None:
        self._session.add(detection)

    async def add_event(self, event: Event) -> None:
        self._session.add(event)

    async def add_configuration(self, configuration: Configuration) -> None:
        self._session.add(configuration)
