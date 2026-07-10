import uuid
from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

JSONType = JSON().with_variant(JSONB, "postgresql")


class Camera(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "cameras"

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    stream_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    detections: Mapped[list["Detection"]] = relationship(back_populates="camera")
    events: Mapped[list["Event"]] = relationship(back_populates="camera")


class Detection(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "detections"
    __table_args__ = (
        Index("idx_detections_camera_id", "camera_id"),
        Index("idx_detections_detected_at", "detected_at"),
    )

    camera_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cameras.id", ondelete="CASCADE"),
        nullable=False,
    )
    object_class: Mapped[str] = mapped_column(String(64), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    bbox: Mapped[dict] = mapped_column(JSONType, nullable=False)
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONType, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    camera: Mapped["Camera"] = relationship(back_populates="detections")


class Event(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "events"
    __table_args__ = (
        Index("idx_events_camera_id", "camera_id"),
        Index("idx_events_event_type", "event_type"),
        Index("idx_events_occurred_at", "occurred_at"),
        Index("idx_events_severity", "severity"),
    )

    camera_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cameras.id", ondelete="CASCADE"),
        nullable=False,
    )
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    severity: Mapped[str] = mapped_column(String(32), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONType, nullable=True)

    camera: Mapped["Camera"] = relationship(back_populates="events")


class Configuration(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "configurations"

    key: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    value: Mapped[dict] = mapped_column(JSONType, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)


class DailySummary(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "daily_summaries"
    __table_args__ = (
        Index("idx_daily_summaries_period_start", "period_start"),
    )

    period_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    period_end: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    summary_text: Mapped[str] = mapped_column(Text, nullable=False)
    total_events: Mapped[int] = mapped_column(nullable=False, default=0)
    llm_provider: Mapped[str] = mapped_column(String(64), nullable=False)
    llm_model: Mapped[str] = mapped_column(String(120), nullable=False)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONType, nullable=True)


__all__ = ["Camera", "Configuration", "DailySummary", "Detection", "Event"]
