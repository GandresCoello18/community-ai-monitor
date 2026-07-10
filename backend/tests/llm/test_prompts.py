from datetime import UTC, datetime

from app.llm.prompts import build_summary_prompt
from app.llm.schemas import EventSummaryItem, SummaryContext

BASE_TIME = datetime(2026, 7, 10, 15, 30, 0, tzinfo=UTC)


def _context() -> SummaryContext:
    return SummaryContext(
        period_start=BASE_TIME.replace(hour=0),
        period_end=BASE_TIME,
        total_events=2,
        events_by_type={"crowd_detected": 1, "long_presence": 1},
        events_by_severity={"low": 1, "medium": 1},
        events=[
            EventSummaryItem(
                event_type="crowd_detected",
                severity="low",
                occurred_at=BASE_TIME,
                camera_name="Camera Entrada",
                metadata={"people_count": 8},
            ),
            EventSummaryItem(
                event_type="long_presence",
                severity="medium",
                occurred_at=BASE_TIME,
                camera_name="Camera Parque",
                metadata={"duration_seconds": 1800},
            ),
        ],
    )


def test_prompt_includes_event_counts_and_cameras() -> None:
    prompt = build_summary_prompt(_context())

    assert "crowd_detected: 1" in prompt
    assert "long_presence: 1" in prompt
    assert "Camera Entrada" in prompt
    assert "Camera Parque" in prompt
    assert "Total de eventos: 2" in prompt


def test_prompt_includes_relevant_metadata_only() -> None:
    prompt = build_summary_prompt(_context())

    assert "people_count" in prompt
    assert "duration_seconds" in prompt
