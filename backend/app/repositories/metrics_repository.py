import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CommunityMetric


class MetricsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def upsert_many(self, metrics: list[CommunityMetric]) -> None:
        for metric in metrics:
            existing = await self._session.scalar(
                select(CommunityMetric).where(
                    CommunityMetric.camera_id == metric.camera_id,
                    CommunityMetric.metric_type == metric.metric_type,
                    CommunityMetric.bucket_start == metric.bucket_start,
                )
            )
            if existing is not None:
                existing.value = metric.value
                existing.metadata_ = metric.metadata_
                existing.updated_at = metric.updated_at
                continue
            self._session.add(metric)

    async def list_by_camera(
        self,
        camera_id: uuid.UUID,
        metric_type: str | None = None,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> list[CommunityMetric]:
        stmt = select(CommunityMetric).where(CommunityMetric.camera_id == camera_id)
        if metric_type is not None:
            stmt = stmt.where(CommunityMetric.metric_type == metric_type)
        if start is not None:
            stmt = stmt.where(CommunityMetric.bucket_start >= start)
        if end is not None:
            stmt = stmt.where(CommunityMetric.bucket_start <= end)
        stmt = stmt.order_by(CommunityMetric.bucket_start.asc())
        result = await self._session.scalars(stmt)
        return list(result.all())
