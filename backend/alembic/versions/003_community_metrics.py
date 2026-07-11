"""Add community_metrics table for rule engine statistics.

Revision ID: 003_community_metrics
Revises: 002_daily_summaries
Create Date: 2026-07-11
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "003_community_metrics"
down_revision: Union[str, None] = "002_daily_summaries"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "community_metrics",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("camera_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("metric_type", sa.String(length=64), nullable=False),
        sa.Column("bucket_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["camera_id"], ["cameras.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "camera_id",
            "metric_type",
            "bucket_start",
            name="uq_community_metrics_camera_type_bucket",
        ),
    )
    op.create_index(
        "idx_community_metrics_camera_id",
        "community_metrics",
        ["camera_id"],
        unique=False,
    )
    op.create_index(
        "idx_community_metrics_metric_type",
        "community_metrics",
        ["metric_type"],
        unique=False,
    )
    op.create_index(
        "idx_community_metrics_bucket_start",
        "community_metrics",
        ["bucket_start"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("idx_community_metrics_bucket_start", table_name="community_metrics")
    op.drop_index("idx_community_metrics_metric_type", table_name="community_metrics")
    op.drop_index("idx_community_metrics_camera_id", table_name="community_metrics")
    op.drop_table("community_metrics")
