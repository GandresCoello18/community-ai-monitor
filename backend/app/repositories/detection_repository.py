from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Detection


class DetectionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def add(self, detection: Detection) -> None:
        self._session.add(detection)

    def add_many(self, detections: list[Detection]) -> None:
        self._session.add_all(detections)

    async def count_all(self, *, camera_id: UUID | None = None) -> int:
        stmt = select(func.count()).select_from(Detection)
        if camera_id is not None:
            stmt = stmt.where(Detection.camera_id == camera_id)
        result = await self._session.scalar(stmt)
        return int(result or 0)

    async def list_paginated(
        self,
        *,
        offset: int,
        limit: int,
        camera_id: UUID | None = None,
    ) -> list[Detection]:
        stmt = (
            select(Detection)
            .order_by(Detection.detected_at.desc())
            .offset(offset)
            .limit(limit)
        )
        if camera_id is not None:
            stmt = stmt.where(Detection.camera_id == camera_id)
        result = await self._session.scalars(stmt)
        return list(result.all())
