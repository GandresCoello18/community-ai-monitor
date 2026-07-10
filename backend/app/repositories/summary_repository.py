from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import DailySummary, Event


class SummaryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def add(self, summary: DailySummary) -> None:
        self._session.add(summary)

    async def count_all(self) -> int:
        stmt = select(func.count()).select_from(DailySummary)
        result = await self._session.scalar(stmt)
        return int(result or 0)

    async def list_paginated(
        self,
        *,
        offset: int,
        limit: int,
    ) -> list[DailySummary]:
        stmt = (
            select(DailySummary)
            .order_by(DailySummary.period_start.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self._session.scalars(stmt)
        return list(result.all())

    async def list_events_in_period(
        self,
        *,
        start: datetime,
        end: datetime,
        limit: int = 200,
    ) -> list[Event]:
        stmt = (
            select(Event)
            .where(Event.occurred_at >= start, Event.occurred_at < end)
            .order_by(Event.occurred_at.asc())
            .limit(limit)
        )
        result = await self._session.scalars(stmt)
        return list(result.all())
