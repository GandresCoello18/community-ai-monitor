from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Event


class EventRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def count_all(self, *, camera_id: UUID | None = None) -> int:
        stmt = select(func.count()).select_from(Event)
        if camera_id is not None:
            stmt = stmt.where(Event.camera_id == camera_id)
        result = await self._session.scalar(stmt)
        return int(result or 0)

    async def list_paginated(
        self,
        *,
        offset: int,
        limit: int,
        camera_id: UUID | None = None,
    ) -> list[Event]:
        stmt = (
            select(Event).order_by(Event.occurred_at.desc()).offset(offset).limit(limit)
        )
        if camera_id is not None:
            stmt = stmt.where(Event.camera_id == camera_id)
        result = await self._session.scalars(stmt)
        return list(result.all())
