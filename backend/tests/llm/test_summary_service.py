from datetime import UTC, datetime, timedelta

import pytest

from app.core.config import Settings
from app.core.exceptions import ValidationError
from app.database.session import get_session_factory
from app.models import Camera, Event
from app.services.summary_service import SummaryService


class FakeLLMProvider:
    provider_name = "fake"
    model_name = "fake-model"

    def __init__(self) -> None:
        self.prompts: list[str] = []

    async def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return "Resumen de prueba: actividad normal durante el período."

    async def is_available(self) -> bool:
        return True


BASE_TIME = datetime(2026, 7, 10, 12, 0, 0, tzinfo=UTC)


async def _seed_events(settings: Settings) -> None:
    session_factory = get_session_factory(settings)
    async with session_factory() as session:
        camera = Camera(
            name="Camera Test",
            location="Test",
            stream_url="rtsp://demo/test",
            is_active=True,
        )
        session.add(camera)
        await session.flush()
        session.add(
            Event(
                camera_id=camera.id,
                event_type="crowd_detected",
                severity="low",
                occurred_at=BASE_TIME - timedelta(hours=1),
                metadata_={"people_count": 6},
            )
        )
        await session.commit()


@pytest.mark.asyncio
async def test_generate_summary_persists_and_returns_text(
    test_settings: Settings,
    app,
) -> None:
    await _seed_events(test_settings)
    provider = FakeLLMProvider()

    session_factory = get_session_factory(test_settings)
    async with session_factory() as session:
        service = SummaryService(session, test_settings, llm_provider=provider)
        response = await service.generate_summary(
            period_start=BASE_TIME - timedelta(hours=24),
            period_end=BASE_TIME,
        )
        await session.commit()

    assert response.data.total_events == 1
    assert response.data.summary_text.startswith("Resumen de prueba")
    assert response.data.llm_provider == "fake"
    assert len(provider.prompts) == 1
    assert "crowd_detected" in provider.prompts[0]


@pytest.mark.asyncio
async def test_generate_summary_rejects_invalid_period(
    test_settings: Settings,
    app,
) -> None:
    provider = FakeLLMProvider()
    session_factory = get_session_factory(test_settings)
    async with session_factory() as session:
        service = SummaryService(session, test_settings, llm_provider=provider)
        with pytest.raises(ValidationError):
            await service.generate_summary(
                period_start=BASE_TIME,
                period_end=BASE_TIME - timedelta(hours=1),
            )


@pytest.mark.asyncio
async def test_list_summaries_paginated(
    test_settings: Settings,
    app,
) -> None:
    await _seed_events(test_settings)
    provider = FakeLLMProvider()
    session_factory = get_session_factory(test_settings)

    async with session_factory() as session:
        service = SummaryService(session, test_settings, llm_provider=provider)
        await service.generate_summary(
            period_start=BASE_TIME - timedelta(hours=24),
            period_end=BASE_TIME,
        )
        await session.commit()

    async with session_factory() as session:
        service = SummaryService(session, test_settings, llm_provider=provider)
        result = await service.list_summaries(page=1, limit=10)

    assert result.meta.total == 1
    assert len(result.data) == 1
    assert result.data[0].llm_model == "fake-model"
