from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Event


@dataclass(frozen=True, slots=True)
class EventStatisticsResult:
    total: int
    by_type: dict[str, int]
    by_severity: dict[str, int]
    by_camera: dict[str, int]
    by_day: dict[str, int]


class EventRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def add(self, event: Event) -> None:
        self._session.add(event)

    def add_many(self, events: list[Event]) -> None:
        self._session.add_all(events)

    def _apply_filters(
        self,
        stmt: Select[tuple],
        *,
        camera_id: UUID | None = None,
        event_type: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> Select[tuple]:
        if camera_id is not None:
            stmt = stmt.where(Event.camera_id == camera_id)
        if event_type is not None:
            stmt = stmt.where(Event.event_type == event_type)
        if start_date is not None:
            stmt = stmt.where(Event.occurred_at >= start_date)
        if end_date is not None:
            stmt = stmt.where(Event.occurred_at <= end_date)
        return stmt

    async def count_all(
        self,
        *,
        camera_id: UUID | None = None,
        event_type: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> int:
        stmt = select(func.count()).select_from(Event)
        stmt = self._apply_filters(
            stmt,
            camera_id=camera_id,
            event_type=event_type,
            start_date=start_date,
            end_date=end_date,
        )
        result = await self._session.scalar(stmt)
        return int(result or 0)

    async def list_paginated(
        self,
        *,
        offset: int,
        limit: int,
        camera_id: UUID | None = None,
        event_type: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[Event]:
        stmt = (
            select(Event)
            .order_by(Event.occurred_at.desc())
            .offset(offset)
            .limit(limit)
        )
        stmt = self._apply_filters(
            stmt,
            camera_id=camera_id,
            event_type=event_type,
            start_date=start_date,
            end_date=end_date,
        )
        result = await self._session.scalars(stmt)
        return list(result.all())

    async def get_statistics(
        self,
        *,
        camera_id: UUID | None = None,
        event_type: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> EventStatisticsResult:
        filters = {
            "camera_id": camera_id,
            "event_type": event_type,
            "start_date": start_date,
            "end_date": end_date,
        }

        total = await self.count_all(**filters)
        by_type = await self._count_grouped("event_type", **filters)
        by_severity = await self._count_grouped("severity", **filters)
        by_camera = await self._count_grouped("camera_id", **filters)
        by_day = await self._count_by_day(**filters)

        return EventStatisticsResult(
            total=total,
            by_type=by_type,
            by_severity=by_severity,
            by_camera=by_camera,
            by_day=by_day,
        )

    async def _count_grouped(
        self,
        field_name: str,
        *,
        camera_id: UUID | None = None,
        event_type: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> dict[str, int]:
        column = getattr(Event, field_name)
        stmt = select(column, func.count()).select_from(Event).group_by(column)
        stmt = self._apply_filters(
            stmt,
            camera_id=camera_id,
            event_type=event_type,
            start_date=start_date,
            end_date=end_date,
        )
        rows = await self._session.execute(stmt)
        result: dict[str, int] = {}
        for key, count in rows.all():
            if key is None:
                continue
            result[str(key)] = int(count)
        return result

    async def _count_by_day(
        self,
        *,
        camera_id: UUID | None = None,
        event_type: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> dict[str, int]:
        day_column = func.date(Event.occurred_at)
        stmt = select(day_column, func.count()).select_from(Event).group_by(day_column)
        stmt = self._apply_filters(
            stmt,
            camera_id=camera_id,
            event_type=event_type,
            start_date=start_date,
            end_date=end_date,
        )
        rows = await self._session.execute(stmt)
        result: dict[str, int] = {}
        for day_value, count in rows.all():
            if day_value is None:
                continue
            result[str(day_value)] = int(count)
        return result
