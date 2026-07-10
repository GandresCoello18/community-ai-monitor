from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Camera


class CameraRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def add(self, camera: Camera) -> None:
        self._session.add(camera)

    async def count_active(self) -> int:
        stmt = (
            select(func.count()).select_from(Camera).where(Camera.deleted_at.is_(None))
        )
        result = await self._session.scalar(stmt)
        return int(result or 0)

    async def list_active(self, *, offset: int, limit: int) -> list[Camera]:
        stmt = (
            select(Camera)
            .where(Camera.deleted_at.is_(None))
            .order_by(Camera.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self._session.scalars(stmt)
        return list(result.all())

    async def get_by_id(self, camera_id: UUID) -> Camera | None:
        stmt = select(Camera).where(
            Camera.id == camera_id,
            Camera.deleted_at.is_(None),
        )
        return await self._session.scalar(stmt)
