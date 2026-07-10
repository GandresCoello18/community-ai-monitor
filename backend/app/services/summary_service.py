import logging
from collections import Counter
from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.exceptions import ValidationError
from app.llm.base import LLMProvider
from app.llm.factory import create_llm_provider
from app.llm.prompts import build_summary_prompt
from app.llm.schemas import EventSummaryItem, SummaryContext
from app.models import DailySummary, Event
from app.repositories.camera_repository import CameraRepository
from app.repositories.summary_repository import SummaryRepository
from app.schemas.camera import PaginatedResponse, PaginationMeta
from app.schemas.common import ApiResponse
from app.schemas.summary import SummaryResponse

logger = logging.getLogger(__name__)


class SummaryService:
    """Generates and lists AI summaries from structured events (FASE 7)."""

    def __init__(
        self,
        session: AsyncSession,
        settings: Settings,
        llm_provider: LLMProvider | None = None,
    ) -> None:
        self._session = session
        self._settings = settings
        self._repository = SummaryRepository(session)
        self._llm = llm_provider or create_llm_provider(settings)

    async def list_summaries(
        self,
        *,
        page: int,
        limit: int,
    ) -> PaginatedResponse[SummaryResponse]:
        safe_limit = min(limit, self._settings.max_page_size)
        offset = (page - 1) * safe_limit
        total = await self._repository.count_all()
        summaries = await self._repository.list_paginated(
            offset=offset,
            limit=safe_limit,
        )
        return PaginatedResponse(
            data=[SummaryResponse.model_validate(item) for item in summaries],
            meta=PaginationMeta(page=page, limit=safe_limit, total=total),
        )

    async def generate_summary(
        self,
        *,
        period_start: datetime | None = None,
        period_end: datetime | None = None,
    ) -> ApiResponse[SummaryResponse]:
        end = period_end or datetime.now(UTC)
        start = period_start or (end - timedelta(hours=24))
        if start >= end:
            raise ValidationError(
                "INVALID_PERIOD",
                "period_start must be earlier than period_end",
            )

        events = await self._repository.list_events_in_period(
            start=start,
            end=end,
            limit=self._settings.summary_max_events,
        )
        context = await self._build_context(start, end, events)
        prompt = build_summary_prompt(context)

        logger.info(
            "Generating summary events=%d provider=%s model=%s",
            context.total_events,
            self._llm.provider_name,
            self._llm.model_name,
        )
        summary_text = await self._llm.generate(prompt)

        summary = DailySummary(
            period_start=start,
            period_end=end,
            summary_text=summary_text,
            total_events=context.total_events,
            llm_provider=self._llm.provider_name,
            llm_model=self._llm.model_name,
            metadata_={
                "events_by_type": context.events_by_type,
                "events_by_severity": context.events_by_severity,
            },
        )
        self._repository.add(summary)
        await self._session.flush()

        return ApiResponse(data=SummaryResponse.model_validate(summary))

    async def _build_context(
        self,
        start: datetime,
        end: datetime,
        events: list[Event],
    ) -> SummaryContext:
        camera_repository = CameraRepository(self._session)
        cameras = await camera_repository.list_active(offset=0, limit=1000)
        camera_names = {camera.id: camera.name for camera in cameras}

        type_counts = Counter(event.event_type for event in events)
        severity_counts = Counter(event.severity for event in events)

        return SummaryContext(
            period_start=start,
            period_end=end,
            total_events=len(events),
            events_by_type=dict(type_counts),
            events_by_severity=dict(severity_counts),
            events=[
                EventSummaryItem(
                    event_type=event.event_type,
                    severity=event.severity,
                    occurred_at=event.occurred_at,
                    camera_name=camera_names.get(event.camera_id, "Cámara desconocida"),
                    metadata=event.metadata_,
                )
                for event in events
            ],
        )
